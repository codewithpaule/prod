from django import forms

from .choices import CATEGORIES, choices_for
from .models import Student

_LABELS = {
    "student_ref": "Student reference ID",
    "age_range": "Age range",
    "level": "Academic level",
    "study_hours": "Study hours per day",
    "attendance": "Lecture attendance",
    "courses_failed": "Courses failed / carried over",
    "sleep_hours": "Sleep hours per night",
    "financial_stress": "Financial stress level",
    "mother_education": "Mother's education level",
    "father_education": "Father's education level",
    "family_income": "Family income band",
    "part_time_work": "Part-time work",
    "motivation": "Academic motivation",
    "stress_level": "Stress level",
    "self_rated_perf": "Self-rated performance",
}


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["student_ref", *CATEGORIES.keys()]
        labels = _LABELS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student_ref"].widget = forms.TextInput(
            attrs={"class": "input", "placeholder": "e.g. STU-2024-001"}
        )
        for field in CATEGORIES:
            self.fields[field] = forms.ChoiceField(
                choices=[("", "Select...")] + choices_for(field),
                label=_LABELS.get(field, field.replace("_", " ").title()),
                widget=forms.Select(attrs={"class": "input"}),
            )

    def clean_student_ref(self) -> str:
        ref = self.cleaned_data["student_ref"].strip()
        if not ref:
            raise forms.ValidationError("Student reference is required.")
        return ref


class UploadForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV file",
        widget=forms.ClearableFileInput(attrs={"class": "input", "accept": ".csv"}),
    )

    def clean_csv_file(self):
        f = self.cleaned_data["csv_file"]
        if not f.name.lower().endswith(".csv"):
            raise forms.ValidationError("Please upload a .csv file.")
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File too large (max 5 MB).")
        return f
