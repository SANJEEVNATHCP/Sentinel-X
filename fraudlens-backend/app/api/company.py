"""
FraudLens AI - Company Verification API Endpoints
Uses authoritative Company Master dataset to verify whether a company is Active (real) or Inactive (fake/defunct).
"""

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.investigation import Investigation
from app.models.uploaded_file import UploadedFile as UploadedFileModel
from app.schemas.company import (
    CompanyVerifyRequest, CompanyVerifyResponse,
    LinkedInVerifyRequest, LinkedInVerifyResponse,
    TrustScoreResponse
)
from app.schemas.offer_letter import OfferLetterResponse
from app.schemas.common import APIResponse
from app.services.company_service import CompanyService
from app.services.linkedin_service import LinkedInService
from app.services.mca_service import MCAService
from app.services.offer_letter_service import OfferLetterService
from app.utils.file_utils import save_upload_file_temporarily

router = APIRouter(prefix="/api/company", tags=["Company Verification"])

from app.models.investigation_result import InvestigationResult

@router.post("/verify", response_model=APIResponse[CompanyVerifyResponse])
def verify_company(
    req: CompanyVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluates corporate entity against authoritative MCA Company Master dataset.
    Flags Active (real) vs Inactive (fake/defunct) status with registered CIN, ROC, and State.
    """
    res = MCAService.verify_company(db, req.company_name, req.domain)
    
    # Check recruiter consistency if email was provided
    if req.recruiter_email:
        from app.services.recruiter_service import RecruiterService
        r_check = RecruiterService.verify_recruiter_email(req.recruiter_email, res.get("official_domain") or req.domain)
        res["domain_match"] = r_check["domain_match"]

    risk_level = res.get("risk_level", "LOW")
    risk_score = 15.0 if risk_level == "LOW" else (85.0 if risk_level == "HIGH_RISK" else 50.0)
    summary = f"MCA Company Verification for '{req.company_name}'. Status: {res.get('company_status')}, Source: {res.get('verification_source')}, Risk: {risk_level}."

    inv = Investigation(
        user_id=current_user.id,
        type="COMPANY",
        status="COMPLETED",
        target_entity=req.company_name,
        risk_score=risk_score,
        risk_level=risk_level,
        summary=summary
    )
    db.add(inv)
    db.flush()

    inv_res = InvestigationResult(
        investigation_id=inv.id,
        user_id=current_user.id,
        type="COMPANY",
        risk_score=risk_score,
        risk_level=risk_level,
        summary=summary,
        recommendation=res.get("verification_note") or f"Company verification status: {res.get('company_status')}.",
        evidence_json=[
            {"signal": "Company Status", "observed_value": str(res.get("company_status")), "risk_weight": 0.8},
            {"signal": "CIN", "observed_value": str(res.get("cin") or "None"), "risk_weight": 0.5},
            {"signal": "Official Domain", "observed_value": str(res.get("official_domain") or "None"), "risk_weight": 0.5}
        ],
        risk_factors_json=[
            {"name": "Status Check", "contribution": 30.0 if risk_level != "LOW" else 0.0}
        ],
        verification_json=res,
        ai_summary=summary
    )
    db.add(inv_res)
    db.commit()

    response_data = CompanyVerifyResponse(
        searched_name=req.company_name,
        mca_verified=res["mca_verified"],
        company_name=res.get("company_name"),
        cin=res.get("cin"),
        company_status=res["company_status"],
        roc=res.get("roc"),
        registered_state=res.get("registered_state"),
        brand_name=res.get("brand_name"),
        official_domain=res.get("official_domain"),
        official_website=res.get("official_website"),
        domain_match=res.get("domain_match"),
        verification_source=res["verification_source"],
        verification_note=res.get("verification_note"),
        risk_level=res["risk_level"],
        investigation_id=inv.id,
        id=inv_res.id
    )
    return APIResponse(data=response_data)

@router.post("/linkedin", response_model=APIResponse[LinkedInVerifyResponse])
def verify_linkedin(
    req: LinkedInVerifyRequest,
    current_user: User = Depends(get_current_user)
):
    """Verifies LinkedIn company presence URL structure."""
    res = LinkedInService.verify_company_presence(req.linkedin_url)
    return APIResponse(data=LinkedInVerifyResponse(**res))

@router.post("/trust-score", response_model=APIResponse[TrustScoreResponse])
def compute_trust_score(
    req: CompanyVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Computes transparent, auditable 0-100 trust score across corporate records."""
    eval_res = CompanyService.evaluate_company(
        db=db,
        company_name=req.company_name,
        domain=req.domain,
        recruiter_email=req.recruiter_email
    )
    return APIResponse(data=TrustScoreResponse(
        company_name=req.company_name,
        trust_score=eval_res["trust_score"],
        risk_level=eval_res["risk_level"],
        components=eval_res["components"],
        evidence=eval_res["evidence"],
        recommendations=eval_res["recommendations"]
    ))

@router.post("/offer-letter", response_model=APIResponse[OfferLetterResponse])
async def verify_offer_letter(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Uploads employment document/offer letter. Performs Gemini structured entity extraction,
    evaluates company against Company Master dataset, and flags advance fee/recruitment scams.
    """
    # 1. Create Investigation Entry
    inv = Investigation(
        user_id=current_user.id,
        type="OFFER_LETTER",
        status="PROCESSING",
        target_entity=file.filename or "Offer Letter"
    )
    db.add(inv)
    db.flush()

    # 2. Persist temporary file
    temp_path = save_upload_file_temporarily(file)
    up_file = UploadedFileModel(
        investigation_id=inv.id,
        original_filename=file.filename or "offer_letter.pdf",
        stored_path=temp_path,
        file_type="DOCUMENT",
        file_size_bytes=len(await file.read())
    )
    db.add(up_file)
    db.commit()

    # 3. Execute Offer Letter Verification Pipeline
    res = await OfferLetterService.verify_offer_letter(
        db=db,
        user_id=current_user.id,
        investigation_id=inv.id,
        file_path=temp_path
    )

    return APIResponse(message="Offer letter verified", data=res)

@router.get("/history", response_model=APIResponse[list])
def get_company_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Returns past company evaluations for this user."""
    invs = db.query(Investigation).filter(
        Investigation.user_id == current_user.id,
        Investigation.type.in_(["COMPANY", "OFFER_LETTER"])
    ).all()
    history = [{"id": i.id, "target": i.target_entity, "score": i.risk_score, "level": i.risk_level, "date": i.created_at.isoformat()} for i in invs]
    return APIResponse(data=history)
