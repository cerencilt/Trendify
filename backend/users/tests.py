"""
=============================================
TRENDIFY – KULLANICI (USERS) BİRİM TESTLERİ
=============================================
Kapsanan TC'ler: TC01, TC02, TC03, TC04
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

# ─────────────────────────────────────────
# YARDIMCI FONKSİYON
# ─────────────────────────────────────────
def create_test_user(email="test@trendify.com", password="test1234", username="testuser"):
    return User.objects.create_user(
        username=username,
        email=email,
        password=password
    )


# ─────────────────────────────────────────
# TC01 – Geçerli Bilgilerle Giriş
# ─────────────────────────────────────────
class TC01_ValidLogin(TestCase):
    """
    TC01 | Geçerli e-posta ve şifre ile giriş yapılınca
          JWT access & refresh token dönmeli, HTTP 200 alınmalı.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()
        self.url = "/api/auth/login/"

    def test_valid_login_returns_200(self):
        response = self.client.post(self.url, {
            "email": "test@trendify.com",
            "password": "test1234"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_login_returns_access_token(self):
        response = self.client.post(self.url, {
            "email": "test@trendify.com",
            "password": "test1234"
        }, format="json")
        self.assertIn("access", response.data)

    def test_valid_login_returns_refresh_token(self):
        response = self.client.post(self.url, {
            "email": "test@trendify.com",
            "password": "test1234"
        }, format="json")
        self.assertIn("refresh", response.data)


# ─────────────────────────────────────────
# TC02 – Hatalı Kimlik Bilgileri
# ─────────────────────────────────────────
class TC02_InvalidLogin(TestCase):
    """
    TC02 | Yanlış şifre veya e-posta girilince
          HTTP 401 dönmeli, token üretilmemeli.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()
        self.url = "/api/auth/login/"

    def test_wrong_password_returns_401(self):
        response = self.client.post(self.url, {
            "email": "test@trendify.com",
            "password": "yanlis_sifre"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_email_returns_401(self):
        response = self.client.post(self.url, {
            "email": "yanlis@trendify.com",
            "password": "test1234"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_login_no_token(self):
        response = self.client.post(self.url, {
            "email": "test@trendify.com",
            "password": "yanlis_sifre"
        }, format="json")
        self.assertNotIn("access", response.data)


# ─────────────────────────────────────────
# TC03 – Boş Alan Kontrolü
# ─────────────────────────────────────────
class TC03_EmptyFieldLogin(TestCase):
    """
    TC03 | E-posta veya şifre boş bırakılınca
          HTTP 400 dönmeli, hata mesajı içermeli.
    """
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/auth/login/"

    def test_empty_email_returns_400(self):
        response = self.client.post(self.url, {
            "email": "",
            "password": "test1234"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_password_returns_400(self):
        response = self.client.post(self.url, {
            "email": "test@trendify.com",
            "password": ""
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_both_empty_returns_400(self):
        response = self.client.post(self.url, {
            "email": "",
            "password": ""
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────
# TC04 – Yetkisiz Erişim (Token Olmadan)
# ─────────────────────────────────────────
class TC04_UnauthorizedAccess(TestCase):
    """
    TC04 | Token olmadan korumalı endpoint'e erişilince
          HTTP 401 dönmeli, veri gönderilmemeli.
    """
    def setUp(self):
        self.client = APIClient()

    def test_no_token_analysis_list_returns_401(self):
        response = self.client.get("/api/analysis/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_token_recommendations_returns_401(self):
        response = self.client.get("/api/recommendations/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_token_me_endpoint_returns_401(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ─────────────────────────────────────────
# KAYIT (REGISTER) TESTLERİ
# ─────────────────────────────────────────
class RegisterTests(TestCase):
    """
    Kullanıcı kayıt endpoint'i doğrulama testleri.
    """
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/auth/register/"

    def test_valid_register_returns_201(self):
        response = self.client.post(self.url, {
            "username": "yenikullanici",
            "email": "yeni@trendify.com",
            "password": "guclusifre123"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_email_returns_400(self):
        create_test_user(email="varolan@trendify.com", username="varolan")
        response = self.client.post(self.url, {
            "username": "yeni2",
            "email": "varolan@trendify.com",
            "password": "sifre123"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_password_returns_400(self):
        response = self.client.post(self.url, {
            "username": "kisasifre",
            "email": "kisa@trendify.com",
            "password": "abc"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)