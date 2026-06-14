from transformers import AutoModelForCausalLM, AutoTokenizer

print("Model yukleniyor...")
model = AutoModelForCausalLM.from_pretrained("./trendify_model")
tokenizer = AutoTokenizer.from_pretrained("./trendify_model")

soru = "Instagram'da yemek icerikleri icin en iyi paylasim zamani nedir?"
prompt = f"Soru: {soru}\nCevap:"
inputs = tokenizer(prompt, return_tensors="pt")

print("Cevap uretiliyor...")
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

cevap = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("\n=== MODEL CEVABI ===")
print(cevap)