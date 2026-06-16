from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAuthenticationTests(TestCase):
    """Kullanıcı kayıt, giriş ve JWT token testleri"""

    def setUp(self):
        """Her test öncesi çalışır - test client'ı hazırlar"""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.me_url = '/api/auth/me/'

        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@trendify.com',
            'password': 'guvenli123'
        }

    def test_tc01_gecerli_kullanici_kaydi(self):
        """TC-01: Geçerli bilgilerle kullanıcı kaydı yapılabilmeli"""
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(email='test@trendify.com').exists()
        )

    def test_tc02_ayni_email_ile_tekrar_kayit(self):
        """TC-02: Aynı email ile ikinci kez kayıt başarısız olmalı"""
        # İlk kullanıcı oluştur
        self.client.post(self.register_url, self.valid_user_data, format='json')

        # Aynı bilgilerle tekrar dene
        response = self.client.post(
            self.register_url,
            self.valid_user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tc03_gecerli_giris_ve_jwt_token(self):
        """TC-03: Doğru bilgilerle giriş JWT token döndürmeli"""
        # Önce kullanıcı oluştur
        self.client.post(self.register_url, self.valid_user_data, format='json')

        # Giriş yap (SimpleJWT email ile çalışır)
        response = self.client.post(
            self.login_url,
            {
                'email': 'test@trendify.com',
                'password': 'guvenli123'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_tc04_hatali_sifre_ile_giris(self):
        """TC-04: Yanlış şifre ile giriş başarısız olmalı"""
        self.client.post(self.register_url, self.valid_user_data, format='json')

        response = self.client.post(
            self.login_url,
            {
                'email': 'test@trendify.com',
                'password': 'yanlissifre'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tc05_korumali_endpoint_tokensiz_erisim(self):
        """TC-05: Token olmadan korumalı uç noktalara erişim engellenmeli"""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tc06_eksik_alan_ile_kayit(self):
        """TC-06: Eksik alanlarla kayıt başarısız olmalı"""
        incomplete_data = {
            'email': 'test@trendify.com'
            # username ve password eksik
        }
        response = self.client.post(
            self.register_url,
            incomplete_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTests(TestCase):
    """Kullanıcı profil bilgisi alma testleri"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='profiluser',
            email='profil@trendify.com',
            password='guvenli123'
        )

    def test_tc07_token_ile_profil_bilgisi_alma(self):
        """TC-07: Geçerli token ile profil bilgisi alınabilmeli"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profil@trendify.com')