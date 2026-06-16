from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from analysis.models import Analysis, AnalysisResult
from recommendations.models import Recommendation, Feedback
from unittest.mock import patch

User = get_user_model()


class RecommendationAPITests(TestCase):
    """Öneri API endpoint'leri için testler"""

    def setUp(self):
        """Her test için kullanıcı, analiz ve token hazırla"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='oneri_user',
            email='oneri@trendify.com',
            password='guvenli123'
        )
        self.client.force_authenticate(user=self.user)

        # Tamamlanmış analiz oluştur
        self.analysis = Analysis.objects.create(
            user=self.user,
            topic='yemek',
            platform='Instagram',
            goal='Etkileşim',
            status='completed'
        )

        # Analiz sonucu oluştur
        AnalysisResult.objects.create(
            analysis=self.analysis,
            best_post_time=22,
            best_day=3,
            avg_engagement_rate=65.3,
            avg_likes=10000,
            avg_comments=500,
            avg_shares=200,
            trend_fit_score=85.0,
            heatmap_data={},
            content_type_performance={'Video': 250000}
        )

    @patch('recommendations.services._call_trendify_ai')
    def test_tc15_gecerli_analiz_ile_oneri(self, mock_ai):
        """TC-15: Geçerli analiz ile öneri üretilebilmeli"""
        mock_ai.return_value = "Test öneri cevabı"

        data = {
            'analysis_id': self.analysis.id,
            'platform': 'Instagram',
            'topic': 'yemek'
        }
        response = self.client.post(
            '/api/recommendations/generate/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Recommendation.objects.filter(analysis=self.analysis).exists()
        )

    def test_tc16_olmayan_analiz_ile_oneri(self):
        """TC-16: Geçersiz analysis_id ile öneri üretilememeli"""
        data = {
            'analysis_id': 9999,  # Olmayan ID
            'platform': 'Instagram',
            'topic': 'yemek'
        }
        response = self.client.post(
            '/api/recommendations/generate/',
            data,
            format='json'
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]
        )

    @patch('recommendations.services._call_trendify_ai')
    def test_tc17_baska_kullanicinin_analizi(self, mock_ai):
        """TC-17: Başka kullanıcının analizi ile öneri üretilememeli"""
        mock_ai.return_value = "Test cevabı"

        # Başka bir kullanıcı oluştur
        other_user = User.objects.create_user(
            username='other_user',
            email='other@trendify.com',
            password='other123'
        )
        other_analysis = Analysis.objects.create(
            user=other_user,
            topic='spor',
            platform='YouTube',
            goal='Erişim',
            status='completed'
        )
        AnalysisResult.objects.create(
            analysis=other_analysis,
            best_post_time=10,
            best_day=1,
            avg_engagement_rate=50.0,
            avg_likes=5000,
            avg_comments=100,
            avg_shares=50,
            trend_fit_score=70.0,
            heatmap_data={},
            content_type_performance={}
        )

        # other_user'ın analiziyle öneri üretmeye çalış
        data = {
            'analysis_id': other_analysis.id,
            'platform': 'YouTube',
            'topic': 'spor'
        }
        response = self.client.post(
            '/api/recommendations/generate/',
            data,
            format='json'
        )
        # 400 veya 404 dönmeli (erişim yok)
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]
        )

    def test_tc18_oneri_gecmisi_listeleme(self):
        """TC-18: Kullanıcı kendi öneri geçmişini görebilmeli"""
        # İki öneri oluştur
        Recommendation.objects.create(
            user=self.user,
            analysis=self.analysis,
            platform='Instagram',
            topic='yemek',
            post_time=22,
            best_day='Perşembe',
            reasoning='Test öneri 1'
        )
        Recommendation.objects.create(
            user=self.user,
            analysis=self.analysis,
            platform='Instagram',
            topic='moda',
            post_time=20,
            best_day='Cuma',
            reasoning='Test öneri 2'
        )

        response = self.client.get('/api/recommendations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        oneriler = response.data
        if isinstance(oneriler, dict) and 'results' in oneriler:
            oneriler = oneriler['results']

        self.assertEqual(len(oneriler), 2)

    def test_tc19_oneriye_geri_bildirim(self):
        """TC-19: Öneriye geri bildirim verilebilmeli"""
        recommendation = Recommendation.objects.create(
            user=self.user,
            analysis=self.analysis,
            platform='Instagram',
            topic='yemek',
            post_time=22,
            best_day='Perşembe',
            reasoning='Test öneri'
        )

        feedback_data = {
            'rating': 5,
            'comment': 'Çok faydalı bir öneri'
        }
        response = self.client.post(
            f'/api/recommendations/{recommendation.id}/feedback/',
            feedback_data,
            format='json'
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_201_CREATED]
        )

    def test_tc20_tokensiz_oneri_uretme(self):
        """TC-20: Token olmadan öneri üretilememeli"""
        unauthenticated_client = APIClient()
        data = {
            'analysis_id': self.analysis.id,
            'platform': 'Instagram',
            'topic': 'yemek'
        }
        response = unauthenticated_client.post(
            '/api/recommendations/generate/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RecommendationModelTests(TestCase):
    """Recommendation modeli için birim testler"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='model_user',
            email='model@trendify.com',
            password='guvenli123'
        )
        self.analysis = Analysis.objects.create(
            user=self.user,
            topic='test',
            platform='Instagram',
            goal='Etkileşim',
            status='completed'
        )

    def test_tc21_recommendation_olusturma(self):
        """TC-21: Recommendation modelinin doğru oluşturulması"""
        rec = Recommendation.objects.create(
            user=self.user,
            analysis=self.analysis,
            platform='Instagram',
            topic='yemek',
            post_time=22,
            best_day='Perşembe',
            reasoning='Test öneri içeriği'
        )

        self.assertEqual(rec.platform, 'Instagram')
        self.assertEqual(rec.post_time, 22)
        self.assertEqual(rec.user, self.user)