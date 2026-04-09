import pandas as pd
from .models import Analysis, AnalysisResult, SocialMediaPost


def run_analysis(analysis_id):
    """
    Analizi çalıştırır ve sonuçları kaydeder.
    analysis_id: Analysis modelinin id'si
    """
    try:
        analysis = Analysis.objects.get(id=analysis_id)
        analysis.status = 'running'
        analysis.save()

        if analysis.input_type == 'content_based':
            result = _run_content_based(analysis)
        else:
            result = _run_performance_based(analysis)

        analysis.status = 'completed'
        analysis.save()
        return result

    except Exception as e:
        analysis.status = 'failed'
        analysis.error_message = str(e)
        analysis.save()
        raise e


def _run_content_based(analysis):
    """
    İçerik bazlı analiz:
    Kullanıcının girdiği platform ve konuya göre
    Kaggle verisinden öneriler üretir.
    """
    # Platforma göre filtrele
    queryset = SocialMediaPost.objects.all()
    if analysis.platform:
        queryset = queryset.filter(platform=analysis.platform)

    # Veri yoksa hata fırlat
    if not queryset.exists():
        raise ValueError('Yeterli veri bulunamadı.')

    # Pandas'a çevir
    df = _queryset_to_df(queryset)

    return _calculate_and_save_result(analysis, df)


def _run_performance_based(analysis):
    """
    Performans bazlı analiz:
    Kullanıcının yüklediği CSV'yi analiz eder.
    """
    if not analysis.csv_file:
        raise ValueError('CSV dosyası bulunamadı.')

    # CSV'yi oku
    df = pd.read_csv(analysis.csv_file.path)

    # Sütun adlarını küçük harfe çevir
    df.columns = df.columns.str.lower().str.strip()

    # Gerekli sütunlar var mı kontrol et
    required_columns = ['likes', 'shares']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f'CSV dosyasında eksik sütunlar: {missing}')

    return _calculate_and_save_result(analysis, df)


def _queryset_to_df(queryset):
    """QuerySet'i DataFrame'e çevirir"""
    data = list(queryset.values(
        'platform', 'date', 'post_time', 'day_of_week',
        'is_weekend', 'content_type', 'hashtags',
        'likes', 'comments', 'shares', 'views',
        'engagement_rate', 'engagement_level'
    ))
    return pd.DataFrame(data)


def _calculate_and_save_result(analysis, df):
    """
    DataFrame üzerinden analiz sonuçlarını hesaplar ve kaydeder.
    """

    # --- En iyi paylaşım saati ---
    best_post_time = None
    if 'post_time' in df.columns:
        hourly = df.groupby('post_time')['likes'].mean()
        if not hourly.empty:
            best_post_time = int(hourly.idxmax())

    # --- En iyi gün ---
    best_day = None
    if 'day_of_week' in df.columns:
        daily = df.groupby('day_of_week')['likes'].mean()
        if not daily.empty:
            best_day = int(daily.idxmax())

    # --- Ortalama metrikler ---
    avg_engagement_rate = _safe_mean(df, 'engagement_rate')
    avg_likes = _safe_mean(df, 'likes')
    avg_comments = _safe_mean(df, 'comments')
    avg_shares = _safe_mean(df, 'shares')

    # --- Trend fit score (0-100 arası normalize edilmiş engagement) ---
    trend_fit_score = None
    if avg_engagement_rate is not None:
        trend_fit_score = min(round(avg_engagement_rate * 10, 2), 100.0)

    # --- Isı haritası verisi ---
    heatmap_data = None
    if 'day_of_week' in df.columns and 'post_time' in df.columns:
        heatmap_data = _build_heatmap(df)

    # --- İçerik türü performansı ---
    content_type_performance = None
    if 'content_type' in df.columns:
        content_type_performance = _build_content_performance(df)

    # --- Kaydet ---
    result, _ = AnalysisResult.objects.update_or_create(
        analysis=analysis,
        defaults={
            'best_post_time': best_post_time,
            'best_day': best_day,
            'avg_engagement_rate': avg_engagement_rate,
            'avg_likes': avg_likes,
            'avg_comments': avg_comments,
            'avg_shares': avg_shares,
            'trend_fit_score': trend_fit_score,
            'heatmap_data': heatmap_data,
            'content_type_performance': content_type_performance,
        }
    )

    return result


def _safe_mean(df, column):
    """Sütun varsa ortalamasını döner, yoksa None"""
    if column in df.columns:
        val = df[column].dropna().mean()
        if pd.notna(val):
            return round(float(val), 2)
    return None


def _build_heatmap(df):
    """
    Gün x Saat bazında ortalama engagement_rate ısı haritası
    Format: {day: {hour: avg_engagement}}
    """
    try:
        df_clean = df[['day_of_week', 'post_time', 'likes']].dropna()
        df_clean = df_clean.astype({'day_of_week': int, 'post_time': int})
        pivot = df_clean.groupby(['day_of_week', 'post_time'])['likes'].mean()

        heatmap = {}
        for (day, hour), value in pivot.items():
            day_key = str(day)
            if day_key not in heatmap:
                heatmap[day_key] = {}
            heatmap[day_key][str(hour)] = round(float(value), 2)

        return heatmap
    except Exception:
        return None


def _build_content_performance(df):
    """
    İçerik türü bazında ortalama likes
    Format: {'Video': 1200.5, 'Image': 800.2, ...}
    """
    try:
        df_clean = df[['content_type', 'likes']].dropna()
        result = df_clean.groupby('content_type')['likes'].mean()
        return {k: round(float(v), 2) for k, v in result.items()}
    except Exception:
        return None