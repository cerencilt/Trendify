from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Avg

from analysis.models import Analysis, AnalysisResult
from analysis.serializers import AnalysisSerializer
from recommendations.models import Recommendation, Feedback


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary(request):
    """Kullanıcının dashboard özeti"""
    user = request.user

    # Toplam sayılar
    total_analyses = Analysis.objects.filter(user=user).count()
    total_recommendations = Recommendation.objects.filter(user=user).count()
    total_feedbacks = Feedback.objects.filter(user=user).count()

    # Tamamlanan analiz sayısı
    completed_analyses = Analysis.objects.filter(
        user=user, status='completed'
    ).count()

    # En son analiz
    latest_analysis = Analysis.objects.filter(user=user).first()
    latest_data = None
    if latest_analysis:
        latest_data = AnalysisSerializer(latest_analysis).data

    # Platform dağılımı
    platform_distribution = list(
        Analysis.objects.filter(user=user)
        .exclude(platform__isnull=True)
        .values('platform')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Ortalama feedback puanı
    avg_rating = Feedback.objects.filter(user=user).aggregate(
        avg=Avg('rating')
    )['avg']

    return Response({
        'total_analyses': total_analyses,
        'completed_analyses': completed_analyses,
        'total_recommendations': total_recommendations,
        'total_feedbacks': total_feedbacks,
        'avg_rating': round(avg_rating, 2) if avg_rating else None,
        'platform_distribution': platform_distribution,
        'latest_analysis': latest_data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history(request):
    """Kullanıcının geçmiş analizleri (filtreleme ile)"""
    user = request.user
    queryset = Analysis.objects.filter(user=user)

    # Filtreler
    platform = request.query_params.get('platform')
    if platform:
        queryset = queryset.filter(platform=platform)

    input_type = request.query_params.get('input_type')
    if input_type:
        queryset = queryset.filter(input_type=input_type)

    status_filter = request.query_params.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # Sıralama
    ordering = request.query_params.get('ordering', '-created_at')
    queryset = queryset.order_by(ordering)

    serializer = AnalysisSerializer(queryset, many=True)
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })