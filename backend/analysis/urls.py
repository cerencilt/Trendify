from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_analyses, name='analysis-list'),
    path('start/', views.create_analysis, name='analysis-create'),
    path('<int:pk>/', views.analysis_detail, name='analysis-detail'),
    path('<int:pk>/result/', views.analysis_result, name='analysis-result'),
]