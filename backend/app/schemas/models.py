from typing import Literal, Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

DataOrigin = Literal['real', 'synthetic']
Direction = Literal['bullish', 'bearish', 'neutral', 'unclear']
EvidenceLevel = Literal['none', 'low', 'medium', 'high', 'insufficient', 'moderate']
ActionType = Literal['bought', 'skipped', 'watching']
AlertType = Literal['outcome_confirmed', 'negative_outcome', 'new_update']
ChatStage = Literal['intake', 'awaiting_thesis', 'auditing', 'questioning', 'gate', 'locked', 'chitchat']


# Existing models
class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)
    source_hint: Optional[str] = None
    posted_at: Optional[str] = None


class EvalSessionRequest(BaseModel):
    participant_label: str = Field(min_length=1)


class EvalDecisionRequest(BaseModel):
    session_id: str
    item_id: str
    decision: Literal['follow', 'skip']
    confidence: int = Field(ge=0, le=100)
    position_pct: float = Field(ge=0, le=100)


# Contract models
class User(BaseModel):
    id: str
    name: str
    email: str


class SignupRequest(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    password: str = Field(min_length=4)


class LoginRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AuthResponse(BaseModel):
    token: str
    user: User


class StockInfo(BaseModel):
    name: str
    ticker: str


class ThesisLinkEvidence(BaseModel):
    summary: str
    source_url: Optional[str] = None


class ThesisLink(BaseModel):
    id: str
    text: str
    status: Literal['backed', 'unchecked', 'no_evidence']
    evidence: Optional[ThesisLinkEvidence] = None


class QuickReply(BaseModel):
    label: str
    value: str


class Block(BaseModel):
    type: str
    content: Optional[str] = None
    tip_id: Optional[str] = None
    sender: Optional[str] = None
    source_id: Optional[str] = None
    stock: Optional[StockInfo] = None
    claim: Optional[str] = None
    red_flags: Optional[List[str]] = None
    source_name: Optional[str] = None
    tips_total: Optional[int] = None
    tips_worked: Optional[int] = None
    shrunk_hit_rate: Optional[float] = None
    evidence_level: Optional[str] = None
    label: Optional[str] = None
    ticker: Optional[str] = None
    price_now: Optional[float] = None
    change_7d_pct: Optional[float] = None
    since_tip_pct: Optional[float] = None
    note: Optional[str] = None
    links: Optional[List[ThesisLink]] = None
    gaps_count: Optional[int] = None
    total_links: Optional[int] = None
    summary: Optional[str] = None
    decision_id: Optional[str] = None
    required_fields: Optional[List[str]] = None
    values: Optional[Dict[str, Any]] = None
    locked: Optional[bool] = None
    locked_at: Optional[str] = None
    text: Optional[str] = None
    confirm_token: Optional[str] = None
    draft: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    conversation_id: str
    stage: ChatStage
    questions_asked: int
    questions_max: int = 6
    blocks: List[Dict[str, Any]]
    quick_replies: List[Dict[str, str]] = []


class DecisionLockRequest(BaseModel):
    decision_id: str
    action: ActionType
    timeframe_days: int = Field(gt=0)
    exit_target: float = Field(gt=0)
    max_loss_pct: float = Field(gt=0, le=100)
    confidence: int = Field(ge=1, le=5)


class DecisionObject(BaseModel):
    id: str
    tip_id: str
    action: Optional[ActionType] = None
    timeframe_days: Optional[int] = None
    exit_target: Optional[float] = None
    max_loss_pct: Optional[float] = None
    confidence: Optional[int] = None
    thesis: Optional[str] = None
    gaps_count: int = 0
    locked_at: Optional[str] = None
    stock: Optional[StockInfo] = None
    source_name: Optional[str] = None


class Investment(BaseModel):
    id: str
    ticker: str
    stock_name: str
    quantity: float
    avg_price: float
    purchase_date: str
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    linked_tip_id: Optional[str] = None


class ConfirmInvestmentRequest(BaseModel):
    confirm_token: str
    ticker: Optional[str] = None
    quantity: Optional[float] = None
    avg_price: Optional[float] = None
    purchase_date: Optional[str] = None


class HorizonResult(BaseModel):
    status: Literal['worked', 'missed', 'pending']
    return_pct: Optional[float] = None
    benchmark_pct: Optional[float] = None


class Alert(BaseModel):
    id: str
    type: AlertType
    title: str
    body: str
    tip_id: str
    source_name: str
    results: Dict[str, HorizonResult]
    created_at: str
    read: bool = False


class Insight(BaseModel):
    id: str
    text: str
    evidence_count: int
