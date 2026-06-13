from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('predict/', views.predict_view, name='predict'),
    path('results/<int:student_id>/', views.results_view, name='results'),
    path('students/', views.students_view, name='students'),
    path('upload/', views.upload_view, name='upload'),
    path('upload/sample.csv', views.sample_csv, name='sample_csv'),
    path('export/', views.export_view, name='export'),
    path('train/', views.train_model_view, name='train_model'),
]
