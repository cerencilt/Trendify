from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Recommendation
from .serializers import (
    RecommendationSerializer,
    RecommendationGenerateSerializer,
    FeedbackSerializer
)
from .services import generate_recommendation


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate(request):
    """Analiz sonucundan öneri üret"""
    serializer = RecommendationGenerateSerializer(data=request.data)

    if serializer.is_valid():
        try:
            recommendation = generate_recommendation(
                user=request.user,
                analysis_id=serializer.validated_data['analysis_id'],
                platform=serializer.validated_data.get('platform'),
                topic=serializer.validated_data.get('topic')
            )
            return Response(
                RecommendationSerializer(recommendation).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Beklenmeyen hata: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_recommendations(request):
    """Kullanıcının tüm önerilerini listele"""
    recommendations = Recommendation.objects.filter(user=request.user)
    serializer = RecommendationSerializer(recommendations, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendation_detail(request, pk):
    """Tek öneri detayı"""
    try:
        recommendation = Recommendation.objects.get(
            id=pk, user=request.user
        )
    except Recommendation.DoesNotExist:
        return Response(
            {'error': 'Öneri bulunamadı.'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = RecommendationSerializer(recommendation)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_feedback(request, pk):
    """Öneriye geri bildirim ekle"""
    try:
        recommendation = Recommendation.objects.get(
            id=pk, user=request.user
        )
    except Recommendation.DoesNotExist:
        return Response(
            {'error': 'Öneri bulunamadı.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if hasattr(recommendation, 'feedback'):
        return Response(
            {'error': 'Bu öneriye zaten geri bildirim verilmiş.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = FeedbackSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(
            user=request.user,
            recommendation=recommendation
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)