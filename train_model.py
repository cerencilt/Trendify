import json
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments
from torch.utils.data import Dataset

# 1. Veriyi yükle
print("Veri yukleniyor...")
data = []
with open("data/trendify_all_categories.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        text = f"Soru: {item['prompt']}\nCevap: {item['response']}<|endoftext|>"
        data.append(text)

print(f"Toplam {len(data)} ornek yuklendi.")

# 2. Model ve tokenizer yukle
print("Model yukleniyor...")
model_name = "distilgpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = GPT2LMHeadModel.from_pretrained(model_name)

# 3. Dataset sinifi
class TrendifyDataset(Dataset):
    def __init__(self, texts, tokenizer, max_length=256):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors="pt"
        )

    def __len__(self):
        return len(self.encodings["input_ids"])

    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item["labels"] = item["input_ids"].clone()
        return item

print("Veri hazirlaniyor...")
dataset = TrendifyDataset(data, tokenizer)

# 4. Egitim ayarlari - DAHA KALITELI
training_args = TrainingArguments(
    output_dir="./trendify_model",
    num_train_epochs=8,
    per_device_train_batch_size=4,
    learning_rate=3e-5,
    warmup_steps=100,
    save_steps=1000,
    save_total_limit=1,
    logging_steps=50,
    use_cpu=True
)

# 5. Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

# 6. Egitimi baslat
print("EGITIM BASLIYOR... (CPU'da uzun surebilir, sabirli ol)")
trainer.train()

# 7. Modeli kaydet
print("Model kaydediliyor...")
model.save_pretrained("./trendify_model")
tokenizer.save_pretrained("./trendify_model")
print("TAMAMLANDI! Model ./trendify_model klasorune kaydedildi.")