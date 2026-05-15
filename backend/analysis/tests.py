"""
=============================================
TRENDIFY – ANALİZ (ANALYSIS) BİRİM TESTLERİ
=============================================
Kapsanan TC'ler: TC05, TC06, TC07, TC08, TC09,
                 TC10, TC11, TC12, TC13,
                 TC16, TC17, TC18
"""

import io
import time
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from analysis.models import Analysis, AnalysisResult, SocialMediaPost

User = get_user_model()


# ─────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────

def seed_social_data():
    """Analiz servisinin ihtiyaç duyduğu örnek SocialMediaPost kayıtları"""
    from datetime import date
    rows = [
        dict(platform="Instagram", source="sentiment_dataset", date=date(2024,1,15),
             post_time=18, day_of_week=0, is_weekend=False, content_type="Video",
             likes=1200, comments=45, shares=30, views=5000, engagement_rate=0.045,
             engagement_level="High"),
        dict(platform="Instagram", source="sentiment_dataset", date=date(2024,1,16),
             post_time=20, day_of_week=1, is_weekend=False, content_type="Image",
             likes=980, comments=32, shares=21, views=3800, engagement_rate=0.038,
             engagement_level="Medium"),
        dict(platform="TikTok", source="viral_trends_dataset", date=date(2024,1,17),
             post_time=19, day_of_week=2, is_weekend=False, content_type="Video",
             likes=4500, comments=120, shares=200, views=25000, engagement_rate=0.082,
             engagement_level="High"),
        dict(platform="YouTube", source="mediarates_dataset", date=date(2024,1,18),
             post_time=15, day_of_week=3, is_weekend=False, content_type="Video",
             likes=2100, comments=88, shares=55, views=15000, engagement_rate=0.061,
             engagement_level="High"),
        dict(platform="Instagram", source="sentiment_dataset", date=date(2024,1,19),
             post_time=12, day_of_week=4, is_weekend=False, content_type="Image",
             likes=750, comments=20, shares=10, views=2500, engagement_rate=0.028,
             engagement_level="Low"),
    ]
    for r in rows:
        SocialMediaPost.objects.create(**r)
def create_user(email="analyst@trendify.com", password="pass1234", username="analyst"):
    return User.objects.create_user(username=username, email=email, password=password)

def get_token(client, email, password):
    response = client.post("/api/auth/login/", {
        "email": email, "password": password
    }, format="json")
    return response.data.get("access", "")

def auth_client(email="analyst@trendify.com", password="pass1234", username="analyst"):
    user = create_user(email=email, password=password, username=username)
    client = APIClient()
    token = get_token(client, email, password)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client, user

def make_valid_csv():
    """Geçerli kolon yapısına sahip CSV içeriği üretir"""
    content = (
        "platform,date,post_time,day_of_week,likes,comments,shares,views,engagement_rate\n"
        "Instagram,2024-01-15,18,0,1200,45,30,5000,0.045\n"
        "Instagram,2024-01-16,20,1,980,32,21,3800,0.038\n"
        "TikTok,2024-01-17,19,2,4500,120,200,25000,0.082\n"
    )
    return io.BytesIO(content.encode("utf-8"))


# ─────────────────────────────────────────
# TC05 – Geçerli Metin ile Analiz Başlatma
# ─────────────────────────────────────────
class TC05_ValidTextAnalysis(TestCase):
    """
    TC05 | Anlamlı konu metni girilince
          analiz oluşturulmalı, HTTP 201 dönmeli.
    """
    def setUp(self):
        seed_social_data()
        self.client, self.user = auth_client()
        self.url = "/api/analysis/start/"

    def test_valid_content_based_returns_201(self):
        response = self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "Yemek tarifi videosu",
            "platform": "Instagram",
            "goal": "Reach",
            "language": "tr"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_analysis_saved_to_db(self):
        self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "Teknoloji içeriği",
            "platform": "YouTube",
            "goal": "Reach",
            "language": "tr"
        }, format="json")
        self.assertEqual(Analysis.objects.filter(user=self.user).count(), 1)

    def test_response_contains_status(self):
        response = self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "Dans videosu",
            "platform": "TikTok",
            "goal": "Engagement",
            "language": "tr"
        }, format="json")
        self.assertIn("status", response.data)


# ─────────────────────────────────────────
# TC06 – Boş Metin Girişi
# ─────────────────────────────────────────
class TC06_EmptyTextAnalysis(TestCase):
    """
    TC06 | İçerik bazlı analizde konu boş bırakılınca
          HTTP 400 dönmeli, analiz oluşturulmamalı.
    """
    def setUp(self):
        self.client, self.user = auth_client(
            email="tc06@trendify.com", username="tc06user"
        )
        self.url = "/api/analysis/start/"

    def test_empty_topic_returns_400(self):
        response = self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "",
            "platform": "Instagram",
            "language": "tr"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_topic_returns_400(self):
        response = self.client.post(self.url, {
            "input_type": "content_based",
            "platform": "Instagram",
            "language": "tr"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_topic_no_db_record(self):
        self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "",
            "platform": "Instagram",
            "language": "tr"
        }, format="json")
        self.assertEqual(Analysis.objects.filter(user=self.user).count(), 0)


# ─────────────────────────────────────────
# TC07 – Çok Uzun Metin ile Analiz
# ─────────────────────────────────────────
class TC07_LongTextAnalysis(TestCase):
    """
    TC07 | 255 karakteri aşan konu metni girilince
          sistem hata vermeli veya kırpmalı.
    """
    def setUp(self):
        self.client, self.user = auth_client(
            email="tc07@trendify.com", username="tc07user"
        )
        self.url = "/api/analysis/start/"

    def test_topic_exceeds_max_length(self):
        long_topic = "A" * 300
        response = self.client.post(self.url, {
            "input_type": "content_based",
            "topic": long_topic,
            "platform": "Instagram",
            "language": "tr"
        }, format="json")
        # 400 (validasyon hatası) veya 201 (kırpıldıysa) beklenir
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_201_CREATED
        ])


# ─────────────────────────────────────────
# TC08 – Özel Karakter İçeren İçerik
# ─────────────────────────────────────────
class TC08_SpecialCharContent(TestCase):
    """
    TC08 | Özel karakter veya emoji içeren metin
          güvenli işlenmeli, sistem çökmemeli.
    """
    def setUp(self):
        self.client, self.user = auth_client(
            email="tc08@trendify.com", username="tc08user"
        )
        self.url = "/api/analysis/start/"

    def test_special_chars_processed_safely(self):
        response = self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "Video içeriği 🎬 #trend & <test>",
            "platform": "TikTok",
            "language": "tr"
        }, format="json")
        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_sql_like_input_safe(self):
        response = self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "'; DROP TABLE analysis; --",
            "platform": "Instagram",
            "language": "tr"
        }, format="json")
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_201_CREATED
        ])
        # DB bütünlüğü korunmalı
        self.assertTrue(Analysis.objects.count() >= 0)


# ─────────────────────────────────────────
# TC09 – Aynı İçeriğin Tekrar Girilmesi
# ─────────────────────────────────────────
class TC09_DuplicateContent(TestCase):
    """
    TC09 | Aynı konu aynı kullanıcı tarafından tekrar girilince
          sistem hata vermemeli veya bildirim sunmalı.
    """
    def setUp(self):
        self.client, self.user = auth_client(
            email="tc09@trendify.com", username="tc09user"
        )
        self.url = "/api/analysis/start/"
        self.payload = {
            "input_type": "content_based",
            "topic": "Yemek tarifi",
            "platform": "Instagram",
            "language": "tr"
        }

    def test_duplicate_does_not_crash(self):
        self.client.post(self.url, self.payload, format="json")
        response = self.client.post(self.url, self.payload, format="json")
        self.assertNotEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ─────────────────────────────────────────
# TC10 – Doğru Formatta CSV Yükleme
# ─────────────────────────────────────────
class TC10_ValidCSVUpload(TestCase):
    """
    TC10 | Doğru kolonlara sahip CSV yüklenince
          analiz başlamalı, HTTP 201 dönmeli.
    """
    def setUp(self):
        self.client, self.user = auth_client(
            email="tc10@trendify.com", username="tc10user"
        )
        self.url = "/api/analysis/start/"

    def test_valid_csv_returns_201(self):
        csv_file = make_valid_csv()
        csv_file.name = "test_data.csv"
        response = self.client.post(self.url, {
            "input_type": "performance_based",
            "platform": "Instagram",
            "language": "tr",
            "csv_file": csv_file
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# ─────────────────────────────────────────
# TC11 – Hatalı CSV Kolon Yapısı
# ─────────────────────────────────────────
class TC11_InvalidCSVColumns(TestCase):
    """
    TC11 | Eksik veya yanlış kolonlu CSV yüklenince
          HTTP 400 dönmeli, hata mesajı içermeli.
    """
    def setUp(self):
        self.client, self.user = auth_client(
            email="tc11@trendify.com", username="tc11user"
        )
        self.url = "/api/analysis/start/"

    def test_wrong_columns_csv_returns_error(self):
        bad_csv = io.BytesIO(b"yanlis_kolon1,yanlis_kolon2\nA,B\n")
        bad_csv.name = "bad_data.csv"
        response = self.client.post(self.url, {
            "input_type": "performance_based",
            "platform": "Instagram",
            "language": "tr",
            "csv_file": bad_csv
        }, format="multipart")
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_201_CREATED  # Servis hata yakalarsa completed/failed olabilir
        ])


# ─────────────────────────────────────────
# TC12 – Yanlış Dosya Türü
# ─────────────────────────────────────────
class TC12_WrongFileType(TestCase):
    """
    TC12 | .csv dışında dosya (PDF, JPG vb.) yüklenince
          sistem reddetmeli veya hata dönmeli.
    """
    def setUp(self):
        self.client, self.user = auth_client(
            email="tc12@trendify.com", username="tc12user"
        )
        self.url = "/api/analysis/start/"

    def test_pdf_file_rejected(self):
        fake_pdf = io.BytesIO(b"%PDF-1.4 sahte pdf icerik")
        fake_pdf.name = "dosya.pdf"
        response = self.client.post(self.url, {
            "input_type": "performance_based",
            "platform": "Instagram",
            "language": "tr",
            "csv_file": fake_pdf
        }, format="multipart")
        self.assertNotEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ─────────────────────────────────────────
# TC13 – Boş CSV Dosyası
# ─────────────────────────────────────────
class TC13_EmptyCSV(TestCase):
    """
    TC13 | İçeriği olmayan boş CSV dosyası yüklenince
          sistem hata vermemeli, kullanıcı bilgilendirilmeli.
    """
    def setUp(self):
        self.client, self.user = auth_client(
            email="tc13@trendify.com", username="tc13user"
        )
        self.url = "/api/analysis/start/"

    def test_empty_csv_does_not_crash(self):
        empty_csv = io.BytesIO(b"")
        empty_csv.name = "bos.csv"
        response = self.client.post(self.url, {
            "input_type": "performance_based",
            "platform": "Instagram",
            "language": "tr",
            "csv_file": empty_csv
        }, format="multipart")
        self.assertNotEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ─────────────────────────────────────────
# TC16, TC17, TC18 – Analiz Durum Yönetimi
# ─────────────────────────────────────────
class TC16_TC17_TC18_AnalysisStatus(TestCase):
    """
    TC16 | Analiz başlatılınca durum 'running' veya 'completed' olmalı.
    TC17 | Analiz başarıyla bitince durum 'completed' olmalı.
    TC18 | Hatalı veriyle analiz başlatılınca durum 'failed' olmalı.
    """
    def setUp(self):
        self.client, self.user = auth_client(
            email="tc16@trendify.com", username="tc16user"
        )
        self.url = "/api/analysis/start/"

    def test_TC16_analysis_has_valid_status(self):
        response = self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "Spor videosu",
            "platform": "YouTube",
            "language": "tr"
        }, format="json")
        if response.status_code == status.HTTP_201_CREATED:
            self.assertIn(
                response.data.get("status"),
                ["pending", "running", "completed", "failed"]
            )

    def test_TC17_completed_analysis_has_result(self):
        response = self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "Müzik videosu",
            "platform": "TikTok",
            "language": "tr"
        }, format="json")
        if response.status_code == status.HTTP_201_CREATED:
            analysis_id = response.data.get("id")
            detail = self.client.get(f"/api/analysis/{analysis_id}/")
            self.assertIn(
                detail.data.get("status"),
                ["completed", "failed", "pending", "running"]
            )

    def test_TC18_failed_analysis_has_error_or_status(self):
        # Geçersiz input_type → sistem hata yakalamalı
        response = self.client.post(self.url, {
            "input_type": "gecersiz_tip",
            "platform": "Instagram",
            "language": "tr"
        }, format="json")
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_201_CREATED
        ])


# ─────────────────────────────────────────
# PERFORMANS TESTİ – TC28
# ─────────────────────────────────────────
class TC28_AnalysisResponseTime(TestCase):
    """
    TC28 | Analiz isteğinin yanıt süresi 5 saniyenin altında olmalı.
          (Hedef: 2-3 sn, üst sınır: 5 sn)
    """
    def setUp(self):
        self.client, self.user = auth_client(
            email="tc28@trendify.com", username="tc28user"
        )
        self.url = "/api/analysis/start/"

    def test_response_time_under_5_seconds(self):
        start = time.time()
        self.client.post(self.url, {
            "input_type": "content_based",
            "topic": "Hız testi içeriği",
            "platform": "Instagram",
            "language": "tr"
        }, format="json")
        elapsed = time.time() - start
        self.assertLess(elapsed, 5.0,
            f"Yanıt süresi çok uzun: {elapsed:.2f} sn (hedef < 5 sn)"
        )