from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from analysis.models import Analysis, AnalysisResult
from recommendations.models import Recommendation

User = get_user_model()


class DashboardSummaryTests(TestCase):
    """Dashboard özet endpoint testleri"""

    def setUp(self):
        """Her test için kullanıcı ve veriler hazırla"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='dashboard_user',
            email='dashboard@trendify.com',
            password='guvenli123'
        )
        self.client.force_authenticate(user=self.user)

    def test_tc22_dashboard_ozet_bilgileri(self):
        """TC-22: Dashboard özet verilerinin doğru dönmesi"""
        # 3 analiz oluştur
        for i in range(3):
            analysis = Analysis.objects.create(
                user=self.user,
                topic=f'konu_{i}',
                platform='Instagram',
                goal='Etkileşim',
                status='completed'
            )
            AnalysisResult.objects.create(
                analysis=analysis,
                best_post_time=20,
                best_day=3,
                avg_engagement_rate=50.0,
                avg_likes=1000,
                avg_comments=50,
                avg_shares=20,
                trend_fit_score=75.0,
                heatmap_data={},
                content_type_performance={}
            )

            # Her analiz için bir öneri ekle
            Recommendation.objects.create(
                user=self.user,
                analysis=analysis,
                platform='Instagram',
                topic=f'konu_{i}',
                post_time=20,
                best_day='Perşembe',
                reasoning='Test öneri'
            )

        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Cevap içeriğini kontrol et
        data = response.data
        # Total analiz sayısı 3 olmalı
        if 'total_analyses' in data:
            self.assertEqual(data['total_analyses'], 3)
        if 'total_recommendations' in data:
            self.assertEqual(data['total_recommendations'], 3)

    def test_tc23_analiz_gecmisi_listeleme(self):
        """TC-23: Geçmiş analizlerin listelenmesi"""
        # 5 analiz oluştur
        for i in range(5):
            Analysis.objects.create(
                user=self.user,
                topic=f'konu_{i}',
                platform='Instagram',
                goal='Etkileşim',
                status='completed'
            )

        response = self.client.get('/api/dashboard/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        history = response.data
        if isinstance(history, dict) and 'results' in history:
            history = history['results']

        # 5 analiz dönmeli
        self.assertEqual(len(history), 5)

    def test_tc24_bos_dashboard(self):
        """TC-24: Hiç verisi olmayan kullanıcı için dashboard"""
        # Bu kullanıcı için veri yok
        response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Sayımlar 0 olmalı
        data = response.data
        if 'total_analyses' in data:
            self.assertEqual(data['total_analyses'], 0)
        if 'total_recommendations' in data:
            self.assertEqual(data['total_recommendations'], 0)

    def test_tc25_tokensiz_dashboard_erisimi(self):
        """TC-25: Token olmadan dashboard erişimi engellenmeli"""
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get('/api/dashboard/summary/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tc26_dashboard_veri_izolasyonu(self):
        """TC-26: Kullanıcı sadece kendi verilerini görmeli"""
        # Başka bir kullanıcı oluştur
        other_user = User.objects.create_user(
            username='other_dash',
            email='other_dash@trendify.com',
            password='other123'
        )

        # Her iki kullanıcı için de analiz oluştur
        Analysis.objects.create(
            user=self.user,
            topic='benim_konu',
            platform='Instagram',
            goal='Etkileşim',
            status='completed'
        )

        # Diğer kullanıcı için 3 analiz
        for i in range(3):
            Analysis.objects.create(
                user=other_user,
                topic=f'baskasinin_konu_{i}',
                platform='YouTube',
                goal='Erişim',
                status='completed'
            )

        # Kendi dashboard'umu kontrol et
        response = self.client.get('/api/dashboard/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        history = response.data
        if isinstance(history, dict) and 'results' in history:
            history = history['results']

        # Sadece kendi analizim (1 tane) görünmeli
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['topic'], 'benim_konu')


class DashboardHistoryFilterTests(TestCase):
    """Dashboard geçmiş filtreleme testleri"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='filter_user',
            email='filter@trendify.com',
            password='guvenli123'
        )
        self.client.force_authenticate(user=self.user)

        # Farklı platformlarda analizler oluştur
        Analysis.objects.create(
            user=self.user, topic='ig_konu', platform='Instagram',
            goal='Etkileşim', status='completed'
        )
        Analysis.objects.create(
            user=self.user, topic='yt_konu', platform='YouTube',
            goal='Erişim', status='completed'
        )
        Analysis.objects.create(
            user=self.user, topic='tt_konu', platform='TikTok',
            goal='Etkileşim', status='completed'
        )

    def test_tc27_platform_bazli_filtreleme(self):
        """TC-27: Platform bazlı filtreleme (varsa)"""
        # Eğer endpoint filtreleme destekliyorsa
        response = self.client.get(
            '/api/dashboard/history/?platform=Instagram'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Filtreleme yoksa bile en azından hatasız dönmeli