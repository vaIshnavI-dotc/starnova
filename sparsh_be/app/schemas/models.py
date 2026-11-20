from typing import Literal, Optional
from pydantic import BaseModel, Field

DataOrigin = Literal['real','synthetic']
Direction = Literal['bullish','bearish','neutral','unclear']
EvidenceLevel = Literal['insufficient','low','moderate','high']
class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)
    source_hint: Optional[str] = None
    posted_at: Optional[str] = None
class EvalSessionRequest(BaseModel):
    participant_label: str = Field(min_length=1)
class EvalDecisionRequest(BaseModel):
    session_id: str
    item_id: str
    decision: Literal['follow','skip']
    confidence: int = Field(ge=0,le=100)
    position_pct: float = Field(ge=0,le=100)
