import requests
from analysis.models import Analysis
from .models import Recommendation

DAY_NAMES = {
    0: 'Pazartesi', 1: 'Salı', 2: 'Çarşamba',
    3: 'Perşembe', 4: 'Cuma', 5: 'Cumartesi', 6: 'Pazar'
}

# Trendify AI endpoint URL
TRENDIFY_AI_URL = "http://127.0.0.1:8000/api/ai/recommend/"


def generate_recommendation(user, analysis_id, platform=None, topic=None):
    try:
        analysis = Analysis.objects.get(id=analysis_id, user=user)
    except Analysis.DoesNotExist:
        raise ValueError('Analiz bulunamadı.')

    if analysis.status != 'completed':
        raise ValueError('Analiz henüz tamamlanmadı.')

    if not hasattr(analysis, 'result'):
        raise ValueError('Analiz sonucu bulunamadı.')

    result = analysis.result
    platform = platform or analysis.platform or 'Instagram'
    topic = topic or analysis.topic or ''
    best_day_name = DAY_NAMES.get(result.best_day, 'Bilinmiyor')

    best_content_type = None
    if result.content_type_performance:
        best_content_type = max(
            result.content_type_performance,
            key=result.content_type_performance.get
        )

    context = _build_context(result, best_day_name, best_content_type)
    ai_response = _call_trendify_ai(topic, platform, context)

    recommendation = Recommendation.objects.create(
        user=user,
        analysis=analysis,
        platform=platform,
        topic=topic,
        post_time=result.best_post_time,
        best_day=best_day_name,
        hashtags='',
        caption='',
        music='',
        reasoning=ai_response
    )

    return recommendation


def _build_context(result, best_day_name, best_content_type):
    context_parts = []

    if result.best_post_time is not None:
        context_parts.append(
            f"En iyi paylaşım saati: {result.best_post_time}:00"
        )
    if best_day_name:
        context_parts.append(
            f"En iyi paylaşım günü: {best_day_name}"
        )
    if result.avg_engagement_rate:
        context_parts.append(
            f"Ortalama etkileşim oranı: %{result.avg_engagement_rate:.1f}"
        )
    if result.avg_likes:
        context_parts.append(
            f"Ortalama beğeni: {int(result.avg_likes)}"
        )
    if best_content_type:
        context_parts.append(
            f"En iyi içerik türü: {best_content_type}"
        )
    if result.trend_fit_score:
        context_parts.append(
            f"Trend uyum skoru: {result.trend_fit_score}/100"
        )

    return '\n'.join(context_parts)
# Topic'i Türkçeleştir (model Türkçe ile eğitildi)
TOPIC_TRANSLATIONS = {
    'travel': 'seyahat',
    'food': 'yemek',
    'fashion': 'moda',
    'fitness': 'fitness',
    'cooking': 'yemek',
    'workout': 'fitness',
    'recipe': 'yemek tarifi',
    'style': 'moda',
}


def _call_trendify_ai(topic, platform, context):
    """Trendify AI servisini çağırır (kendi modelimiz)"""
    # İngilizce ise Türkçeye çevir
    topic_lower = topic.lower().strip()
    if topic_lower in TOPIC_TRANSLATIONS:
        topic = TOPIC_TRANSLATIONS[topic_lower]
    try:
        response = requests.post(
                TRENDIFY_AI_URL,
                json={
                    'topic': topic,
                    'platform': platform,
                    'context': context
                },
                timeout=120
            )

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data.get('recommendation', '')
            else:
                raise ValueError(f"AI servisi hata döndü: {data.get('message')}")
        else:
            raise ValueError(f"AI servisi: HTTP {response.status_code}")

    except requests.exceptions.ConnectionError:
        raise ValueError('AI servisi çalışmıyor.')
    except requests.exceptions.Timeout:
        raise ValueError('AI servisi zaman aşımına uğradı.')