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
    Topic, hashtags ve content_type sütunlarında aranır.
    """
    queryset = SocialMediaPost.objects.all()

    # Platforma göre filtrele
    if analysis.platform:
        queryset = queryset.filter(platform=analysis.platform)

    # Topic'e göre filtrele (hashtag ve content_type'da ara)
    if analysis.topic:
        topic = analysis.topic.strip()
        topic_keywords = _extract_topic_keywords(topic)

        # Topic'i hashtag'de ara (en az bir keyword eşleşmesi)
        from django.db.models import Q
        topic_filter = Q()
        for keyword in topic_keywords:
            topic_filter |= Q(hashtags__icontains=keyword)

        topic_queryset = queryset.filter(topic_filter)

        # Eğer topic ile yeterli kayıt bulunduysa onu kullan
        if topic_queryset.count() >= 10:
            queryset = topic_queryset
        # Aksi takdirde platform bazlı veriyi koru (topic etkisi azalır)
        # Ama içerik türünü topic'ten tahmin et
        else:
            content_type_guess = _guess_content_type(topic)
            if content_type_guess:
                content_filtered = queryset.filter(content_type=content_type_guess)
                if content_filtered.count() >= 10:
                    queryset = content_filtered

    if not queryset.exists():
        raise ValueError('Yeterli veri bulunamadı.')

    df = _queryset_to_df(queryset)
    return _calculate_and_save_result(analysis, df)


def _extract_topic_keywords(topic):
    """
    Topic'ten arama için anahtar kelimeleri çıkarır.
    Türkçe ve İngilizce karşılıkları da ekler.
    """
    # Topic'i kelimelere ayır
    words = topic.lower().split()

    # Türkçe-İngilizce çeviri sözlüğü
    translations = {
        'yemek': ['food', 'recipe', 'cooking', 'tarifi', 'mutfak'],
        'tarifi': ['recipe', 'food', 'cooking'],
        'moda': ['fashion', 'style', 'outfit', 'trend'],
        'stil': ['style', 'fashion'],
        'fitness': ['fitness', 'workout', 'gym', 'spor', 'sport'],
        'spor': ['sport', 'fitness', 'workout'],
        'seyahat': ['travel', 'vacation', 'trip', 'gezi', 'tatil'],
        'gezi': ['travel', 'trip', 'gezi'],
        'food': ['food', 'yemek', 'recipe'],
        'fashion': ['fashion', 'moda', 'style'],
        'travel': ['travel', 'seyahat', 'gezi'],
        'workout': ['workout', 'fitness', 'spor'],
    }

    keywords = set(words)
    for word in words:
        if word in translations:
            keywords.update(translations[word])

    return list(keywords)


def _guess_content_type(topic):
    """
    Topic'e göre içerik türünü tahmin eder.
    """
    topic_lower = topic.lower()

    if any(w in topic_lower for w in ['video', 'reels', 'kısa', 'tiktok']):
        return 'Video'
    elif any(w in topic_lower for w in ['canlı', 'live', 'yayın']):
        return 'Live'
    elif any(w in topic_lower for w in ['resim', 'fotoğraf', 'image', 'photo']):
        return 'Image'
    elif any(w in topic_lower for w in ['yazı', 'text', 'metin', 'tweet']):
        return 'Text'

    return None


def _run_performance_based(analysis):
    """
    Performans bazlı analiz:
    Kullanıcının yüklediği CSV'yi okur, topic'e göre filtreler ve analiz eder.
    """
    if not analysis.csv_file:
        raise ValueError('CSV dosyası bulunamadı.')

    # CSV'yi oku
    try:
        df = pd.read_csv(analysis.csv_file.path)
    except Exception as e:
        raise ValueError(f'CSV dosyası okunamadı: {str(e)}')

    # Sütun adlarını küçük harfe çevir
    df.columns = df.columns.str.lower().str.strip()

    # Gerekli sütunlar var mı kontrol et
    required_columns = ['likes']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f'CSV dosyasında zorunlu sütunlar eksik: {missing}')

    # Boş veri kontrolü
    if df.empty:
        raise ValueError('CSV dosyası boş.')

    original_count = len(df)

    # Topic'e göre filtrele (CSV içinde)
    if analysis.topic:
        topic = analysis.topic.strip()
        topic_keywords = _extract_topic_keywords(topic)

        # hashtags sütununda topic ara
        if 'hashtags' in df.columns:
            mask = df['hashtags'].fillna('').str.lower().apply(
                lambda x: any(kw in x for kw in topic_keywords)
            )
            filtered_df = df[mask]

            # Yeterli kayıt varsa filtrelenmiş veriyi kullan
            if len(filtered_df) >= 5:
                df = filtered_df
            else:
                # Hashtag'lerde bulunamadıysa content_type'a bak
                content_type_guess = _guess_content_type(topic)
                if content_type_guess and 'content_type' in df.columns:
                    content_filtered = df[
                        df['content_type'].fillna('').str.lower() == content_type_guess.lower()
                        ]
                    if len(content_filtered) >= 5:
                        df = content_filtered

    if df.empty:
        raise ValueError(
            f'"{analysis.topic}" konusu için CSV dosyasında yeterli veri bulunamadı. '
            f'Toplam {original_count} kayıt tarandı.'
        )

    # Platform'u CSV'den otomatik tespit et
    if 'platform' in df.columns and not df['platform'].empty:
        most_common_platform = df['platform'].mode()
        if not most_common_platform.empty:
            detected_platform = most_common_platform.iloc[0]
            # Analysis nesnesine kaydet
            analysis.platform = detected_platform
            analysis.save()

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


def validate_recommendation(platform, content_type=None):
    """
    Modelin önerisini gerçek veriyle doğrular (k-fold cross validation).
    IQR ile outlier temizleme + mean bazlı karşılaştırma.
    """
    from .models import SocialMediaPost
    import pandas as pd
    import numpy as np

    queryset = SocialMediaPost.objects.filter(platform=platform)
    total_count = queryset.count()

    if total_count == 0:
        return {
            'platform': platform,
            'error': f'{platform} platformu için veri bulunamadı.',
            'is_valid': False,
        }

    df = pd.DataFrame(list(queryset.values()))
    df = df.dropna(subset=['day_of_week', 'post_time', 'likes'])
    valid_count = len(df)

    if valid_count < 50:
        return {
            'platform': platform,
            'total_records': total_count,
            'valid_records': valid_count,
            'error': f'{platform} için yeterli zaman verisi yok.',
            'data_limitation': True,
            'is_valid': False,
        }

    # IQR ile outlier temizleme
    q1 = df['likes'].quantile(0.25)
    q3 = df['likes'].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr
    lower_bound = max(0, q1 - 1.5 * iqr)

    original_count = len(df)
    df = df[(df['likes'] >= lower_bound) & (df['likes'] <= upper_bound)]
    outliers_removed = original_count - len(df)

    if len(df) < 50:
        return {
            'platform': platform,
            'error': 'Outlier temizleme sonrası yeterli veri kalmadı.',
            'is_valid': False,
        }

    # 5-fold cross validation
    np.random.seed(42)
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
    fold_size = len(df_shuffled) // 5

    improvements = []
    predictions = []

    for fold in range(5):
        test_start = fold * fold_size
        test_end = test_start + fold_size
        test_df = df_shuffled[test_start:test_end]
        train_df = pd.concat([
            df_shuffled[:test_start],
            df_shuffled[test_end:]
        ])

        # Eğitim verisinden en iyi gün-saat (MEAN ile)
        best_combo = train_df.groupby(
            ['day_of_week', 'post_time']
        )['likes'].mean().idxmax()
        best_day, best_hour = best_combo

        # Test verisinde ±2 saatlik pencere (MEAN ile)
        hour_min = max(0, best_hour - 2)
        hour_max = min(23, best_hour + 2)

        predicted_perf = test_df[
            (test_df['day_of_week'] == best_day) &
            (test_df['post_time'] >= hour_min) &
            (test_df['post_time'] <= hour_max)
        ]['likes'].mean()

        overall_mean = test_df['likes'].mean()

        if pd.notna(predicted_perf) and overall_mean > 0:
            improvement = ((predicted_perf - overall_mean) / overall_mean) * 100
            improvements.append(improvement)
            predictions.append({
                'day': int(best_day),
                'hour': int(best_hour),
                'predicted_perf': float(predicted_perf),
                'avg_perf': float(overall_mean),
                'improvement': float(improvement)
            })

    if not improvements:
        return {
            'platform': platform,
            'error': 'Doğrulama hesaplanamadı.',
            'is_valid': False,
        }

    avg_improvement = np.mean(improvements)
    std_improvement = np.std(improvements)
    best_pred = predictions[0]

    return {
        'platform': platform,
        'total_records': total_count,
        'valid_records': valid_count,
        'outliers_removed': outliers_removed,
        'predicted_day': best_pred['day'],
        'predicted_hour': best_pred['hour'],
        'predicted_performance': round(best_pred['predicted_perf'], 2),
        'average_performance': round(best_pred['avg_perf'], 2),
        'improvement_percentage': round(avg_improvement, 2),
        'std_deviation': round(std_improvement, 2),
        'fold_count': len(improvements),
        'all_improvements': [round(i, 2) for i in improvements],
        'is_valid': avg_improvement > 0,
        'method': 'IQR outlier removal + mean-based 5-fold cross validation'
    }


