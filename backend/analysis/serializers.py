from rest_framework import serializers
from .models import Analysis, AnalysisResult, SocialMediaPost


class AnalysisCreateSerializer(serializers.ModelSerializer):
    """Analiz oluştururken kullanılır"""

    class Meta:
        model = Analysis
        fields = [
            'id', 'input_type', 'topic', 'platform',
            'goal', 'language', 'description', 'csv_file'
        ]

    def validate(self, data):
        input_type = data.get('input_type')

        # İçerik bazlıysa topic zorunlu
        if input_type == 'content_based' and not data.get('topic'):
            raise serializers.ValidationError(
                {'topic': 'İçerik bazlı analizde konu zorunludur.'}
            )

        # Performans bazlıysa csv zorunlu
        if input_type == 'performance_based' and not data.get('csv_file'):
            raise serializers.ValidationError(
                {'csv_file': 'Performans bazlı analizde CSV dosyası zorunludur.'}
            )

        return data


class AnalysisResultSerializer(serializers.ModelSerializer):
    """Analiz sonuçlarını döner"""

    class Meta:
        model = AnalysisResult
        fields = [
            'id', 'best_post_time', 'best_day',
            'avg_engagement_rate', 'avg_likes',
            'avg_comments', 'avg_shares',
            'trend_fit_score', 'heatmap_data',
            'content_type_performance', 'created_at'
        ]


class AnalysisSerializer(serializers.ModelSerializer):
    """Analiz listesi ve detayı için"""

    result = AnalysisResultSerializer(read_only=True)

    class Meta:
        model = Analysis
        fields = [
            'id', 'input_type', 'topic', 'platform',
            'goal', 'language', 'description',
            'csv_file', 'status', 'error_message',
            'created_at', 'updated_at', 'result'
        ]
        read_only_fields = ['status', 'error_message', 'created_at', 'updated_at']