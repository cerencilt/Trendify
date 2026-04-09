from django.db import models
from django.conf import settings


class SocialMediaPost(models.Model):
    """Kaggle veri setinden gelen ham sosyal medya verisi"""

    PLATFORM_CHOICES = [
        ('Instagram', 'Instagram'),
        ('TikTok', 'TikTok'),
        ('YouTube', 'YouTube'),
        ('Twitter', 'Twitter'),
        ('Facebook', 'Facebook'),
        ('Unknown', 'Unknown'),
    ]

    CONTENT_TYPE_CHOICES = [
        ('Video', 'Video'),
        ('Image', 'Image'),
        ('Text', 'Text'),
        ('Live', 'Live'),
    ]

    ENGAGEMENT_LEVEL_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    SOURCE_CHOICES = [
        ('sentiment_dataset', 'Sentiment Dataset'),
        ('mediarates_dataset', 'Media Rates Dataset'),
        ('viral_trends_dataset', 'Viral Trends Dataset'),
    ]

    # Platform bilgisi
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES)

    # Zaman bilgisi
    date = models.DateField(null=True, blank=True)
    post_time = models.IntegerField(null=True, blank=True)  # 0-23 arası saat
    day_of_week = models.IntegerField(null=True, blank=True)  # 0=Pzt, 6=Paz
    is_weekend = models.BooleanField(default=False)

    # İçerik bilgisi
    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPE_CHOICES,
        null=True,
        blank=True
    )
    hashtags = models.TextField(null=True, blank=True)

    # Etkileşim metrikleri
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(null=True, blank=True)
    shares = models.IntegerField(default=0)
    views = models.BigIntegerField(null=True, blank=True)
    engagement_rate = models.FloatField(null=True, blank=True)
    engagement_level = models.CharField(
        max_length=10,
        choices=ENGAGEMENT_LEVEL_CHOICES,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-post_time']
        verbose_name = 'Sosyal Medya Gönderisi'
        verbose_name_plural = 'Sosyal Medya Gönderileri'

    def __str__(self):
        return f"{self.platform} | {self.date} | {self.engagement_level}"


class Analysis(models.Model):
    """Kullanıcının başlattığı analiz süreci"""

    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('running', 'Çalışıyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Hata'),
    ]

    INPUT_TYPE_CHOICES = [
        ('content_based', 'İçerik Bazlı'),
        ('performance_based', 'Performans Bazlı'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analyses'
    )

    # Girdi bilgisi
    input_type = models.CharField(max_length=20, choices=INPUT_TYPE_CHOICES)
    topic = models.CharField(max_length=255, null=True, blank=True)
    platform = models.CharField(max_length=20, null=True, blank=True)
    goal = models.CharField(max_length=100, null=True, blank=True)
    language = models.CharField(max_length=10, default='tr')
    description = models.TextField(null=True, blank=True)

    # CSV yükleme
    csv_file = models.FileField(upload_to='uploads/csv/', null=True, blank=True)

    # Durum
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Analiz'
        verbose_name_plural = 'Analizler'

    def __str__(self):
        return f"{self.user.email} | {self.input_type} | {self.status}"


class AnalysisResult(models.Model):
    """Analiz sonuçları"""

    analysis = models.OneToOneField(
        Analysis,
        on_delete=models.CASCADE,
        related_name='result'
    )

    # En iyi paylaşım zamanı
    best_post_time = models.IntegerField(null=True, blank=True)  # saat (0-23)
    best_day = models.IntegerField(null=True, blank=True)  # 0-6

    # Ortalama metrikler
    avg_engagement_rate = models.FloatField(null=True, blank=True)
    avg_likes = models.FloatField(null=True, blank=True)
    avg_comments = models.FloatField(null=True, blank=True)
    avg_shares = models.FloatField(null=True, blank=True)

    # Trend skoru
    trend_fit_score = models.FloatField(null=True, blank=True)  # 0-100

    # Isı haritası verisi JSON olarak
    heatmap_data = models.JSONField(null=True, blank=True)

    # İçerik türü performansı JSON olarak
    content_type_performance = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Analiz Sonucu'
        verbose_name_plural = 'Analiz Sonuçları'

    def __str__(self):
        return f"Sonuç → {self.analysis}"