import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@csrf_exempt
def get_recommendation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic = data.get('topic', '')
            platform = data.get('platform', '')
            context = data.get('context', '')

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

            recommendation = response.choices[0].message.content

            return JsonResponse({
                'status': 'success',
                'recommendation': recommendation
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Sadece POST kabul edilir'
    }, status=405)