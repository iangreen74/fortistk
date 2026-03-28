from fastapi import APIRouter, HTTPException, status, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict
import importlib
import os

from backend.fastapi_service.api.schemas import (
    HealthResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    WalletScoreRequest,
    WalletScoreResponse,
    TransactionAnalysisRequest,
    TransactionAnalysisResponse,
    ThreatHuntRequest,
    ThreatHuntResponse,
    ErrorResponse
)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

def get_agent(agent_name: str):
    """Dynamically load agent based on name."""
    try:
        module_path = f"agents.{agent_name}.agent"
        module = importlib.import_module(module_path)
        agent_class = getattr(module, "Agent")
        return agent_class()
    except (ImportError, AttributeError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' not found: {str(e)}"
        )

@router.get("/health", response_model=HealthResponse, tags=["Health"])
@limiter.limit("100/minute")
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        services={"api": "healthy"}
    )

@router.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
@limiter.limit("20/minute")
async def analyze(request: AnalyzeRequest):
    """Generic analysis endpoint that routes to specific agents."""
    try:
        agent = get_agent(request.agent_type)
        result = agent.analyze(request.data)
        return AnalyzeResponse(
            agent_type=request.agent_type,
            result=result,
            success=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/wallet/score", response_model=WalletScoreResponse, tags=["Wallet"])
@limiter.limit("20/minute")
async def wallet_score(request: WalletScoreRequest):
    """Score a wallet address."""
    try:
        agent = get_agent("wallet_score_agent")
        result = agent.analyze({"address": request.address, "chain": request.chain})
        return WalletScoreResponse(
            address=request.address,
            score=result.get("score", 0),
            risk_level=result.get("risk_level", "unknown"),
            details=result.get("details", {})
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/transaction/analyze", response_model=TransactionAnalysisResponse, tags=["Transaction"])
@limiter.limit("20/minute")
async def transaction_analyze(request: TransactionAnalysisRequest):
    """Analyze a transaction."""
    try:
        agent = get_agent("tx_analyzer_agent")
        result = agent.analyze({"tx_hash": request.tx_hash, "chain": request.chain})
        return TransactionAnalysisResponse(
            tx_hash=request.tx_hash,
            analysis=result.get("analysis", {}),
            anomalies=result.get("anomalies", []),
            confidence=result.get("confidence", 0.0)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/threat/hunt", response_model=ThreatHuntResponse, tags=["Threat"])
@limiter.limit("10/minute")
async def threat_hunt(request: ThreatHuntRequest):
    """Hunt for threats in blockchain data."""
    try:
        agent = get_agent("threat_hunter_agent")
        result = agent.analyze({
            "query": request.query,
            "chain": request.chain,
            "depth": request.depth
        })
        return ThreatHuntResponse(
            threats=result.get("threats", []),
            patterns=result.get("patterns", []),
            summary=result.get("summary", "")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
