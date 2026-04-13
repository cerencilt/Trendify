import os
from openai import OpenAI
from dotenv import load_dotenv
from analysis.models import Analysis
from .models import Recommendation

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DAY_NAMES = {
    0: 'Pazartesi', 1: 'Salı', 2: 'Çarşamba',
    3: 'Perşembe', 4: 'Cuma', 5: 'Cumartesi', 6: 'Pazar'
}


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
    ai_response = _call_openai(topic, platform, context)

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


def _call_openai(topic, platform, context):
    prompt = f"""Sen bir sosyal medya uzmanısın.
Aşağıdaki bilgilere göre öneri ver:

Platform: {platform}
İçerik konusu: {topic}
Analiz verisi: {context}

Lütfen şunları öner:
1. En iyi paylaşım zamanı
2. Önerilen hashtagler
3. İçerik açıklaması
4. Müzik önerisi
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Sen bir sosyal medya içerik uzmanısın. Türkçe cevap ver."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=500
    )

    return response.choices[0].message.content