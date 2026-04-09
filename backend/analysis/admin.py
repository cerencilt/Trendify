from django.contrib import admin
from .models import SocialMediaPost, Analysis, AnalysisResult


@admin.register(SocialMediaPost)
class SocialMediaPostAdmin(admin.ModelAdmin):
    list_display = ['platform', 'date', 'post_time', 'content_type',
                    'engagement_level', 'likes', 'source']
    list_filter = ['platform', 'content_type', 'engagement_level', 'source']
    search_fields = ['hashtags', 'platform']


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'input_type', 'platform', 'status', 'created_at']
    list_filter = ['status', 'input_type', 'platform']


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['analysis', 'best_post_time', 'best_day',
                    'avg_engagement_rate', 'trend_fit_score']