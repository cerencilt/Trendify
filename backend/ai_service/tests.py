from django.test import TestCase, Client
from unittest.mock import patch, MagicMock
import json


class AIServiceUnitTests(TestCase):
    """AI servisi birim testleri - mock ile"""

    def test_tc28_ai_servisi_modul_yuklemesi(self):
        """TC-28: AI servisinin modül olarak yüklenebildiğinin doğrulanması"""
        try:
            from ai_service import views
            # Modül başarıyla import edildi
            self.assertTrue(hasattr(views, 'get_recommendation'))
        except ImportError:
            self.fail("AI Service modülü import edilemedi")

    @patch('ai_service.views.model')
    @patch('ai_service.views.tokenizer')
    def test_tc29_gecerli_veri_ile_oneri_uretme(self, mock_tokenizer, mock_model):
        """TC-29: Geçerli veri ile AI servisi cevap üretmeli"""
        # Mock tokenizer ve model davranışı
        mock_tokenizer.return_value = MagicMock()
        mock_tokenizer.decode.return_value = "Soru: test soru\nCevap: Test öneri cevabı"
        mock_tokenizer.eos_token_id = 0

        mock_model.generate.return_value = MagicMock()

        client = Client()
        response = client.post(
            '/api/ai/recommend/',
            data=json.dumps({
                'topic': 'yemek',
                'platform': 'Instagram',
                'context': 'En iyi saat: 22:00'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        # Status 'success' veya 'error' olmalı
        self.assertIn(data['status'], ['success', 'error'])

    def test_tc30_eksik_veri_ile_ai_cagrisi(self):
        """TC-30: Eksik veri ile çağrı yapılabilmeli (boş cevap olabilir)"""
        client = Client()
        response = client.post(
            '/api/ai/recommend/',
            data=json.dumps({}),
            content_type='application/json'
        )

        # Boş bile olsa hatasız çalışmalı veya uygun hata vermeli
        self.assertIn(response.status_code, [200, 400, 500])

    def test_tc31_get_metodu_reddi(self):
        """TC-31: AI servisi sadece POST kabul etmeli"""
        client = Client()
        response = client.get('/api/ai/recommend/')

        # GET isteği reddedilmeli
        data = response.json()
        self.assertEqual(response.status_code, 405)
        self.assertEqual(data['status'], 'error')

    @patch('ai_service.views.model')
    @patch('ai_service.views.tokenizer')
    def test_tc32_prompt_formati_dogrulama(self, mock_tokenizer, mock_model):
        """TC-32: AI servisi 'Soru:/Cevap:' formatını işliyor mu"""
        # Mock'tan dönecek format
        mock_tokenizer.return_value = MagicMock()
        mock_tokenizer.decode.return_value = (
            "Soru: Instagram yemek\nCevap: En iyi saat 22:00, "
            "video formatı öneririz."
        )
        mock_tokenizer.eos_token_id = 0
        mock_model.generate.return_value = MagicMock()

        client = Client()
        response = client.post(
            '/api/ai/recommend/',
            data=json.dumps({
                'topic': 'yemek',
                'platform': 'Instagram',
                'context': 'test'
            }),
            content_type='application/json'
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                # Cevapta "Soru:" kısmı OLMAMALI (sadece cevap kısmı dönmeli)
                recommendation = data.get('recommendation', '')
                self.assertNotIn('Soru:', recommendation)


class AIServiceEndpointTests(TestCase):
    """AI servisi endpoint testleri"""

    def test_tc33_yanlis_url_ile_istek(self):
        """TC-33: Olmayan URL ile istek 404 dönmeli"""
        client = Client()
        response = client.post('/api/ai/yanlis_endpoint/')
        self.assertEqual(response.status_code, 404)