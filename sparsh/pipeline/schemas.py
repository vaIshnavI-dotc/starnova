from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

DataOrigin = Literal["real", "synthetic"]
Direction = Literal["bullish", "bearish", "neutral", "unclear"]
EvidenceLevel = Literal["insufficient", "low", "moderate", "high"]
Outcome = Literal["hit", "miss", "expired", "unscorable"]
SourceType = Literal["youtube", "telegram", "whatsapp", "x", "instagram", "other"]


class Source(BaseModel):
    source_id: str
    display_name: str                    # anonymised
    source_type: SourceType
    sebi_registered: Optional[bool] = None
    data_origin: DataOrigin


class Tip(BaseModel):
    tip_id: str
    source_id: str
    source_type: SourceType
    posted_at: datetime                  # UTC
    raw_text: str
    language: str = "en"
    ticker: Optional[str] = None         # filled by P2
    direction: Direction = "unclear"
    target_price: Optional[float] = None
    horizon_days: Optional[int] = None
    confidence_words: list[str] = []
    extraction_conf: float = Field(default=0.0, ge=0, le=1)
    data_origin: DataOrigin


class ScoredTip(BaseModel):
    tip_id: str
    outcome: Outcome
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    return_pct: Optional[float] = None
    cost_pct: float
    benchmark_return_pct: Optional[float] = None
    excess_return: Optional[float] = None
    hit: Optional[bool] = None
    scored_at: datetime


class SourceStats(BaseModel):
    source_id: str
    display_name: str
    source_type: str
    sebi_registered: Optional[bool] = None
    n_tips: int
    n_hits: int
    raw_hit_rate: float
    shrunk_hit_rate: float
    ci_low: float
    ci_high: float
    avg_excess_return: Optional[float] = None
    overconfidence_gap: Optional[float] = None
    evidence_level: EvidenceLevel
    data_origin: DataOrigin


class RiskFlag(BaseModel):
    code: Literal["COORDINATED_PROMOTION", "VOLUME_SPIKE", "LOW_FLOAT",
                  "CIRCUIT_LIMIT_STOCK", "UNREGISTERED_SOURCE",
                  "CERTAINTY_LANGUAGE", "SMALL_SAMPLE"]
    detail: str
    severity: Literal["info", "caution"]