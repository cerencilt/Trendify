from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch
from analysis.models import Analysis, AnalysisResult, SocialMediaPost
from recommendations.models import Recommendation

User = get_user_model()


class TamKullaniciAkisiTest(TestCase):
    """Uçtan uca tam kullanıcı akışı testleri"""

    def setUp(self):
        """Test verileri hazırla"""
        self.client = APIClient()

        # Test için sosyal medya verisi
        for i in range(60):
            SocialMediaPost.objects.create(
                platform='Instagram',
                source='test',
                post_time=20 + (i % 4),
                day_of_week=i % 7,
                content_type='Video',
                likes=100 + i * 5,
                comments=10,
                shares=5,
                views=1000,
                engagement_rate=5.0,
                engagement_level='High'
            )

    @patch('recommendations.services._call_trendify_ai')
    def test_tc34_tam_kullanici_akisi(self, mock_ai):
        """TC-34: Kayıt → Giriş → Analiz → Öneri → Dashboard akışı"""
        mock_ai.return_value = "Test AI cevabı"

        # 1. ADIM: Kullanıcı kaydı
        register_response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'tamakis',
                'email': 'tamakis@trendify.com',
                'password': 'guvenli123'
            },
            format='json'
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        # 2. ADIM: Giriş yapma
        login_response = self.client.post(
            '/api/auth/login/',
            {
                'email': 'tamakis@trendify.com',
                'password': 'guvenli123'
            },
            format='json'
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data['access']

        # Token'ı header'a ekle
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 3. ADIM: Analiz başlatma
        analysis_response = self.client.post(
            '/api/analysis/start/',
            {
                'input_type': 'content_based',
                'topic': 'yemek',
                'platform': 'Instagram',
                'goal': 'Etkileşim',
                'language': 'tr'
            },
            format='json'
        )
        self.assertEqual(analysis_response.status_code, status.HTTP_201_CREATED)
        analysis_id = analysis_response.data['id']

        # 4. ADIM: Öneri üretme
        recommendation_response = self.client.post(
            '/api/recommendations/generate/',
            {
                'analysis_id': analysis_id,
                'platform': 'Instagram',
                'topic': 'yemek'
            },
            format='json'
        )
        self.assertEqual(
            recommendation_response.status_code,
            status.HTTP_201_CREATED
        )

        # 5. ADIM: Dashboard kontrolü
        dashboard_response = self.client.get('/api/dashboard/summary/')
        self.assertEqual(dashboard_response.status_code, status.HTTP_200_OK)

        # Akışın sonunda 1 analiz ve 1 öneri olmalı
        dashboard_data = dashboard_response.data
        if 'total_analyses' in dashboard_data:
            self.assertGreaterEqual(dashboard_data['total_analyses'], 1)


class TokenYenilemeTests(TestCase):
    """JWT token yenileme entegrasyon testleri"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='token_user',
            email='token@trendify.com',
            password='guvenli123'
        )

    def test_tc35_token_yenileme_akisi(self):
        """TC-35: Refresh token ile yeni access token alma"""
        # 1. Giriş yap ve refresh token al
        login_response = self.client.post(
            '/api/auth/login/',
            {
                'email': 'token@trendify.com',
                'password': 'guvenli123'
            },
            format='json'
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        refresh_token = login_response.data['refresh']

        # 2. Refresh ile yeni access token al
        refresh_response = self.client.post(
            '/api/auth/token/refresh/',
            {'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

        # 3. Yeni access token ile korumalı endpoint'e erişim
        new_access = refresh_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access}')

        me_response = self.client.get('/api/auth/me/')
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)


class AnalizOneriGeriBildirimAkisiTests(TestCase):
    """Analiz → Öneri → Geri Bildirim zincirleme akışı"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='zincir_user',
            email='zincir@trendify.com',
            password='guvenli123'
        )
        self.client.force_authenticate(user=self.user)

    @patch('recommendations.services._call_trendify_ai')
    def test_tc36_analiz_oneri_geribildirim(self, mock_ai):
        """TC-36: Analiz → Öneri → Geri Bildirim zincirleme akışı"""
        mock_ai.return_value = "Test öneri"

        # 1. Analiz oluştur
        analysis = Analysis.objects.create(
            user=self.user,
            topic='moda',
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
            trend_fit_score=80.0,
            heatmap_data={},
            content_type_performance={'Video': 1000}
        )

        # 2. Öneri üret
        oneri_response = self.client.post(
            '/api/recommendations/generate/',
            {
                'analysis_id': analysis.id,
                'platform': 'Instagram',
                'topic': 'moda'
            },
            format='json'
        )
        self.assertEqual(oneri_response.status_code, status.HTTP_201_CREATED)
        oneri_id = oneri_response.data['id']

        # 3. Geri bildirim ver
        feedback_response = self.client.post(
            f'/api/recommendations/{oneri_id}/feedback/',
            {
                'rating': 5,
                'comment': 'Çok faydalı oldu'
            },
            format='json'
        )
        self.assertIn(
            feedback_response.status_code,
            [status.HTTP_200_OK, status.HTTP_201_CREATED]
        )


class CokluKullaniciIzolasyonuTests(TestCase):
    """Çoklu kullanıcı veri izolasyon testleri"""

    def test_tc37_coklu_kullanici_veri_izolasyonu(self):
        """TC-37: İki farklı kullanıcının verisi birbirinden izole olmalı"""
        # İki kullanıcı oluştur
        kullanici_a = User.objects.create_user(
            username='kullanici_a',
            email='a@trendify.com',
            password='sifre123'
        )
        kullanici_b = User.objects.create_user(
            username='kullanici_b',
            email='b@trendify.com',
            password='sifre123'
        )

        # Her kullanıcı için analizler oluştur
        Analysis.objects.create(
            user=kullanici_a, topic='a_konu', platform='Instagram',
            goal='Etkileşim', status='completed'
        )
        Analysis.objects.create(
            user=kullanici_b, topic='b_konu', platform='YouTube',
            goal='Erişim', status='completed'
        )
        Analysis.objects.create(
            user=kullanici_b, topic='b_konu2', platform='TikTok',
            goal='Etkileşim', status='completed'
        )

        # Kullanıcı A ile giriş yap
        client_a = APIClient()
        client_a.force_authenticate(user=kullanici_a)

        # A sadece kendi analizini görmeli
        response_a = client_a.get('/api/analysis/')
        analizler_a = response_a.data
        if isinstance(analizler_a, dict) and 'results' in analizler_a:
            analizler_a = analizler_a['results']
        self.assertEqual(len(analizler_a), 1)
        self.assertEqual(analizler_a[0]['topic'], 'a_konu')

        # Kullanıcı B ile giriş yap
        client_b = APIClient()
        client_b.force_authenticate(user=kullanici_b)

        # B kendi 2 analizini görmeli
        response_b = client_b.get('/api/analysis/')
        analizler_b = response_b.data
        if isinstance(analizler_b, dict) and 'results' in analizler_b:
            analizler_b = analizler_b['results']
        self.assertEqual(len(analizler_b), 2)


class EsZamanliAnalizTests(TestCase):
    """Eş zamanlı analiz performans testleri"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='perf_user',
            email='perf@trendify.com',
            password='guvenli123'
        )
        self.client.force_authenticate(user=self.user)

        # Test verisi
        for i in range(50):
            SocialMediaPost.objects.create(
                platform='Instagram',
                source='test',
                post_time=20,
                day_of_week=3,
                content_type='Video',
                likes=100 + i * 5,
                comments=10,
                shares=5,
                views=1000,
                engagement_rate=5.0,
                engagement_level='High'
            )

    def test_tc38_es_zamanli_analiz_isleme(self):
        """TC-38: Birden fazla analiz başarıyla işlenmeli"""
        # 5 ayrı analiz başlat
        for i in range(5):
            response = self.client.post(
                '/api/analysis/start/',
                {
                    'input_type': 'content_based',
                    'topic': f'konu_{i}',
                    'platform': 'Instagram',
                    'goal': 'Etkileşim',
                    'language': 'tr'
                },
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 5 analiz oluşturuldu mu?
        toplam_analiz = Analysis.objects.filter(user=self.user).count()
        self.assertEqual(toplam_analiz, 5)