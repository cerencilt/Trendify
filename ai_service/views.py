import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Egitilmis modeli bir kez yukle (sunucu baslarken)
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'trendify_model')
print("Trendify modeli yukleniyor...")
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
print("Model yuklendi!")

@csrf_exempt
def get_recommendation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic = data.get('topic', '')
            platform = data.get('platform', '')
            context = data.get('context', '')

            # Soru olustur
            if context:
                soru = f"{platform}'da {topic} icerikleri icin oneri ver. {context}"
            else:
                soru = f"{platform}'da {topic} icerikleri icin en iyi paylasim zamani ve oneriler nedir?"

            prompt = f"Soru: {soru}\nCevap:"
            inputs = tokenizer(prompt, return_tensors="pt")

            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.3,
                no_repeat_ngram_size=3,
                pad_token_id=tokenizer.eos_token_id
            )

            tam_cevap = tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Sadece "Cevap:" kismindan sonrasini al
            if "Cevap:" in tam_cevap:
                recommendation = tam_cevap.split("Cevap:", 1)[1].strip()
            else:
                recommendation = tam_cevap

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