"""Page views for the AcadPredict web layer."""
from __future__ import annotations

import csv
import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from . import ml_client
from .choices import CATEGORIES
from .csv_utils import CSV_COLUMNS, build_sample_csv, parse_upload, parse_google_form_file
from .forms import StudentForm, UploadForm, TrainUploadForm
from .models import Prediction, Student
from .services import save_prediction


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next') or 'dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    predictions = Prediction.objects.all()
    total = predictions.count()

    distribution = {
        'First Class (4.5-5.0)': 0,
        'Second Class Upper (3.5-4.4)': 0,
        'Second Class Lower (2.5-3.4)': 0,
        'Third Class (1.5-2.4)': 0,
        'Below Third Class (<1.5)': 0,
    }
    for row in predictions.values('predicted_class').annotate(n=Count('id')):
        key = row['predicted_class']
        if key in distribution:
            distribution[key] = row['n']

    since = timezone.now() - timedelta(days=30)
    per_day_qs = (
        predictions.filter(created_at__gte=since)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(n=Count('id'))
        .order_by('day')
    )
    per_day = [
        {'day': row['day'].isoformat(), 'count': row['n']}
        for row in per_day_qs
        if row['day'] is not None
    ]

    try:
        importance = ml_client.feature_importance()
    except ml_client.MLServiceError:
        importance = []

    at_risk_count = distribution.get('Third Class (1.5-2.4)', 0) + distribution.get('Below Third Class (<1.5)', 0)
    high_count = distribution.get('First Class (4.5-5.0)', 0) + distribution.get('Second Class Upper (3.5-4.4)', 0)

    context = {
        'active': 'dashboard',
        'total': total,
        'high_count': high_count,
        'average_count': distribution.get('Second Class Lower (2.5-3.4)', 0),
        'risk_count': at_risk_count,
        'distribution_json': json.dumps(distribution),
        'per_day_json': json.dumps(per_day),
        'feature_importance_json': json.dumps(importance[:10]),
        'recent': predictions.select_related('student')[:5],
    }
    return render(request, 'dashboard.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def predict_view(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            payload = {'student_ref': form.cleaned_data['student_ref']}
            payload.update({f: form.cleaned_data[f] for f in CATEGORIES})
            try:
                result = ml_client.predict(payload)
            except ml_client.MLServiceError as exc:
                messages.error(request, f'Prediction failed: {exc}')
            else:
                student = save_prediction(payload, result)
                return redirect('results', student_id=student.id)
    else:
        form = StudentForm()
    return render(request, 'predict.html', {'form': form, 'active': 'predict'})


@login_required
def results_view(request, student_id: int):
    student = get_object_or_404(Student, id=student_id)
    prediction = get_object_or_404(Prediction, student=student)
    top_scores = (prediction.feature_scores or [])[:5]
    context = {
        'student': student,
        'prediction': prediction,
        'top_scores': top_scores,
        'top_scores_json': json.dumps(top_scores),
        'active': 'students',
    }
    return render(request, 'results.html', context)


@login_required
def students_view(request):
    qs = Prediction.objects.select_related('student').all()
    risk = request.GET.get('risk')
    valid_classes = {
        'First Class (4.5-5.0)', 'Second Class Upper (3.5-4.4)',
        'Second Class Lower (2.5-3.4)', 'Third Class (1.5-2.4)',
        'Below Third Class (<1.5)',
    }
    if risk in valid_classes:
        qs = qs.filter(predicted_class=risk)
    paginator = Paginator(qs, 15)
    page = paginator.get_page(request.GET.get('page'))
    return render(
        request,
        'students.html',
        {'page_obj': page, 'risk': risk, 'total': paginator.count, 'active': 'students'},
    )


@login_required
@require_http_methods(['GET', 'POST'])
def upload_view(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            valid_rows, errors = parse_upload(form.cleaned_data['csv_file'])
            for err in errors:
                messages.warning(request, err)
            if valid_rows:
                try:
                    results = ml_client.predict_bulk(valid_rows)
                except ml_client.MLServiceError as exc:
                    messages.error(request, f'Bulk prediction failed: {exc}')
                else:
                    for payload, result in zip(valid_rows, results):
                        save_prediction(payload, result)
                    messages.success(
                        request,
                        f'Processed {len(results)} student record(s) successfully.',
                    )
                    return redirect('students')
            elif not errors:
                messages.error(request, 'No valid rows found in the uploaded file.')
    else:
        form = UploadForm()
    return render(request, 'upload.html', {'form': form, 'columns': CSV_COLUMNS, 'active': 'upload'})


@login_required
def sample_csv(request):
    response = HttpResponse(build_sample_csv(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=acadpredict_sample.csv'
    return response


@login_required
def export_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=acadpredict_results.csv'
    writer = csv.writer(response)
    writer.writerow(
        ['student_ref', *CATEGORIES.keys(), 'predicted_class', 'estimated_cgpa_midpoint', 'confidence', 'created_at']
    )
    for pred in Prediction.objects.select_related('student').all():
        s = pred.student
        writer.writerow(
            [s.student_ref]
            + [getattr(s, f, '') for f in CATEGORIES]
            + [pred.predicted_class, f'{pred.estimated_cgpa_midpoint:.2f}', f'{pred.confidence:.4f}', pred.created_at.isoformat()]
        )
    return response


@login_required
@require_http_methods(['GET', 'POST'])
def train_model_view(request):
    """Upload Google Form data to retrain the prediction model."""
    if request.method == 'POST':
        form = TrainUploadForm(request.POST, request.FILES)
        if form.is_valid():
            data_file = form.cleaned_data['data_file']
            use_synthetic = form.cleaned_data.get('use_synthetic', True)
            synthetic_n = form.cleaned_data.get('synthetic_n') or 3000

            training_rows, parse_errors, total_raw = parse_google_form_file(data_file)

            for err in parse_errors[:10]:
                messages.warning(request, err)
            if len(parse_errors) > 10:
                messages.warning(request, f'…and {len(parse_errors) - 10} more warnings.')

            if not training_rows:
                messages.error(
                    request,
                    f'No valid training rows extracted from {total_raw} raw rows. '
                    'Please check the file format and column headers match the survey questions.'
                )
            else:
                try:
                    result = ml_client.retrain_model(
                        rows=training_rows,
                        use_synthetic=use_synthetic,
                        synthetic_n=synthetic_n,
                    )
                    acc = result.get('accuracy')
                    acc_str = f', accuracy: {acc:.1%}' if acc is not None else ''
                    messages.success(
                        request,
                        f"Model retrained successfully! Used {len(training_rows)} real rows "
                        f"from {total_raw} uploaded rows{acc_str}."
                    )
                    return redirect('dashboard')
                except ml_client.MLServiceError as exc:
                    messages.error(request, f'Model training failed: {exc}')
    else:
        form = TrainUploadForm()

    return render(request, 'train.html', {'form': form, 'active': 'train'})


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)
