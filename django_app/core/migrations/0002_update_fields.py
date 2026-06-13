from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(model_name='student', name='financial_stress'),
        migrations.AlterField(
            model_name='student',
            name='student_ref',
            field=models.CharField(max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='gender',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='study_hours',
            field=models.CharField(max_length=40, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='attendance',
            field=models.CharField(max_length=40, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='courses_failed',
            field=models.CharField(max_length=20, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='sleep_hours',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='mother_education',
            field=models.CharField(max_length=50, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='father_education',
            field=models.CharField(max_length=50, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='family_income',
            field=models.CharField(max_length=50, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='part_time_work',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='motivation',
            field=models.CharField(max_length=20, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='stress_level',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='self_rated_perf',
            field=models.CharField(max_length=20, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='current_cgpa',
            field=models.CharField(max_length=50, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='household_size',
            field=models.CharField(max_length=20, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='parental_involvement',
            field=models.CharField(max_length=40, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='class_prep',
            field=models.CharField(max_length=20, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='resource_use',
            field=models.CharField(max_length=20, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='group_study',
            field=models.CharField(max_length=20, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='past_questions',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='distance',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='internet_access',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='extracurricular',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='family_responsibilities',
            field=models.CharField(max_length=20, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='student',
            name='course_interest',
            field=models.CharField(max_length=50, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='prediction',
            name='predicted_class',
            field=models.CharField(max_length=60),
        ),
        migrations.AddField(
            model_name='prediction',
            name='estimated_cgpa_range',
            field=models.CharField(max_length=60, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='prediction',
            name='estimated_cgpa_midpoint',
            field=models.FloatField(default=2.95),
        ),
        migrations.AlterField(
            model_name='prediction',
            name='model_version',
            field=models.CharField(max_length=20, default='v2.0'),
        ),
    ]
