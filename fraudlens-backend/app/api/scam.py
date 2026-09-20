"""
FraudLens AI - Scam & URL Intelligence API Endpoints
"""

import os
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.investigation import Investigation
from app.models.investigation_result import InvestigationResult
from app.models.uploaded_file import UploadedFile as UploadedFileModel
from app.schemas.scam import (
    ScamAnalyzeRequest, ScamAnalysisResponse,
    URLCheckRequest, URLCheckResponse, VirusTotalResult
)
from app.schemas.common import APIResponse
from app.services.scam_service import ScamService
from app.services.url_service import URLService
from app.services.virustotal_service import VirusTotalService
from app.services.image_analysis_service import ImageAnalysisService
from app.services.pdf_service import PDFService
from app.utils.file_utils import save_upload_file_temporarily
from app.exceptions import ValidationError

router = APIRouter(prefix="/api/scam", tags=["Scam Intelligence"])

@router.post("/analyze", response_model=APIResponse[ScamAnalysisResponse])
async def analyze_scam(
    req: ScamAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Combines URL intelligence, Company Master dataset lookup, and message analysis
    into a unified investigation session.
    """
    inv = Investigation(
        user_id=current_user.id,
        type="SCAM_URL",
        status="PROCESSING",
        target_entity=req.url or req.company_name or "Scam Investigation"
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    res = await ScamService.analyze_multi_signal(
        db=db,
        user_id=current_user.id,
        investigation_id=inv.id,
        url=req.url,
        company_name=req.company_name,
        linkedin_url=req.linkedin_url,
        recruiter_email=req.recruiter_email,
        message_text=req.message_text
    )
    return APIResponse(message="Scam investigation completed", data=res)

@router.post("/url", response_model=APIResponse[URLCheckResponse])
async def scan_url(
    req: URLCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluates URL security using SSRF-safe checks, local threat dataset status (ACTIVE/INACTIVE),
    and VirusTotal scanning. Creates an investigation record and derived result for report export.
    """
    res = await URLService.analyze_url(db, req.url)

    inv = Investigation(
        user_id=current_user.id,
        type="SCAM_URL",
        status="COMPLETED",
        target_entity=req.url,
        risk_score=res.get("risk_score", 0.0),
        risk_level=res.get("risk_level", "LOW"),
        summary=f"Scanned {req.url}. Threat status: {res.get('local_dataset', {}).get('status', 'NOT_FOUND')}, Risk: {res.get('risk_level', 'LOW')} ({res.get('risk_score', 0)}/100)."
    )
    db.add(inv)
    db.flush()

    inv_res = InvestigationResult(
        investigation_id=inv.id,
        user_id=current_user.id,
        type="SCAM_URL",
        risk_score=res.get("risk_score", 0.0),
        risk_level=res.get("risk_level", "LOW"),
        summary=inv.summary,
        recommendation="; ".join(res.get("recommendations", [])),
        evidence_json=res.get("evidence", []),
        risk_factors_json=[{"name": p, "weight": 1.0, "contribution": 10.0} for p in res.get("suspicious_patterns_detected", [])],
        ai_summary=inv.summary
    )
    db.add(inv_res)
    db.commit()

    res["investigation_id"] = inv.id
    res["id"] = inv_res.id
    return APIResponse(data=URLCheckResponse(**res))

@router.post("/url/virustotal", response_model=APIResponse[VirusTotalResult])
async def check_virustotal_only(
    req: URLCheckRequest,
    current_user: User = Depends(get_current_user)
):
    """Direct VirusTotal query endpoint with graceful fallback."""
    vt = await VirusTotalService.scan_url(req.url)
    return APIResponse(data=VirusTotalResult(**vt))

@router.post("/image-analysis", response_model=APIResponse[dict])
async def analyze_screenshot(
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None),
    context: Optional[str] = Form(None),
    x_gemini_key: Optional[str] = Header(None, alias="x-gemini-key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Accepts up to 3 chat or payment screenshots. Analyzes visual and text indicators
    for advance payment demands, fake receipts, urgency, and OTP solicitation using Gemini Vision.
    """
    upload_list = []
    if files:
        upload_list.extend(files)
    if file and file not in upload_list:
        upload_list.append(file)

    valid_uploads = [f for f in upload_list if f and f.filename][:3]
    if not valid_uploads:
        raise ValidationError("Please upload between 1 and 3 screenshot/payment images.")

    inv = Investigation(
        user_id=current_user.id,
        type="IMAGE_CHAT",
        status="PROCESSING",
        target_entity=", ".join([f.filename for f in valid_uploads])
    )
    db.add(inv)
    db.flush()

    saved_paths = []
    for f in valid_uploads:
        temp_path = save_upload_file_temporarily(f)
        saved_paths.append(temp_path)
        file_size = os.path.getsize(temp_path) if os.path.exists(temp_path) else 0
        up_file = UploadedFileModel(
            investigation_id=inv.id,
            original_filename=f.filename,
            stored_path=temp_path,
            file_type="IMAGE",
            file_size_bytes=file_size
        )
        db.add(up_file)
    db.commit()

    res = await ImageAnalysisService.analyze_multimodal_images(
        image_paths=saved_paths,
        context_text=context,
        custom_api_key=x_gemini_key,
        file_names=[f.filename for f in valid_uploads]
    )

    inv.status = "COMPLETED"
    inv.risk_score = res["risk_score"]
    inv.risk_level = res["risk_level"]
    inv.summary = res.get("summary") or f"Identified {len(res.get('anomalies_detected', []))} anomaly(ies) across {len(valid_uploads)} image(s)."

    inv_res = InvestigationResult(
        investigation_id=inv.id,
        user_id=current_user.id,
        type="IMAGE_CHAT",
        risk_score=res["risk_score"],
        risk_level=res["risk_level"],
        summary=inv.summary,
        recommendation="; ".join(res.get("recommendations", [])),
        evidence_json=res.get("evidence", []),
        risk_factors_json=[{"name": a, "weight": 1.0, "contribution": 15.0} for a in res.get("anomalies_detected", [])],
        attack_patterns_json=res.get("attack_patterns", []),
        ai_summary=res.get("summary")
    )
    db.add(inv_res)
    db.commit()

    res["investigation_id"] = inv.id
    res["id"] = inv_res.id
    return APIResponse(data=res)

