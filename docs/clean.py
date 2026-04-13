
import os
import pandas as pd
import numpy as np

# ── Yollar ────────────────────────────────────────────────────────────────────
RAW_SENTIMENT = "data/raw/archive1/sentimentdataset.csv"
RAW_MEDIARATES = "data/raw/archive2/mediarates.xlsx"
RAW_VIRAL = "data/raw/archive3/Cleaned_Viral_Social_Media_Trends.csv"
OUT_DIR = "data/cleaned"
OUT_FILE = os.path.join(OUT_DIR, "trendify_clean.csv")

os.makedirs(OUT_DIR, exist_ok=True)

# ── Standart sütun listesi (ekip bu isimleri kullanır) ────────────────────────
STANDARD_COLS = [
    "platform",    # str  : Instagram | TikTok | YouTube | Twitter | Facebook
    "date",        # date : YYYY-MM-DD
    "post_time",   # int  : 0-23  (paylaşım saati)
    "day_of_week", # int  : 0=Pazartesi … 6=Pazar
    "is_weekend",  # int  : 0=hayır  1=evet
    "content_type",# str  : Video | Image | Text | Live
    "hashtags",    # str  : '#tag1 #tag2 …'
    "likes",       # int  : beğeni sayısı
    "comments",    # int  : yorum sayısı
    "shares",      # int  : paylaşım / retweet sayısı
    "views",       # int  : görüntülenme (yoksa NaN)
    "engagement_rate",   # float : (likes+comments+shares)/views*100
    "engagement_level",  # str   : High | Medium | Low
    "source",      # str  : hangi datasetten geldiği
]


# ══════════════════════════════════════════════════════════════════════════════
# YARDIMCI FONKSİYONLAR
# ══════════════════════════════════════════════════════════════════════════════

def normalize_platform(series: pd.Series) -> pd.Series:
    """Platform adlarındaki boşluk/büyük-küçük harf farklarını temizler."""
    mapping = {
        "twitter": "Twitter",
        "instagram": "Instagram",
        "facebook": "Facebook",
        "tiktok": "TikTok",
        "youtube": "YouTube",
    }
    return series.str.strip().str.lower().map(mapping).fillna("Unknown")


def normalize_content_type(series: pd.Series) -> pd.Series:
    """Farklı datasetlerdeki içerik türü adlarını tek formata indirir."""
    mapping = {
        # Video grubu
        "video": "Video",
        "shorts": "Video",
        "reel": "Video",
        # Image grubu
        "image": "Image",
        "post": "Image",
        # Text grubu
        "text": "Text",
        "tweet": "Text",
        # Live grubu
        "live stream": "Live",
        "live": "Live",
    }
    return series.str.strip().str.lower().map(mapping)


def derive_engagement_level(rate: pd.Series) -> pd.Series:
    """engagement_rate değerinden High/Medium/Low üretir."""
    result = pd.Series("Low", index=rate.index, dtype=object)
    result[rate >= 3] = "Medium"
    result[rate >= 6] = "High"
    result[rate.isna()] = np.nan
    return result


def align_to_standard(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame'i standart sütun listesine hizalar; eksik sütunları NaN yapar."""
    for col in STANDARD_COLS:
        if col not in df.columns:
            df[col] = np.nan
    return df[STANDARD_COLS]


def print_report(label: str, df: pd.DataFrame) -> None:
    print(f"\n{'─'*55}")
    print(f"  {label}")
    print(f"{'─'*55}")
    print(f"  Satır : {len(df):,}   Sütun : {len(df.columns)}")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        print("  Eksik değer : yok")
    else:
        for col, cnt in missing.items():
            print(f"  Eksik  {col:<20} {cnt:>5} ({cnt/len(df)*100:.1f}%)")


# ══════════════════════════════════════════════════════════════════════════════
# 1. SENTİMENT DATASETİ
#    Sütunlar: Unnamed:0.1, Unnamed:0, Text, Sentiment, Timestamp, User,
#              Platform, Hashtags, Retweets, Likes, Country, Year, Month, Day, Hour
# ══════════════════════════════════════════════════════════════════════════════

print("\n[1/3] sentiment_dataset okunuyor…")
raw_s = pd.read_csv(RAW_SENTIMENT)

s = raw_s.copy()

# Gereksiz sütunları düşür
s = s.drop(columns=["Unnamed: 0.1", "Unnamed: 0", "Text", "User", "Country",
                     "Sentiment", "Year", "Month", "Day"])

# Timestamp → date ve post_time
s["Timestamp"] = pd.to_datetime(s["Timestamp"], errors="coerce")
s["date"] = s["Timestamp"].dt.date
s["post_time"] = s["Hour"].astype("Int64")    # Int64 → NaN destekler
s["day_of_week"] = s["Timestamp"].dt.dayofweek
s["is_weekend"] = s["day_of_week"].isin([5, 6]).astype(int)
s = s.drop(columns=["Timestamp", "Hour"])

# Sütun yeniden adlandır
s = s.rename(columns={
    "Platform": "platform",
    "Hashtags": "hashtags",
    "Retweets": "shares",
    "Likes": "likes",
})

# Platform normalize
s["platform"] = normalize_platform(s["platform"])

# Eksik likes/shares satırlarını düşür (çok az, 0 zaten)
s = s.dropna(subset=["likes", "shares"])
s["likes"] = s["likes"].astype(int)
s["shares"] = s["shares"].astype(int)

# Bu datasette yorum ve görüntüleme yok
s["comments"] = np.nan
s["views"] = np.nan
s["content_type"] = np.nan
s["engagement_rate"] = np.nan
s["engagement_level"] = np.nan
s["source"] = "sentiment_dataset"

s = align_to_standard(s)
print_report("sentiment_dataset", s)


# ══════════════════════════════════════════════════════════════════════════════
# 2. MEDİARATES DATASETİ
#    Sütunlar: user_id, post_type, post_length, likes, comments, shares,
#              engagement_rate, user_followers, post_category, post_hour,
#              is_weekend, user_verified, spam_flag
#    NOT: Platform ve tarih bilgisi YOK.
# ══════════════════════════════════════════════════════════════════════════════

print("\n[2/3] mediarates_dataset okunuyor…")
raw_m = pd.read_excel(RAW_MEDIARATES)

m = raw_m.copy()

# Spam satırlarını kaldır
before = len(m)
m = m[m["spam_flag"] == 0].copy()
print(f"  Spam temizlendi: {before - len(m)} satır kaldırıldı")

# Gereksiz sütunlar
m = m.drop(columns=["spam_flag", "user_id", "post_length",
                     "user_followers", "user_verified", "post_category"])

# Eksik değerleri medyan ile doldur
m["engagement_rate"] = m["engagement_rate"].fillna(m["engagement_rate"].median())

# Sütun yeniden adlandır
m = m.rename(columns={
    "post_type": "content_type",
    "post_hour": "post_time",
})

# Platform bu datasette YOK → Unknown
m["platform"] = "Unknown"

# Tarih bu datasette YOK → NaN
# day_of_week: sadece is_weekend bilgisi var, tam gün bilinmiyor → NaN
m["date"] = pd.NaT
m["day_of_week"] = np.nan    # uydurmak yerine NaN bırakıyoruz

# content_type normalize
m["content_type"] = normalize_content_type(m["content_type"])

# engagement_level türet
m["engagement_level"] = derive_engagement_level(m["engagement_rate"])

# Bu datasette views ve hashtags yok
m["views"] = np.nan
m["hashtags"] = np.nan
m["source"] = "mediarates_dataset"

m = align_to_standard(m)
print_report("mediarates_dataset", m)


# ══════════════════════════════════════════════════════════════════════════════
# 3. VİRAL TRENDS DATASETİ
#    Sütunlar: Post_ID, Post_Date, Platform, Hashtag, Content_Type,
#              Region, Views, Likes, Shares, Comments, Engagement_Level
# ══════════════════════════════════════════════════════════════════════════════

print("\n[3/3] viral_trends_dataset okunuyor…")
raw_v = pd.read_csv(RAW_VIRAL)

v = raw_v.copy()

# Gereksiz sütun
v = v.drop(columns=["Post_ID", "Region"])

# Tarih sütunu
v["Post_Date"] = pd.to_datetime(v["Post_Date"], errors="coerce")
v["date"] = v["Post_Date"].dt.date
v["day_of_week"] = v["Post_Date"].dt.dayofweek
v["is_weekend"] = v["day_of_week"].isin([5, 6]).astype(int)
v = v.drop(columns=["Post_Date"])

# Bu datasette paylaşım saati yok
v["post_time"] = np.nan

# Sütun yeniden adlandır
v = v.rename(columns={
    "Platform": "platform",
    "Hashtag": "hashtags",
    "Content_Type": "content_type",
    "Views": "views",
    "Likes": "likes",
    "Shares": "shares",
    "Comments": "comments",
    "Engagement_Level": "engagement_level",
})

# Platform normalize
v["platform"] = normalize_platform(v["platform"])

# content_type normalize
v["content_type"] = normalize_content_type(v["content_type"])

# engagement_rate hesapla
v["engagement_rate"] = (
    (v["likes"] + v["comments"] + v["shares"]) / v["views"] * 100
).round(4)

v["source"] = "viral_trends_dataset"

v = align_to_standard(v)
print_report("viral_trends_dataset", v)


# ══════════════════════════════════════════════════════════════════════════════
# 4. BİRLEŞTİR (UNION – dikey, yatay JOIN değil)
# ══════════════════════════════════════════════════════════════════════════════

print(f"\n{'─'*55}")
print("  Datasetler birleştiriliyor (pd.concat)…")

merged = pd.concat([s, m, v], ignore_index=True)

# Tip düzeltmeleri
merged["likes"] = pd.to_numeric(merged["likes"], errors="coerce").astype("Int64")
merged["comments"] = pd.to_numeric(merged["comments"], errors="coerce").astype("Int64")
merged["shares"] = pd.to_numeric(merged["shares"], errors="coerce").astype("Int64")
merged["views"] = pd.to_numeric(merged["views"], errors="coerce").astype("Int64")
merged["post_time"] = pd.to_numeric(merged["post_time"], errors="coerce").astype("Int64")
merged["day_of_week"] = pd.to_numeric(merged["day_of_week"], errors="coerce").astype("Int64")

# Negatif değer kontrolü (veri kalitesi)
neg_likes = (merged["likes"].fillna(0) < 0).sum()
if neg_likes > 0:
    print(f"  UYARI: {neg_likes} satırda negatif likes bulundu → kaldırıldı")
    merged = merged[merged["likes"].fillna(0) >= 0]

print_report("BİRLEŞİK VERİ (final)", merged)


# ══════════════════════════════════════════════════════════════════════════════
# 5. KAYDET
# ══════════════════════════════════════════════════════════════════════════════

merged.to_csv(OUT_FILE, index=False)

print(f"\n{'═'*55}")
print(f"  ✓ Kaydedildi  →  {OUT_FILE}")
print(f"  Toplam satır  :  {len(merged):,}")
print(f"  Toplam sütun  :  {len(merged.columns)}")
print(f"  Sütunlar      :  {merged.columns.tolist()}")
print(f"{'═'*55}\n")