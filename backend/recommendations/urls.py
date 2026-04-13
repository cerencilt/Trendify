from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_recommendations, name='recommendation-list'),
    path('generate/', views.generate, name='recommendation-generate'),
    path('<int:pk>/', views.recommendation_detail, name='recommendation-detail'),
    path('<int:pk>/feedback/', views.add_feedback, name='recommendation-feedback'),
]