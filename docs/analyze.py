"""
Trendify – Veri Analiz Scripti
"""

import os
import pandas as pd
import numpy as np

IN_FILE = "data/cleaned/trendify_clean.csv"
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(IN_FILE)
df["post_time"]       = pd.to_numeric(df["post_time"],       errors="coerce")
df["day_of_week"]     = pd.to_numeric(df["day_of_week"],     errors="coerce")
df["engagement_rate"] = pd.to_numeric(df["engagement_rate"], errors="coerce")
df["likes"]           = pd.to_numeric(df["likes"],           errors="coerce")
print(f"Yüklendi: {len(df)} satır")

# 1. PLATFORM BAZLI EN İYİ SAAT
hour_df = df[df["post_time"].notna()].copy()
hour_df["post_time"] = hour_df["post_time"].astype(int)
platform_hours = (
    hour_df.groupby(["platform", "post_time"])
    .agg(avg_likes=("likes", "mean"), avg_engagement_rate=("engagement_rate", "mean"), post_count=("likes", "count"))
    .reset_index().round(2)
)
platform_hours = platform_hours.sort_values(["platform", "avg_likes"], ascending=[True, False])
platform_hours["rank"] = platform_hours.groupby("platform")["avg_likes"].rank(ascending=False, method="first").astype(int)
platform_hours.to_csv(f"{OUT_DIR}/platform_best_hours.csv", index=False)
print(f"✓ platform_best_hours.csv ({len(platform_hours)} satır)")

# 2. İÇERİK TÜRÜ PERFORMANSI
ct_df = df[df["content_type"].notna()].copy()
content_perf = (
    ct_df.groupby("content_type")
    .agg(avg_likes=("likes", "mean"), avg_comments=("comments", "mean"),
         avg_shares=("shares", "mean"), avg_views=("views", "mean"),
         avg_engagement_rate=("engagement_rate", "mean"), post_count=("likes", "count"))
    .reset_index().round(2)
)
content_perf = content_perf.sort_values("avg_likes", ascending=False)
content_perf["rank"] = range(1, len(content_perf) + 1)
content_perf.to_csv(f"{OUT_DIR}/content_type_performance.csv", index=False)
print(f"✓ content_type_performance.csv ({len(content_perf)} satır)")

# 3. HASHTAG ETKİNLİĞİ
hash_df = df[df["hashtags"].notna()].copy()
hash_df["hashtag"] = hash_df["hashtags"].str.strip().str.split()
hash_df = hash_df.explode("hashtag")
hash_df = hash_df[hash_df["hashtag"].str.startswith("#") & (hash_df["hashtag"].str.len() > 2)]
hashtag_perf = (
    hash_df.groupby("hashtag")
    .agg(avg_likes=("likes", "mean"), avg_engagement_rate=("engagement_rate", "mean"), usage_count=("hashtag", "count"))
    .reset_index().round(2)
)
hashtag_perf = hashtag_perf[hashtag_perf["usage_count"] >= 5].sort_values("avg_likes", ascending=False)
hashtag_perf["rank"] = range(1, len(hashtag_perf) + 1)
hashtag_perf.to_csv(f"{OUT_DIR}/hashtag_performance.csv", index=False)
print(f"✓ hashtag_performance.csv ({len(hashtag_perf)} satır)")

# 4. HAFTA İÇİ / HAFTA SONU
GUN = {0:"Pazartesi",1:"Salı",2:"Çarşamba",3:"Perşembe",4:"Cuma",5:"Cumartesi",6:"Pazar"}
general = (
    df.groupby("is_weekend")
    .agg(avg_likes=("likes","mean"), avg_comments=("comments","mean"),
         avg_shares=("shares","mean"), avg_engagement_rate=("engagement_rate","mean"), post_count=("likes","count"))
    .reset_index().round(2)
)
general["is_weekend"] = general["is_weekend"].map({0:"Hafta İçi", 1:"Hafta Sonu"})
general = general.rename(columns={"is_weekend":"period"})
general["section"] = "genel"

platform_we = (
    df.groupby(["platform","is_weekend"])
    .agg(avg_likes=("likes","mean"), avg_engagement_rate=("engagement_rate","mean"), post_count=("likes","count"))
    .reset_index().round(2)
)
platform_we["is_weekend"] = platform_we["is_weekend"].map({0:"Hafta İçi", 1:"Hafta Sonu"})
platform_we = platform_we.rename(columns={"is_weekend":"period"})
platform_we["section"] = "platform_bazli"

dow_df = df[df["day_of_week"].notna()].copy()
dow_df["day_of_week"] = dow_df["day_of_week"].astype(int)
daily = (
    dow_df.groupby("day_of_week")
    .agg(avg_likes=("likes","mean"), avg_engagement_rate=("engagement_rate","mean"), post_count=("likes","count"))
    .reset_index().round(2)
)
daily["day_name"]   = daily["day_of_week"].map(GUN)
daily["is_weekend"] = daily["day_of_week"].isin([5,6]).map({True:"Hafta Sonu", False:"Hafta İçi"})
daily["section"]    = "gun_bazli"

weekend_combined = pd.concat([general, platform_we, daily], ignore_index=True, sort=False)
weekend_combined.to_csv(f"{OUT_DIR}/weekday_vs_weekend.csv", index=False)
print(f"✓ weekday_vs_weekend.csv ({len(weekend_combined)} satır)")
print("\nTüm analizler tamamlandı.")