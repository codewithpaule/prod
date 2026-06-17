from django import forms

from .choices import CATEGORIES, choices_for
from .models import Student

_LABELS = {
    'student_ref': 'Student reference ID',
    'gender': 'Q1. Gender',
    'age_range': 'Q2. Age range',
    'level': 'Q3. Current level of study',
    'current_cgpa': 'Q4. Current CGPA range',
    'courses_failed': 'Q5. Courses failed / carried over',
    'father_education': "Q6. Father's highest education",
    'mother_education': "Q7. Mother's highest education",
    'family_income': 'Q8. Family monthly income level',
    'household_size': 'Q9. Household size (financially dependent)',
    'parental_involvement': 'Q10. Parental involvement in academics',
    'study_hours': 'Q11. Study hours per day (outside class)',
    'attendance': 'Q12. Lecture attendance frequency',
    'class_prep': 'Q13. Read ahead / prepare before class',
    'resource_use': 'Q14. Use of academic resources',
    'sleep_hours': 'Q15. Sleep hours per night',
    'group_study': 'Q16. Group study / academic discussions',
    'past_questions': 'Q17. Practice past exam questions',
    'part_time_work': 'Q18. Part-time work / business while schooling',
    'distance': 'Q19. Distance from campus',
    'internet_access': 'Q20. Internet access stability',
    'extracurricular': 'Q21. Extracurricular activities',
    'family_responsibilities': 'Q22. Family responsibilities impact on study',
    'stress_level': 'Q23. Mental health / stress level',
    'course_interest': 'Q24. Studying course out of personal interest?',
    'motivation': 'Q25. Overall motivation to succeed academically',
    'self_rated_perf': 'Q26. Self-rated academic performance',
}


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_ref', *CATEGORIES.keys()]
        labels = _LABELS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_ref'].widget = forms.TextInput(
            attrs={'class': 'input', 'placeholder': 'e.g. STU-2024-001'}
        )
        for field in CATEGORIES:
            self.fields[field] = forms.ChoiceField(
                choices=[('', 'Select…')] + choices_for(field),
                label=_LABELS.get(field, field.replace('_', ' ').title()),
                widget=forms.Select(attrs={'class': 'input'}),
            )

    def clean_student_ref(self) -> str:
        ref = self.cleaned_data['student_ref'].strip()
        if not ref:
            raise forms.ValidationError('Student reference is required.')
        return ref


class UploadForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV file',
        widget=forms.ClearableFileInput(
            attrs={'class': 'input', 'accept': '.csv'}
        ),
    )

    def clean_csv_file(self):
        f = self.cleaned_data['csv_file']
        if not f.name.lower().endswith('.csv'):
            raise forms.ValidationError('Please upload a .csv file.')
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File too large (max 5 MB).')
        return f


class TrainUploadForm(forms.Form):
    data_file = forms.FileField(
        label='Google Form export (Excel .xlsx or .csv)',
        widget=forms.ClearableFileInput(
            attrs={'class': 'input', 'accept': '.csv,.xlsx,.xls'}
        ),
    )
    use_synthetic = forms.BooleanField(
        required=False,
        initial=False,
        label='Blend with synthetic data (optional — only if you have very few responses)',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'}),
    )
    synthetic_n = forms.IntegerField(
        required=False,
        initial=3000,
        min_value=100,
        max_value=10000,
        label='Number of synthetic rows to blend',
        widget=forms.NumberInput(attrs={'class': 'input'}),
    )

    def clean_data_file(self):
        f = self.cleaned_data['data_file']
        name = f.name.lower()
        if not (name.endswith('.csv') or name.endswith('.xlsx') or name.endswith('.xls')):
            raise forms.ValidationError('Please upload a .csv or .xlsx file.')
        if f.size > 20 * 1024 * 1024:
            raise forms.ValidationError('File too large (max 20 MB).')
        return f
