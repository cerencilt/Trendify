from rest_framework import serializers
from .models import Recommendation, Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']


class RecommendationSerializer(serializers.ModelSerializer):
    feedback = FeedbackSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            'id', 'analysis', 'platform', 'topic',
            'post_time', 'best_day', 'hashtags',
            'caption', 'music', 'reasoning',
            'created_at', 'updated_at', 'feedback'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RecommendationGenerateSerializer(serializers.Serializer):
    analysis_id = serializers.IntegerField()
    platform = serializers.CharField(max_length=20, required=False)
    topic = serializers.CharField(max_length=255, required=False)