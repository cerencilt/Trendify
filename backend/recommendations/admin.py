from django.contrib import admin
from .models import Recommendation, Feedback


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'topic',
                    'post_time', 'best_day', 'created_at']
    list_filter = ['platform']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'recommendation', 'rating', 'created_at']
    list_filter = ['rating']