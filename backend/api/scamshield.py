from fastapi import APIRouter, HTTPException, status

from backend.schemas.scamshield import URLAnalyzeRequest, URLAnalyzeResponse
from backend.services.scamshield_service import analyze_url

router = APIRouter(prefix="/api/url", tags=["ScamShield"])


@router.post(
    "/analyze",
    response_model=URLAnalyzeResponse,
    summary="Analyze URL for scams, phishing, or threats",
    description="Inspects target URL via ScamShield intelligence and heuristic analysis.",
)
def analyze_target_url(request: URLAnalyzeRequest):
    """Analyzes a URL for malicious indicators, phishing, or fake job/company patterns."""
    raw_url = request.url.strip()
    if not raw_url or len(raw_url) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid non-empty URL must be provided.",
        )

    try:
        result = analyze_url(raw_url)
        return URLAnalyzeResponse(
            url=result["url"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            indicators=result.get("indicators", []),
            status=result.get("status"),
            provider=result.get("provider"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ScamShield analysis failed: {str(e)}",
        )
