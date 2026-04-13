import requests
from analysis.models import Analysis
from .models import Recommendation

DAY_NAMES = {
    0: 'Pazartesi', 1: 'Salı', 2: 'Çarşamba',
    3: 'Perşembe', 4: 'Cuma', 5: 'Cumartesi', 6: 'Pazar'
}

AI_SERVICE_URL = "http://127.0.0.1:8001/api/ai/recommend/"


def generate_recommendation(user, analysis_id, platform=None, topic=None):
    # Analizi getir
    try:
        analysis = Analysis.objects.get(id=analysis_id, user=user)
    except Analysis.DoesNotExist:
        raise ValueError('Analiz bulunamadı.')

    if analysis.status != 'completed':
        raise ValueError('Analiz henüz tamamlanmadı.')

    if not hasattr(analysis, 'result'):
        raise ValueError('Analiz sonucu bulunamadı.')

    result = analysis.result

    # Platform ve topic belirle
    platform = platform or analysis.platform or 'Instagram'
    topic = topic or analysis.topic or ''

    # Gün adını belirle
    best_day_name = DAY_NAMES.get(result.best_day, 'Bilinmiyor')

    # En iyi içerik türünü bul
    best_content_type = None
    if result.content_type_performance:
        best_content_type = max(
            result.content_type_performance,
            key=result.content_type_performance.get
        )

    # AI'a gönderilecek context'i oluştur
    context = _build_context(result, best_day_name, best_content_type)

    # AI servisine istek at
    ai_response = _call_ai_service(topic, platform, context)

    # AI cevabını parse et
    parsed = _parse_ai_response(ai_response)

    # Kaydet
    recommendation = Recommendation.objects.create(
        user=user,
        analysis=analysis,
        platform=platform,
        topic=topic,
        post_time=result.best_post_time,
        best_day=best_day_name,
        hashtags=parsed.get('hashtags', ''),
        caption=parsed.get('caption', ''),
        music=parsed.get('music', ''),
        reasoning=parsed.get('reasoning', ai_response)
    )

    return recommendation


def _build_context(result, best_day_name, best_content_type):
    """Analiz sonuçlarından AI için context metni oluşturur"""
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

    if result.content_type_performance:
        perf_str = ', '.join([
            f"{k}: {int(v)} beğeni"
            for k, v in result.content_type_performance.items()
        ])
        context_parts.append(f"İçerik türü performansları: {perf_str}")

    return '\n'.join(context_parts)


def _call_ai_service(topic, platform, context):
    """AI servisine HTTP isteği atar"""
    try:
        response = requests.post(
            AI_SERVICE_URL,
            json={
                'topic': topic,
                'platform': platform,
                'context': context
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data.get('recommendation', '')
            else:
                raise ValueError(
                    f"AI servisi hata döndü: {data.get('message')}"
                )
        else:
            raise ValueError(
                f"AI servisine ulaşılamadı: HTTP {response.status_code}"
            )

    except requests.exceptions.ConnectionError:
        raise ValueError(
            'AI servisi çalışmıyor. '
            'Lütfen AI servisinin 8001 portunda çalıştığından emin olun.'
        )
    except requests.exceptions.Timeout:
        raise ValueError('AI servisi zaman aşımına uğradı.')


def _parse_ai_response(ai_text):
    """AI'dan gelen metni parse eder"""
    parsed = {
        'hashtags': '',
        'caption': '',
        'music': '',
        'reasoning': ai_text
    }

    if not ai_text:
        return parsed

    lines = ai_text.split('\n')

    for i, line in enumerate(lines):
        line_lower = line.lower()

        if 'hashtag' in line_lower and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line:
                parsed['hashtags'] = next_line

        if ('açıklama' in line_lower or 'caption' in line_lower) \
                and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line:
                parsed['caption'] = next_line

        if ('müzik' in line_lower or 'music' in line_lower) \
                and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line:
                parsed['music'] = next_line

    return parsed