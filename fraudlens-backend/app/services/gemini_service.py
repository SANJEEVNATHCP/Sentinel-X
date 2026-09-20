"""
FraudLens AI - Gemini AI Explanation & Extraction Service
Integrates Google Gemini for document extraction, attack pattern recognition, and concise summaries.
Follows principle: Gemini extracts & explains; Backend verifies facts.
"""

import json
from typing import Dict, Any, Optional, List
from app.config import settings
from app.logging_config import logger

class GeminiService:
    @staticmethod
    def is_configured() -> bool:
        return bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 5)

    @classmethod
    def extract_offer_letter_data(cls, document_text: str) -> Dict[str, Any]:
        """
        Uses Gemini to extract structured job offer fields from OCR/text.
        Falls back to regex-based extraction if API key is not present.
        """
        if cls.is_configured():
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.GEMINI_MODEL)

                prompt = (
                    "You are a specialized document information extractor. Extract the following fields from the "
                    "employment document text into valid JSON with keys: 'company_name', 'company_website', "
                    "'recruiter_name', 'recruiter_email', 'job_role', 'salary', 'offer_date'. "
                    "Do not make any judgments about legitimacy. Return only JSON.\n\n"
                    f"Document Text:\n{document_text[:4000]}"
                )
                response = model.generate_content(prompt)
                clean_txt = response.text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_txt)
            except Exception as e:
                logger.warning(f"Gemini extraction fallback triggered: {str(e)}")

        # Rule-based fallback extraction
        import re
        company_match = re.search(r"(?:at|for|with)\s+([A-Z][a-zA-Z0-9\s&]{2,30}(?:Limited|Ltd|Pvt|Technologies|Inc))", document_text)
        email_match = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", document_text)
        salary_match = re.search(r"(?:₹|\$|INR|salary|ctc|compensation)[:\s]*([0-9,\.]+\s*(?:LPA|lac|per annum|USD)?)", document_text, re.IGNORECASE)
        role_match = re.search(r"(?:role|position|designation)[:\s]*([A-Za-z\s]{3,30})", document_text, re.IGNORECASE)

        return {
            "company_name": company_match.group(1).strip() if company_match else None,
            "company_website": None,
            "recruiter_name": None,
            "recruiter_email": email_match.group(1) if email_match else None,
            "job_role": role_match.group(1).strip() if role_match else "Software Engineer",
            "salary": salary_match.group(1).strip() if salary_match else None,
            "offer_date": None
        }

    @classmethod
    def generate_investigation_summary(
        cls,
        analysis_type: str,
        risk_score: float,
        risk_level: str,
        evidence: List[Dict[str, Any]],
        recommendations: List[str]
    ) -> str:
        """
        Generates a concise, explainable human summary of an investigation.
        Gemini receives only verified derived evidence, never raw private datasets.
        """
        evidence_snippets = [f"- {e.get('signal')}: {e.get('explanation')}" for e in evidence[:5]]
        evidence_text = "\n".join(evidence_snippets)

        if cls.is_configured():
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.GEMINI_MODEL)

                prompt = (
                    f"You are the FraudLens AI cybersecurity explanation agent. "
                    f"Write a concise 2-3 sentence executive explanation for a {analysis_type} investigation.\n"
                    f"Risk Score: {risk_score}/100 ({risk_level})\n"
                    f"Observed Evidence:\n{evidence_text}\n"
                    f"Recommendations:\n{'; '.join(recommendations)}\n\n"
                    f"Explain what was detected, why it matters, and the primary action. Do not sound robotic."
                )
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini summary fallback triggered: {str(e)}")

        # Deterministic explainable summary fallback
        if risk_level == "HIGH_RISK":
            return (
                f"FraudLens identified critical risk factors with a score of {risk_score}/100. "
                f"Primary indicators include contradictory entity records or high-severity behavioral deviations. "
                f"Immediate caution is advised before proceeding with any financial transactions."
            )
        elif risk_level == "SUSPICIOUS":
            return (
                f"FraudLens detected multiple warning signals resulting in a suspicious score of {risk_score}/100. "
                f"Several observed attributes fail standard verification checks. Manual verification is recommended."
            )
        elif risk_level == "MODERATE":
            return (
                f"Investigation yielded a moderate risk score of {risk_score}/100. While no active exploit was confirmed, "
                f"certain verification signals require additional confirmation."
            )
        else:
            return (
                f"Analysis completed with a low risk rating of {risk_score}/100. All audited parameters conform to "
                f"verified baselines and authoritative corporate catalogs."
            )

    @classmethod
    def analyze_images_for_anomalies(
        cls,
        image_paths: List[str],
        context_text: Optional[str] = None,
        custom_api_key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Uses Google Gemini multimodal vision to detect visual tampering, fraudulent claims,
        advance fee demands, OTP elicitation, and suspicious indicators in up to 3 images.
        """
        import os
        api_key = custom_api_key or settings.GEMINI_API_KEY
        if not api_key or len(api_key.strip()) < 5:
            return None

        try:
            from PIL import Image
            pil_images = []
            for p in image_paths[:3]:
                if os.path.exists(p):
                    try:
                        pil_images.append(Image.open(p).convert("RGB"))
                    except Exception as img_err:
                        logger.warning(f"Failed to load image {p} for Gemini vision: {img_err}")

            if not pil_images:
                return None

            prompt = (
                "You are an expert fraud forensics and cybersecurity AI analyzer for FraudLens AI.\n"
                "Examine the provided screenshot(s) / transaction proof(s) / chat messages (up to 3 images) thoroughly.\n"
                "Analyze for all forms of fraud, deception, and visual/behavioral anomalies:\n"
                "1. Behavioral & Social Engineering: Advance fee demands (registration fee, security deposit, processing charge), "
                "artificial urgency pressure (threats of account blocking, arrest, immediate action required), "
                "OTP / credential harvesting (requesting OTPs, passwords, PINs), fake job offers, impersonation of official bank/support staff.\n"
                "2. Visual & Digital Document Tampering: Mismatched fonts, edited numbers/balances, fake bank receipt templates, "
                "forged UPI transaction confirmation, blurred or spliced text regions, fake checkmarks or verification badges.\n"
                "3. Communication Identifiers: Suspicious URLs, personal email domains (@gmail, @yahoo) used for enterprise support, "
                "personal UPI VPA handles (e.g. name@okaxis) demanding business payments.\n"
                "4. Offer Legitimacy Classification: Determine whether the document, message, or transaction proof represents a 'TRUSTED OFFER' "
                "(legitimate employment or payment proof, official corporate domain, standard terms, no advance fees) or an 'UNTRUSTED OFFER' "
                "(advance fee scam, fraudulent recruiter, fake payment screenshot, phishing, lottery/prize scam, credential harvesting).\n"
                f"User context / description: {context_text or 'None provided'}\n\n"
                "Return ONLY a valid JSON object (no markdown, no backticks) matching this exact format:\n"
                "{\n"
                '  "offer_verdict": "<TRUSTED OFFER | UNTRUSTED OFFER>",\n'
                '  "offer_verdict_reason": "<Clear forensic explanation of why this is a TRUSTED OFFER or UNTRUSTED OFFER>",\n'
                '  "risk_score": <number 0-100>,\n'
                '  "risk_level": "<LOW | MODERATE | SUSPICIOUS | HIGH_RISK>",\n'
                '  "summary": "<2-3 sentence executive forensic summary>",\n'
                '  "anomalies_detected": ["<anomaly 1 with exact visual/text detail>", "<anomaly 2>"],\n'
                '  "attack_patterns": [{"pattern": "<PATTERN_CODE>", "description": "<description>"}],\n'
                '  "evidence": [\n'
                '    {\n'
                '      "category": "<Category>",\n'
                '      "signal": "<Signal Name>",\n'
                '      "observed_value": "<Observed detail in image>",\n'
                '      "reference_value": "<Legitimate standard>",\n'
                '      "severity": "<LOW | MEDIUM | HIGH | CRITICAL>",\n'
                '      "confidence": 0.95,\n'
                '      "risk_contribution": 35.0,\n'
                '      "explanation": "<Why this indicates fraud>"\n'
                '    }\n'
                '  ],\n'
                '  "recommendations": ["<Action 1>", "<Action 2>"],\n'
                '  "extracted_text": "<Extracted textual dialogue or key transaction details from images>"\n'
                "}"
            )

            response_text = None
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                model_name = settings.GEMINI_MODEL or "gemini-1.5-flash"
                contents = [*pil_images, prompt]
                resp = client.models.generate_content(
                    model=model_name,
                    contents=contents
                )
                response_text = resp.text
            except Exception as genai_err:
                logger.warning(f"google.genai call failed, attempting google.generativeai fallback: {genai_err}")
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=api_key)
                model = legacy_genai.GenerativeModel(settings.GEMINI_MODEL or "gemini-1.5-flash")
                resp = model.generate_content([*pil_images, prompt])
                response_text = resp.text

            if response_text:
                clean = response_text.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean)
                return parsed

        except Exception as e:
            logger.error(f"Gemini multimodal anomaly analysis error: {str(e)}")
            return None
        return None

