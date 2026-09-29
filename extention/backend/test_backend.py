import json
import unittest
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import app, normalize_domain_backend, load_sample_xlsx

class TestScamShieldBackend(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_domain_normalization(self):
        self.assertEqual(normalize_domain_backend("www.example.com"), "example.com")
        self.assertEqual(normalize_domain_backend("example.com/login"), "example.com")
        self.assertEqual(normalize_domain_backend("", "https://www.southbankmosaics.com/about"), "southbankmosaics.com")
        self.assertEqual(normalize_domain_backend("EXAMPLE.XYZ"), "example.xyz")

    def test_sample_xlsx_inactive_warning(self):
        # 1. Inactive company row: southbankmosaics
        payload1 = {
            "url": "https://www.southbankmosaics.com/programs",
            "domain": "southbankmosaics.com"
        }
        res1 = self.client.post("/api/check-url", json=payload1)
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertTrue(data1["found"])
        self.assertEqual(data1["risk_level"], "HIGH")
        self.assertEqual(data1["company_status"], "Inactive")
        self.assertIn("INACTIVE", data1["reason"])

        # 2. Inactive company row: voicefmradio
        payload2 = {
            "url": "https://www.voicefmradio.co.uk",
            "domain": "voicefmradio.co.uk"
        }
        res2 = self.client.post("/api/check-url", json=payload2)
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertTrue(data2["found"])
        self.assertEqual(data2["risk_level"], "HIGH")
        self.assertEqual(data2["company_status"], "Inactive")

    def test_sample_xlsx_active_company(self):
        payload = {
            "url": "https://www.tcs.com/careers",
            "domain": "tcs.com"
        }
        res = self.client.post("/api/check-url", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertFalse(data["found"])
        self.assertTrue(data.get("verified_active"))
        self.assertEqual(data["company_status"], "Active")
        self.assertEqual(data["risk_level"], "LOW")

    def test_threat_feed_suspicious(self):
        payload = {
            "url": "https://google-careers-example.xyz/internship",
            "domain": "google-careers-example.xyz"
        }
        res = self.client.post("/api/check-url", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["found"])
        self.assertEqual(data["risk_level"], "HIGH")

    def test_check_url_no_known_match(self):
        payload = {
            "url": "https://wikipedia.org/wiki/Main_Page",
            "domain": "wikipedia.org"
        }
        res = self.client.post("/api/check-url", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertFalse(data["found"])
        self.assertEqual(data["risk_level"], "UNKNOWN")

    def test_web_routes(self):
        res_home = self.client.get("/")
        self.assertEqual(res_home.status_code, 200)

        res_analyze = self.client.get("/analyze?url=https%3A%2F%2Fsouthbankmosaics.com")
        self.assertEqual(res_analyze.status_code, 200)
        self.assertIn(b"southbankmosaics.com", res_analyze.data)

if __name__ == "__main__":
    unittest.main()
