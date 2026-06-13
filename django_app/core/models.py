from django.db import models
from django.utils import timezone


class Student(models.Model):
    student_ref = models.CharField(max_length=30, unique=True)
    gender = models.CharField(max_length=30, blank=True, default='')
    age_range = models.CharField(max_length=20, blank=True, default='')
    level = models.CharField(max_length=20, blank=True, default='')
    current_cgpa = models.CharField(max_length=50, blank=True, default='')
    courses_failed = models.CharField(max_length=20, blank=True, default='')
    father_education = models.CharField(max_length=50, blank=True, default='')
    mother_education = models.CharField(max_length=50, blank=True, default='')
    family_income = models.CharField(max_length=50, blank=True, default='')
    household_size = models.CharField(max_length=20, blank=True, default='')
    parental_involvement = models.CharField(max_length=40, blank=True, default='')
    study_hours = models.CharField(max_length=40, blank=True, default='')
    attendance = models.CharField(max_length=40, blank=True, default='')
    class_prep = models.CharField(max_length=20, blank=True, default='')
    resource_use = models.CharField(max_length=20, blank=True, default='')
    sleep_hours = models.CharField(max_length=30, blank=True, default='')
    group_study = models.CharField(max_length=20, blank=True, default='')
    past_questions = models.CharField(max_length=30, blank=True, default='')
    part_time_work = models.CharField(max_length=30, blank=True, default='')
    distance = models.CharField(max_length=30, blank=True, default='')
    internet_access = models.CharField(max_length=30, blank=True, default='')
    extracurricular = models.CharField(max_length=30, blank=True, default='')
    family_responsibilities = models.CharField(max_length=20, blank=True, default='')
    stress_level = models.CharField(max_length=30, blank=True, default='')
    course_interest = models.CharField(max_length=50, blank=True, default='')
    motivation = models.CharField(max_length=20, blank=True, default='')
    self_rated_perf = models.CharField(max_length=20, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.student_ref

    def feature_payload(self) -> dict[str, str]:
        from .choices import CATEGORIES
        payload = {field: getattr(self, field) for field in CATEGORIES}
        payload['student_ref'] = self.student_ref
        return payload


class Prediction(models.Model):
    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name='prediction'
    )
    predicted_class = models.CharField(max_length=60)
    estimated_cgpa_range = models.CharField(max_length=60, blank=True, default='')
    estimated_cgpa_midpoint = models.FloatField(default=2.95)
    confidence = models.FloatField()
    recommendation = models.TextField()
    feature_scores = models.JSONField(default=list, blank=True)
    model_version = models.CharField(max_length=20, default='v2.0')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.student.student_ref} -> {self.predicted_class}'

    @property
    def confidence_pct(self) -> int:
        return round(self.confidence * 100)

    @property
    def badge_class(self) -> str:
        pc = self.predicted_class
        if 'First Class' in pc:
            return 'badge-first'
        if 'Second Class Upper' in pc:
            return 'badge-high'
        if 'Second Class Lower' in pc:
            return 'badge-average'
        if 'Third Class' in pc:
            return 'badge-third'
        return 'badge-risk'


class AdvisorNote(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='notes'
    )
    author = models.CharField(max_length=120, blank=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Note for {self.student.student_ref}'


class TrainingBatch(models.Model):
    """Records each batch of real training data uploaded to the system.

    Rows are stored as a JSON list so they can be accumulated and replayed
    every time the model is retrained (incremental / continual learning).
    """
    name = models.CharField(max_length=120, blank=True, default='')
    uploaded_by = models.CharField(max_length=120, blank=True, default='')
    row_count = models.IntegerField(default=0)
    rows = models.JSONField(default=list)
    accuracy_after = models.FloatField(null=True, blank=True)
    bias_report = models.JSONField(default=dict, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self) -> str:
        return f'Batch {self.pk}: {self.row_count} rows ({self.uploaded_at:%Y-%m-%d})'
