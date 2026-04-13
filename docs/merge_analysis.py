"""
Trendify – Analiz Sonuçlarını trendify_clean Üzerine Ekle
"""

import os
import pandas as pd
import numpy as np

IN_CLEAN   = "data/cleaned/trendify_clean.csv"
IN_HOURS   = "data/processed/platform_best_hours.csv"
IN_CONTENT = "data/processed/content_type_performance.csv"
IN_HASHTAG = "data/processed/hashtag_performance.csv"
IN_WEEKEND = "data/processed/weekday_vs_weekend.csv"
OUT_FILE   = "data/processed/trendify_enriched.csv"

df      = pd.read_csv(IN_CLEAN)
hours   = pd.read_csv(IN_HOURS)
content = pd.read_csv(IN_CONTENT)
hashtag = pd.read_csv(IN_HASHTAG)
weekend = pd.read_csv(IN_WEEKEND)

df["post_time"]   = pd.to_numeric(df["post_time"],   errors="coerce")
df["day_of_week"] = pd.to_numeric(df["day_of_week"], errors="coerce")
print(f"Yüklendi: {len(df)} satır")

# 1. SAAT SKORU
hours_join = hours[["platform","post_time","avg_likes","rank"]].rename(columns={"avg_likes":"hour_avg_likes","rank":"hour_rank"})
df["post_time_int"] = df["post_time"].astype("Int64")
df = df.merge(hours_join, left_on=["platform","post_time_int"], right_on=["platform","post_time"], how="left", suffixes=("","_h"))
df = df.drop(columns=["post_time_h","post_time_int"], errors="ignore")
print("✓ Saat skoru eklendi")

# 2. İÇERİK TÜRÜ SKORU
content_join = content[["content_type","avg_likes","avg_engagement_rate","rank"]].rename(columns={
    "avg_likes":"content_avg_likes","avg_engagement_rate":"content_avg_engagement_rate","rank":"content_rank"})
df = df.merge(content_join, on="content_type", how="left")
print("✓ İçerik türü skoru eklendi")

# 3. HASHTAG SKORU
hashtag_lookup = hashtag.set_index("hashtag")["avg_likes"].to_dict()
hashtag_rank   = hashtag.set_index("hashtag")["rank"].to_dict()

def hashtag_score(tag_str):
    if pd.isna(tag_str):
        return np.nan, np.nan
    tags   = [t.strip() for t in tag_str.split() if t.startswith("#")]
    scores = [hashtag_lookup[t] for t in tags if t in hashtag_lookup]
    ranks  = [hashtag_rank[t]   for t in tags if t in hashtag_rank]
    if not scores:
        return np.nan, np.nan
    return round(sum(scores)/len(scores), 2), round(sum(ranks)/len(ranks), 2)

df[["hashtag_avg_likes","hashtag_avg_rank"]] = df["hashtags"].apply(lambda x: pd.Series(hashtag_score(x)))
print("✓ Hashtag skoru eklendi")

# 4. GÜN SKORU
daily = weekend[weekend["section"]=="gun_bazli"][["day_of_week","avg_likes","avg_engagement_rate"]].rename(columns={
    "avg_likes":"day_avg_likes","avg_engagement_rate":"day_avg_engagement_rate"})
daily["day_of_week"] = daily["day_of_week"].astype("Int64")
df["day_of_week_int"] = df["day_of_week"].astype("Int64")
df = df.merge(daily, left_on="day_of_week_int", right_on="day_of_week", how="left", suffixes=("","_d"))
df = df.drop(columns=["day_of_week_d","day_of_week_int"], errors="ignore")
print("✓ Gün skoru eklendi")

# 5. OPTİMİZASYON SKORU
def minmax(s):
    mn, mx = s.min(), s.max()
    return pd.Series(np.nan, index=s.index) if mx == mn else (s - mn) / (mx - mn) * 100

df["_s_hour"]    = minmax(df["hour_rank"].max() - df["hour_rank"])
df["_s_content"] = minmax(df["content_rank"].max() - df["content_rank"])
df["_s_hashtag"] = minmax(df["hashtag_avg_likes"])
df["_s_day"]     = minmax(df["day_avg_likes"])
df["optimization_score"] = (
    df["_s_hour"].fillna(50)    * 0.35 +
    df["_s_content"].fillna(50) * 0.30 +
    df["_s_hashtag"].fillna(50) * 0.20 +
    df["_s_day"].fillna(50)     * 0.15
).round(2)
df = df.drop(columns=["_s_hour","_s_content","_s_hashtag","_s_day"])
print("✓ Optimizasyon skoru eklendi")

df.to_csv(OUT_FILE, index=False)
print(f"\n✓ Kaydedildi → {OUT_FILE}")
print(f"  {len(df)} satır, {len(df.columns)} sütun")