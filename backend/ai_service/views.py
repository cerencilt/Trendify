import os
import json
import torch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from transformers import AutoTokenizer, AutoModelForCausalLM

# Model dosyalarının yolu
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model')

# Modeli ve tokenizer'ı global olarak yükle (sadece bir kez)
print("Trendify AI modeli yükleniyor...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
print("Trendify AI modeli hazır!")


@csrf_exempt
def get_recommendation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic = data.get('topic', '')
            platform = data.get('platform', '')
            context = data.get('context', '')

            # Soru formatı (Gökçe'nin belirttiği gibi)
            soru = f"{platform} platformunda {topic} içeriği için en iyi paylaşım önerileri nelerdir? Analiz verisi: {context}"
            prompt = f"Soru: {soru}\nCevap:"

            # Tokenize et
            inputs = tokenizer(prompt, return_tensors="pt")

            # Üret
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.3,
                no_repeat_ngram_size=3,
                pad_token_id=tokenizer.eos_token_id
            )

            # Decode et
            full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Sadece "Cevap:" kısmından sonrasını al
            if "Cevap:" in full_text:
                recommendation = full_text.split("Cevap:")[-1].strip()
            else:
                recommendation = full_text.strip()

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