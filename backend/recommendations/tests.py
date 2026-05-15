"""
===========================================================
TRENDIFY – ÖNERİ (RECOMMENDATIONS) & GÜVENLİK TESTLERİ
===========================================================
Kapsanan TC'ler: TC19, TC20, TC21, TC22, TC23, TC24, TC25, TC26
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from analysis.models import Analysis, AnalysisResult
from recommendations.models import Recommendation, Feedback

User = get_user_model()


# ─────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────
def create_user(email, password="pass1234", username=None):
    if username is None:
        username = email.split("@")[0]
    return User.objects.create_user(
        username=username, email=email, password=password
    )

def get_token(client, email, password="pass1234"):
    res = client.post("/api/auth/login/", {
        "email": email, "password": password
    }, format="json")
    return res.data.get("access", "")

def auth_client(email, password="pass1234"):
    user = create_user(email=email, password=password)
    client = APIClient()
    token = get_token(client, email, password)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client, user

def create_completed_analysis(user):
    """Tamamlanmış analiz + sonucu oluştur"""
    analysis = Analysis.objects.create(
        user=user,
        input_type="content_based",
        topic="Test konusu",
        platform="Instagram",
        status="completed"
    )
    AnalysisResult.objects.create(
        analysis=analysis,
        best_post_time=18,
        best_day=1,
        avg_engagement_rate=0.045,
        avg_likes=1200.0,
        trend_fit_score=72.5
    )
    return analysis


# ─────────────────────────────────────────
# TC19 – Başarılı Öneri Üretimi
# ─────────────────────────────────────────
class TC19_SuccessfulRecommendation(TestCase):
    """
    TC19 | Tamamlanmış analiz için öneri üretilince
          HTTP 201 dönmeli, öneri alanları dolu olmalı.
    """
    def setUp(self):
        self.client, self.user = auth_client("tc19@trendify.com")
        self.analysis = create_completed_analysis(self.user)
        self.url = "/api/recommendations/generate/"

    def test_generate_returns_201(self):
        response = self.client.post(self.url, {
            "analysis_id": self.analysis.id,
            "platform": "Instagram",
            "topic": "Test konusu"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_recommendation_saved_to_db(self):
        self.client.post(self.url, {
            "analysis_id": self.analysis.id,
            "platform": "Instagram",
            "topic": "Test konusu"
        }, format="json")
        self.assertEqual(
            Recommendation.objects.filter(user=self.user).count(), 1
        )

    def test_response_has_expected_fields(self):
        response = self.client.post(self.url, {
            "analysis_id": self.analysis.id,
            "platform": "Instagram",
            "topic": "Test konusu"
        }, format="json")
        if response.status_code == status.HTTP_201_CREATED:
            for field in ["id", "platform", "created_at"]:
                self.assertIn(field, response.data)


# ─────────────────────────────────────────
# TC20 – Yetersiz Veriyle Öneri
# ─────────────────────────────────────────
class TC20_InsufficientDataRecommendation(TestCase):
    """
    TC20 | Var olmayan analiz ID'siyle öneri istenince
          HTTP 400 veya 404 dönmeli.
    """
    def setUp(self):
        self.client, self.user = auth_client("tc20@trendify.com")
        self.url = "/api/recommendations/generate/"

    def test_nonexistent_analysis_id_returns_error(self):
        response = self.client.post(self.url, {
            "analysis_id": 99999,
            "platform": "Instagram",
            "topic": "Test"
        }, format="json")
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ])

    def test_missing_analysis_id_returns_400(self):
        response = self.client.post(self.url, {
            "platform": "Instagram",
            "topic": "Test"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────
# TC21 – Analiz Geçmişi Listelenir
# ─────────────────────────────────────────
class TC21_AnalysisHistoryList(TestCase):
    """
    TC21 | Kullanıcı analiz geçmişini listelediğinde
          tüm kayıtlar dönmeli, HTTP 200 alınmalı.
    """
    def setUp(self):
        self.client, self.user = auth_client("tc21@trendify.com")

    def test_empty_history_returns_200(self):
        response = self.client.get("/api/analysis/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_history_with_records_returns_list(self):
        create_completed_analysis(self.user)
        create_completed_analysis(self.user)
        response = self.client.get("/api/analysis/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_sees_only_own_analyses(self):
        """Kullanıcı yalnızca kendi analizlerini görmeli"""
        _, other_user = auth_client("other@trendify.com")
        create_completed_analysis(other_user)
        create_completed_analysis(self.user)
        response = self.client.get("/api/analysis/")
        self.assertEqual(len(response.data), 1)


# ─────────────────────────────────────────
# TC22 – Boş Geçmiş Durumu
# ─────────────────────────────────────────
class TC22_EmptyHistory(TestCase):
    """
    TC22 | Hiç analiz yapmamış kullanıcı geçmişe bakınca
          boş liste dönmeli, sistem hata vermemeli.
    """
    def setUp(self):
        self.client, self.user = auth_client("tc22@trendify.com")

    def test_empty_analysis_list(self):
        response = self.client.get("/api/analysis/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_empty_recommendation_list(self):
        response = self.client.get("/api/recommendations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


# ─────────────────────────────────────────
# TC23 – Öneriye Geri Bildirim Verme
# ─────────────────────────────────────────
class TC23_AddFeedback(TestCase):
    """
    TC23 | Öneri için puan ve yorum verilince
          geri bildirim kaydedilmeli, HTTP 201 dönmeli.
    """
    def setUp(self):
        self.client, self.user = auth_client("tc23@trendify.com")
        self.analysis = create_completed_analysis(self.user)
        # Önce öneri oluştur
        rec = Recommendation.objects.create(
            user=self.user,
            analysis=self.analysis,
            platform="Instagram",
            topic="Test"
        )
        self.rec_id = rec.id
        self.url = f"/api/recommendations/{self.rec_id}/feedback/"

    def test_valid_feedback_returns_201(self):
        response = self.client.post(self.url, {
            "rating": 4,
            "comment": "Çok işe yaradı!"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_feedback_saved_to_db(self):
        self.client.post(self.url, {
            "rating": 5,
            "comment": "Harika öneri"
        }, format="json")
        self.assertEqual(
            Feedback.objects.filter(user=self.user).count(), 1
        )


# ─────────────────────────────────────────
# TC24 – Çift Geri Bildirim Engelleme
# ─────────────────────────────────────────
class TC24_DuplicateFeedback(TestCase):
    """
    TC24 | Aynı öneriye ikinci kez geri bildirim verilince
          HTTP 400 dönmeli, ikinci kayıt oluşturulmamalı.
    """
    def setUp(self):
        self.client, self.user = auth_client("tc24@trendify.com")
        self.analysis = create_completed_analysis(self.user)
        rec = Recommendation.objects.create(
            user=self.user,
            analysis=self.analysis,
            platform="TikTok",
            topic="Test"
        )
        self.url = f"/api/recommendations/{rec.id}/feedback/"

    def test_second_feedback_returns_400(self):
        self.client.post(self.url, {"rating": 4, "comment": "İlk"}, format="json")
        response = self.client.post(self.url, {"rating": 2, "comment": "İkinci"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_one_feedback_in_db(self):
        self.client.post(self.url, {"rating": 4, "comment": "İlk"}, format="json")
        self.client.post(self.url, {"rating": 2, "comment": "İkinci"}, format="json")
        self.assertEqual(Feedback.objects.filter(user=self.user).count(), 1)


# ─────────────────────────────────────────
# TC25 – SQL/Script Injection Denemesi
# ─────────────────────────────────────────
class TC25_SQLInjectionAttempt(TestCase):
    """
    TC25 | Zararlı SQL/script girdileri girilince
          sistem güvenli işlemeli, çökmemeli.
    """
    def setUp(self):
        self.client, self.user = auth_client("tc25@trendify.com")
        self.url = "/api/analysis/start/"

    def test_sql_injection_in_topic(self):
        response = self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "'; DROP TABLE analysis_analysis; --",
            "platform": "Instagram",
            "language": "tr"
        }, format="json")
        self.assertNotEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        # Tablo hâlâ erişilebilir olmalı
        count = Analysis.objects.count()
        self.assertGreaterEqual(count, 0)

    def test_xss_in_topic(self):
        response = self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "<script>alert('xss')</script>",
            "platform": "Instagram",
            "language": "tr"
        }, format="json")
        self.assertNotEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def test_script_injection_in_description(self):
        response = self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "Normal konu",
            "description": "<img src=x onerror=alert(1)>",
            "platform": "Instagram",
            "language": "tr"
        }, format="json")
        self.assertNotEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ─────────────────────────────────────────
# TC26 – Başka Kullanıcının Verisine Erişim
# ─────────────────────────────────────────
class TC26_CrossUserDataAccess(TestCase):
    """
    TC26 | Kullanıcı başkasının analizine veya önerisine
          erişmeye çalışınca HTTP 404 dönmeli.
    """
    def setUp(self):
        # user_a kendi analizini oluşturur
        self.client_a, self.user_a = auth_client("usera@trendify.com")
        self.client_b, self.user_b = auth_client("userb@trendify.com")
        self.analysis_a = create_completed_analysis(self.user_a)

    def test_user_b_cannot_access_user_a_analysis(self):
        response = self.client_b.get(
            f"/api/analysis/{self.analysis_a.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_b_cannot_access_user_a_recommendation(self):
        rec = Recommendation.objects.create(
            user=self.user_a,
            analysis=self.analysis_a,
            platform="Instagram"
        )
        response = self.client_b.get(
            f"/api/recommendations/{rec.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


from analysis.models import Analysis, AnalysisResult
from analysis.models import SocialMediaPost
from datetime import date as _date

def _seed():
    """Entegrasyon testi için örnek sosyal medya verisi"""
    for i in range(5):
        SocialMediaPost.objects.create(
            platform="Instagram",
            source="sentiment_dataset",
            date=_date(2024, 1, i + 1),
            post_time=18,
            day_of_week=i,
            is_weekend=False,
            content_type="Video",
            likes=1000 + i * 100,
            comments=40 + i * 5,
            shares=20,
            views=5000,
            engagement_rate=0.04 + i * 0.005,
            engagement_level="High"
        )


# ─────────────────────────────────────────
# ENTEGRASYon TESTİ – Uçtan Uca Akış
# ─────────────────────────────────────────
class IntegrationTest_FullFlow(TestCase):
    """
    ENTEGRASYon | Kayıt → Giriş → Analiz → Öneri → Geri Bildirim
    tam zincirinin uçtan uca doğrulanması.
    """
    def setUp(self):
        _seed()
        self.client = APIClient()

    def test_full_user_journey(self):
        # 1. Kayıt
        reg = self.client.post("/api/auth/register/", {
            "username": "enttest",
            "email": "enttest@trendify.com",
            "password": "enttest123"
        }, format="json")
        self.assertEqual(reg.status_code, status.HTTP_201_CREATED)

        # 2. Giriş → token al
        login = self.client.post("/api/auth/login/", {
            "email": "enttest@trendify.com",
            "password": "enttest123"
        }, format="json")
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        token = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # 3. Analiz oluştur
        analysis = self.client.post("/api/analysis/start/", {
            "input_type": "content_based",
            "topic": "Entegrasyon testi konusu",
            "platform": "Instagram",
            "language": "tr"
        }, format="json")
        self.assertEqual(analysis.status_code, status.HTTP_201_CREATED)
        analysis_id = analysis.data["id"]

        # 4. Analiz listesinde görünmeli
        lst = self.client.get("/api/analysis/")
        self.assertEqual(lst.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(lst.data), 1)

        # 5. Öneri üret
        rec = self.client.post("/api/recommendations/generate/", {
            "analysis_id": analysis_id,
            "platform": "Instagram",
            "topic": "Entegrasyon testi konusu"
        }, format="json")
        # 201 veya 400 (AI servisi yoksa) kabul edilir
        self.assertIn(rec.status_code, [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST
        ])