from django.contrib import admin

from .models import AdvisorNote, Prediction, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_ref", "level", "gender", "created_at")
    search_fields = ("student_ref",)
    list_filter = ("level", "gender")


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("student", "predicted_class", "confidence", "model_version", "created_at")
    list_filter = ("predicted_class", "model_version")
    search_fields = ("student__student_ref",)


@admin.register(AdvisorNote)
class AdvisorNoteAdmin(admin.ModelAdmin):
    list_display = ("student", "author", "created_at")
    search_fields = ("student__student_ref", "author")
