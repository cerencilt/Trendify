from pathlib import Path

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from analysis.models import SocialMediaPost


class Command(BaseCommand):
    help = 'Kaggle CSV dosyalarını veritabanına yükler'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default='data',
            help='CSV dosyasının veya CSV dosyalarının bulunduğu klasörün yolu'
        )

    def handle(self, *args, **options):
        data_path = self._resolve_path(options['path'])

        if not data_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Klasör bulunamadı: {data_path}')
            )
            return

        if data_path.is_file():
            if data_path.suffix.lower() != '.csv':
                self.stdout.write(
                    self.style.ERROR(f'CSV dosyası değil: {data_path}')
                )
                return
            csv_files = [data_path]
        else:
            csv_files = sorted(
                path for path in data_path.iterdir()
                if path.is_file() and path.suffix.lower() == '.csv'
            )

        if not csv_files:
            self.stdout.write(self.style.ERROR('CSV dosyası bulunamadı!'))
            return

        total_created = 0
        total_skipped = 0

        for csv_file in csv_files:
            self.stdout.write(f'Yükleniyor: {csv_file.name}')

            try:
                df = pd.read_csv(csv_file)
                df.columns = df.columns.str.lower().str.strip()
                created, skipped = self._load_dataframe(df, csv_file.name)
                total_created += created
                total_skipped += skipped
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ {created} kayıt eklendi, {skipped} satır atlandı'
                    )
                )
            except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError, UnicodeDecodeError, ValueError) as error:
                self.stdout.write(self.style.ERROR(f'  ✗ Hata: {error}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nToplam {total_created} kayıt yüklendi, {total_skipped} satır atlandı!'
            )
        )

    def _load_dataframe(self, df, filename):
        source = self._detect_source(filename)
        posts = []
        skipped = 0

        for _, row in df.iterrows():
            try:
                post = SocialMediaPost(
                    platform=self._safe_str(row, 'platform', 'Unknown'),
                    source=self._safe_str(row, 'source', source),
                    date=self._safe_date(row, 'date'),
                    post_time=self._safe_int(row, 'post_time'),
                    day_of_week=self._safe_int(row, 'day_of_week'),
                    is_weekend=bool(self._safe_int(row, 'is_weekend', 0)),
                    content_type=self._safe_str(row, 'content_type'),
                    hashtags=self._safe_str(row, 'hashtags'),
                    likes=self._safe_int(row, 'likes', 0),
                    comments=self._safe_int(row, 'comments'),
                    shares=self._safe_int(row, 'shares', 0),
                    views=self._safe_int(row, 'views'),
                    engagement_rate=self._safe_float(row, 'engagement_rate'),
                    engagement_level=self._safe_str(row, 'engagement_level'),
                )
                posts.append(post)
            except (TypeError, ValueError):
                skipped += 1

        SocialMediaPost.objects.bulk_create(posts, ignore_conflicts=True)
        return len(posts), skipped

    def _resolve_path(self, path_option):
        path = Path(path_option)
        if path.is_absolute():
            return path
        return Path(settings.BASE_DIR) / path

    def _detect_source(self, filename):
        filename = filename.lower()
        if 'sentiment' in filename:
            return 'sentiment_dataset'
        elif 'media' in filename or 'rates' in filename:
            return 'mediarates_dataset'
        elif 'viral' in filename or 'trend' in filename:
            return 'viral_trends_dataset'
        return 'sentiment_dataset'

    def _safe_str(self, row, col, default=None):
        if col in row and pd.notna(row[col]):
            return str(row[col]).strip()
        return default

    def _safe_int(self, row, col, default=None):
        if col in row and pd.notna(row[col]):
            try:
                return int(float(row[col]))
            except (ValueError, TypeError):
                return default
        return default

    def _safe_float(self, row, col, default=None):
        if col in row and pd.notna(row[col]):
            try:
                return float(row[col])
            except (ValueError, TypeError):
                return default
        return default

    def _safe_date(self, row, col):
        if col in row and pd.notna(row[col]):
            try:
                return pd.to_datetime(row[col]).date()
            except (TypeError, ValueError):
                return None
        return None
