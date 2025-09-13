"""Pydantic models for RCA data structures."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class Incident(BaseModel):
    """Incident data structure."""
    id: str
    title: str
    service: str
    api_endpoint: Optional[str] = None
    job_id: Optional[str] = None
    workflow_id: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    version: Optional[str] = None
    created_at: str
    resolved_at: Optional[str] = None
    impact: str
    error_message: str


class Candidate(BaseModel):
    """Code candidate for RCA analysis."""
    repo: str
    file: str
    score: int
    reasons: List[str]


class Observation(BaseModel):
    """Code analysis observation."""
    kind: str  # "business_logic" or "code_quality"
    note: str
    rule: str


class RCAData(BaseModel):
    """Complete RCA analysis data."""
    incident: Incident
    suspect: Candidate
    summary: str
    created_at: str
    resolved_at: Optional[str] = None
    tat: Optional[str] = None
    impact: str
    whys: List[str]
    observations: List[Observation]
    diffs: List[str]
    validations: List[str]
    prevention: List[str]
    owners: str


class TicketData(BaseModel):
    """Linear ticket data structure."""
    title: str
    description: str
    team_key: str
    priority: int = 2
    labels: List[str] = []
    assignee: Optional[str] = None


class ComparisonData(BaseModel):
    """Before/after comparison data."""
    incident_id: str
    before_code: str
    after_code: str
    before_lang: str = "typescript"
    after_lang: str = "typescript"
    delta_note: str
    timeline_delta: str
