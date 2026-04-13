import pandas as pd
from sqlalchemy import create_engine

DB_USER     = "postgres"
DB_PASSWORD = "1234"   # kurulumda yazdığın şifre
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "trendify"

CSV_FILE = "data/processed/trendify_for_backend.csv"
TABLE    = "social_media_posts"

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

df = pd.read_csv(CSV_FILE)
print(f"Yüklendi: {len(df)} satır")

df.to_sql(TABLE, engine, if_exists="replace", index=False)
print(f"✓ '{TABLE}' tablosuna {len(df)} satır yazıldı.")