"""
Trendify – Backend'e Hazırlık Scripti
"""

import os
import pandas as pd
import numpy as np

IN_FILE  = "data/processed/trendify_enriched.csv"
OUT_FILE = "data/processed/trendify_for_backend.csv"

MODEL_COLS = [
    "platform","source","date","post_time","day_of_week","is_weekend",
    "content_type","hashtags","likes","comments","shares",
    "views","engagement_rate","engagement_level",
]

VALID_PLATFORM         = {"Instagram","TikTok","YouTube","Twitter","Facebook","Unknown"}
VALID_CONTENT_TYPE     = {"Video","Image","Text","Live"}
VALID_ENGAGEMENT_LEVEL = {"High","Medium","Low"}
VALID_SOURCE           = {"sentiment_dataset","mediarates_dataset","viral_trends_dataset"}

df = pd.read_csv(IN_FILE)
print(f"Yüklendi: {len(df)} satır, {len(df.columns)} sütun")

df = df[MODEL_COLS].copy()

df["date"]            = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
df["post_time"]       = df["post_time"].apply(lambda x: int(x) if pd.notna(x) else None)
df["day_of_week"]     = df["day_of_week"].apply(lambda x: int(x) if pd.notna(x) else None)
df["is_weekend"]      = df["is_weekend"].astype(int)
df["likes"]           = pd.to_numeric(df["likes"], errors="coerce").fillna(0).astype(int)
df["comments"]        = df["comments"].apply(lambda x: int(x) if pd.notna(x) else None)
df["shares"]          = pd.to_numeric(df["shares"], errors="coerce").fillna(0).astype(int)
df["views"]           = df["views"].apply(lambda x: int(x) if pd.notna(x) else None)
df["engagement_rate"] = pd.to_numeric(df["engagement_rate"], errors="coerce").round(4)

invalid = ~df["platform"].isin(VALID_PLATFORM)
df.loc[invalid, "platform"] = "Unknown"

invalid_ct = df["content_type"].notna() & ~df["content_type"].isin(VALID_CONTENT_TYPE)
df.loc[invalid_ct, "content_type"] = None

invalid_el = df["engagement_level"].notna() & ~df["engagement_level"].isin(VALID_ENGAGEMENT_LEVEL)
df.loc[invalid_el, "engagement_level"] = None

os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
df.to_csv(OUT_FILE, index=False)
print(f"✓ Kaydedildi → {OUT_FILE}")
print(f"  {len(df)} satır, {len(df.columns)} sütun")