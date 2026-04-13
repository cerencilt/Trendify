from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.get_recommendation, name='get_recommendation'),
]
