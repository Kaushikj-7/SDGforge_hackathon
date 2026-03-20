from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime


class EvidenceSource(BaseModel):
    name: str = Field(..., description="Name of the source, e.g., PubMed or WHO")
    url: str = Field(..., description="Link to the source")
    snippet: str = Field(..., description="Relevant extract from the source")


class VerifyRequest(BaseModel):
    selected_text: str = Field(..., description="The raw claim text to verify")
    surrounding_context: str = Field("", description="Context surrounding the text")
    page_title: str = Field("", description="Title of the webpage")
    page_url: str = Field("", description="URL of the page where the claim was found")
    image_b64: Optional[str] = Field(
        "", description="Base64 encoded image, if running multimodal extraction"
    )


class DashboardStats(BaseModel):
    total: int
    critical: int
    high: int
    cached_hits: int
    avg_p_true: float
    risk_distribution: List[Dict[str, Any]]
    daily_trend: List[Dict[str, Any]]
    languages: List[Dict[str, Any]]
    recent_claims: List[Dict[str, Any]]
    top_topics: List[Dict[str, Any]]


class AggregatedVerdict(BaseModel):
    p_true: float = Field(..., ge=0, le=1)
    risk_level: str = Field(..., description="CRITICAL, HIGH, MEDIUM, LOW")
    verdict: str = Field(...)
    confidence: float = Field(..., ge=0, le=1)
    correction: str = Field(...)
    correction_en: str = Field(...)
    explanation: str = Field(...)
    sources: List[EvidenceSource] = []
    bias_flags: List[str] = []
    inequality_angle: str = ""
    vulnerable_populations: List[str] = []
    sdg3_impact: str = ""
    sdg10_impact: str = ""
    non_english_risk: bool = False
    claim_type: str = "general"
    agent_scores: Dict[str, float] = {}
    original_lang: Optional[str] = None
    lang_name: Optional[str] = None
    claim_text: Optional[str] = None
    translated_text: Optional[str] = None
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    from_cache: Optional[bool] = False


class StreamResponse(BaseModel):
    status: str
    message: Optional[str] = None
    lang: Optional[str] = None
    verdict: Optional[AggregatedVerdict] = None

class Agent1Response(BaseModel):
    agent: str = "groq_detector"
    p_true: float = 0.5
    verdict: str = "UNCERTAIN"
    reasoning: str = ""
    claim_type: str = "general"
    latency_ms: int = 0
    error: Optional[str] = None

class Agent2Response(BaseModel):
    agent: str = "rag_evidence"
    p_true: float = 0.5
    sources: List[EvidenceSource] = []
    rag_hits: int = 0
    latency_ms: int = 0
    error: Optional[str] = None

class Agent3Response(BaseModel):
    agent: str = "authority_check"
    p_true: float = 0.5
    sources: List[EvidenceSource] = []
    authority_found: bool = False
    latency_ms: int = 0
    error: Optional[str] = None

class Agent4Response(BaseModel):
    agent: str = "gemini_correction"
    correction: str = "Unable to verify."
    correction_en: str = "Unable to verify."
    explanation: str = ""
    p_true_adjustment: float = 0.0
    sources: List[EvidenceSource] = []
    latency_ms: int = 0
    error: Optional[str] = None

class Agent5Response(BaseModel):
    agent: str = "bias_sdg10"
    vulnerable_populations: List[str] = []
    inequality_angle: str = ""
    sdg3_impact: str = ""
    sdg10_impact: str = ""
    bias_flags: List[str] = []
    non_english_risk: bool = False
    latency_ms: int = 0
    error: Optional[str] = None

