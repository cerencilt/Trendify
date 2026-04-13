from django.db import models
from django.conf import settings
from analysis.models import Analysis


class Recommendation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
        related_name='recommendations',
        null=True,
        blank=True
    )
    platform = models.CharField(max_length=20, null=True, blank=True)
    topic = models.CharField(max_length=255, null=True, blank=True)
    post_time = models.IntegerField(null=True, blank=True)
    best_day = models.CharField(max_length=20, null=True, blank=True)
    hashtags = models.TextField(null=True, blank=True)
    caption = models.TextField(null=True, blank=True)
    music = models.CharField(max_length=255, null=True, blank=True)
    reasoning = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Öneri'
        verbose_name_plural = 'Öneriler'

    def __str__(self):
        return f"{self.user.email} | {self.platform} | {self.created_at}"


class Feedback(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    recommendation = models.OneToOneField(
        Recommendation,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Geri Bildirim'
        verbose_name_plural = 'Geri Bildirimler'

    def __str__(self):
        return f"{self.user.email} | Puan: {self.rating}"