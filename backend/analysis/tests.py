from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from analysis.models import SocialMediaPost, Analysis, AnalysisResult

User = get_user_model()


class AnalysisAPITests(TestCase):
    """Analiz API endpoint'leri için testler"""

    def setUp(self):
        """Her test için kullanıcı, token ve örnek veri hazırla"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='analiz_user',
            email='analiz@trendify.com',
            password='guvenli123'
        )
        self.client.force_authenticate(user=self.user)

        # Test için örnek sosyal medya verisi
        for i in range(60):
            SocialMediaPost.objects.create(
                platform='Instagram',
                source='test',
                post_time=20,
                day_of_week=3,
                content_type='Video',
                likes=100 + i * 10,
                comments=10,
                shares=5,
                views=1000,
                engagement_rate=5.0,
                engagement_level='High'
            )

    def test_tc08_yetkili_analiz_baslatma(self):
        """TC-08: Yetkili kullanıcı analiz başlatabilmeli"""
        data = {
            'input_type': 'content_based',
            'topic': 'yemek',
            'platform': 'Instagram',
            'goal': 'Etkileşim',
            'language': 'tr'
        }
        response = self.client.post('/api/analysis/start/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Analysis.objects.filter(user=self.user, topic='yemek').exists()
        )

    def test_tc09_tokensiz_analiz_baslatma(self):
        """TC-09: Token olmadan analiz başlatılamamalı"""
        unauthenticated_client = APIClient()
        data = {
            'input_type': 'content_based',
            'topic': 'yemek',
            'platform': 'Instagram',
            'goal': 'Etkileşim'
        }
        response = unauthenticated_client.post(
            '/api/analysis/start/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tc10_analiz_sonuclarinin_hesaplanmasi(self):
        """TC-10: Analiz başlatıldığında sonuç kaydı doğru oluşmalı"""
        data = {
            'input_type': 'content_based',
            'topic': 'moda',
            'platform': 'Instagram',
            'goal': 'Etkileşim',
            'language': 'tr'
        }
        response = self.client.post('/api/analysis/start/', data, format='json')

        analysis_id = response.data['id']
        analysis = Analysis.objects.get(id=analysis_id)

        # Sonuç kaydı oluştu mu?
        self.assertTrue(hasattr(analysis, 'result'))
        result = analysis.result

        # Best post time 0-23, best day 0-6 arasında olmalı
        if result.best_post_time is not None:
            self.assertTrue(0 <= result.best_post_time <= 23)
        if result.best_day is not None:
            self.assertTrue(0 <= result.best_day <= 6)

    def test_tc11_kullanici_kendi_analizlerini_gorur(self):
        """TC-11: Kullanıcı sadece kendi analizlerini görebilmeli"""
        # Başka bir kullanıcı oluştur
        other_user = User.objects.create_user(
            username='other_user',
            email='other@trendify.com',
            password='other123'
        )

        # Başka kullanıcının analizini oluştur
        Analysis.objects.create(
            user=other_user,
            topic='spor',
            platform='YouTube',
            goal='Erişim',
            status='completed'
        )

        # Kendi analizimi oluştur
        Analysis.objects.create(
            user=self.user,
            topic='yemek',
            platform='Instagram',
            goal='Etkileşim',
            status='completed'
        )

        # Listele - sadece kendi analizim dönmeli
        response = self.client.get('/api/analysis/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Sadece 1 analiz görünmeli (kendiminki)
        analizler = response.data
        # Eğer paginated cevap dönüyorsa
        if isinstance(analizler, dict) and 'results' in analizler:
            analizler = analizler['results']

        self.assertEqual(len(analizler), 1)
        self.assertEqual(analizler[0]['topic'], 'yemek')

    def test_tc12_eksik_parametrelerle_analiz(self):
        """TC-12: Eksik parametrelerle analiz başlatılamamalı"""
        # Topic eksik
        data = {
            'input_type': 'content_based',
            'platform': 'Instagram',
            'goal': 'Etkileşim'
        }
        response = self.client.post('/api/analysis/start/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tc13_model_dogrulama_kfold(self):
        """TC-13: k-Fold cross validation endpoint'i doğru çalışmalı"""
        response = self.client.get(
            '/api/analysis/validate/?platform=Instagram'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Doğrulama sonucunda olması gereken alanlar
        # (Yeterli veri varsa bu alanlar dönmeli)
        if 'improvement_percentage' in response.data:
            self.assertIn('fold_count', response.data)
            self.assertIn('predicted_day', response.data)
            self.assertIn('predicted_hour', response.data)
            self.assertIn('method', response.data)


class SocialMediaPostModelTests(TestCase):
    """SocialMediaPost modeli için birim testler"""

    def test_tc14_post_olusturma(self):
        """TC-14: SocialMediaPost modelinin doğru oluşturulması"""
        post = SocialMediaPost.objects.create(
            platform='Instagram',
            source='test',
            post_time=20,
            day_of_week=4,
            content_type='Video',
            likes=1000,
            comments=50,
            shares=20,
            views=10000,
            engagement_rate=10.7,
            engagement_level='High'
        )

        self.assertEqual(post.platform, 'Instagram')
        self.assertEqual(post.likes, 1000)
        self.assertTrue(0 <= post.post_time <= 23)
        self.assertTrue(0 <= post.day_of_week <= 6)