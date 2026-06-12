from django.db import models


class Student(models.Model):
    student_ref = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=20)
    age_range = models.CharField(max_length=20)
    level = models.CharField(max_length=20)
    study_hours = models.CharField(max_length=30)
    attendance = models.CharField(max_length=30)
    courses_failed = models.CharField(max_length=20)
    sleep_hours = models.CharField(max_length=20)
    financial_stress = models.CharField(max_length=30)
    mother_education = models.CharField(max_length=40)
    father_education = models.CharField(max_length=40)
    family_income = models.CharField(max_length=30)
    part_time_work = models.CharField(max_length=30)
    motivation = models.CharField(max_length=30)
    stress_level = models.CharField(max_length=30)
    self_rated_perf = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.student_ref

    def feature_payload(self) -> dict[str, str]:
        from .choices import CATEGORIES

        payload = {field: getattr(self, field) for field in CATEGORIES}
        payload["student_ref"] = self.student_ref
        return payload


class Prediction(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="prediction")
    predicted_class = models.CharField(max_length=20)  # High / Average / At-Risk
    confidence = models.FloatField()
    recommendation = models.TextField()  # Groq AI output
    feature_scores = models.JSONField(default=list, blank=True)
    model_version = models.CharField(max_length=20, default="v1.0")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.student.student_ref} -> {self.predicted_class}"

    @property
    def confidence_pct(self) -> int:
        return round(self.confidence * 100)

    @property
    def badge_class(self) -> str:
        return {
            "High": "badge-high",
            "Average": "badge-average",
            "At-Risk": "badge-risk",
        }.get(self.predicted_class, "badge-average")


class AdvisorNote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="notes")
    author = models.CharField(max_length=120, blank=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Note for {self.student.student_ref}"
