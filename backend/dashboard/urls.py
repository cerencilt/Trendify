from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.summary, name='dashboard-summary'),
    path('history/', views.history, name='dashboard-history'),
]