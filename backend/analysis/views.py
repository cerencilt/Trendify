from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from .models import Analysis
from .serializers import AnalysisCreateSerializer, AnalysisSerializer
from .services import run_analysis


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def create_analysis(request):
    """Yeni analiz oluştur ve çalıştır"""
    serializer = AnalysisCreateSerializer(data=request.data)

    if serializer.is_valid():
        analysis = serializer.save(user=request.user)

        # Analizi çalıştır
        try:
            run_analysis(analysis.id)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Güncel halini döndür
        result_serializer = AnalysisSerializer(analysis)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_analyses(request):
    """Kullanıcının tüm analizlerini listele"""
    analyses = Analysis.objects.filter(user=request.user)
    serializer = AnalysisSerializer(analyses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analysis_detail(request, pk):
    """Tek analiz detayı"""
    try:
        analysis = Analysis.objects.get(id=pk, user=request.user)
    except Analysis.DoesNotExist:
        return Response(
            {'error': 'Analiz bulunamadı.'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = AnalysisSerializer(analysis)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analysis_result(request, pk):
    """Analiz sonucunu getir"""
    try:
        analysis = Analysis.objects.get(id=pk, user=request.user)
    except Analysis.DoesNotExist:
        return Response(
            {'error': 'Analiz bulunamadı.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not hasattr(analysis, 'result'):
        return Response(
            {'error': 'Analiz sonucu henüz hazır değil.'},
            status=status.HTTP_404_NOT_FOUND
        )

    from .serializers import AnalysisResultSerializer
    serializer = AnalysisResultSerializer(analysis.result)
    return Response(serializer.data)


from django.shortcuts import render

# Create your views here.
