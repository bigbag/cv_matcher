from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PingResponse(BaseModel):
    ping: str = "pong"


class ModelType(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


@dataclass
class ModelConfig:
    model_name: str
    api_key: str
    max_tokens: int
    temperature: float


class Location(BaseModel):
    country: str
    city: str


class Emphasis(BaseModel):
    technical_skills_weight: int = Field(default=50, ge=0, le=100)
    soft_skills_weight: int = Field(default=20, ge=0, le=100)
    experience_weight: int = Field(default=20, ge=0, le=100)
    education_weight: int = Field(default=10, ge=0, le=100)
    language_proficiency_weight: int = Field(default=5, ge=0, le=100)
    certifications_weight: int = Field(default=5, ge=0, le=100)


class JobRequirements(BaseModel):
    required_experience_years: int
    required_education_level: str
    required_skills: List[str]
    optional_skills: List[str]
    certifications_preferred: List[str]
    soft_skills: List[str]
    keywords_to_match: List[str]
    location: Location
    emphasis: Emphasis


class ScoringCriterion(BaseModel):
    name: str
    key: str
    weight: int = Field(ge=0, le=100)
    description: str
    factors: List[str]
    score: Optional[int] = None


class ScoreLevel(BaseModel):
    min_score: int
    max_score: int
    label: str


class DetailedMatchResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    criteria_scores: List[ScoringCriterion]
    match_reasons: str
    red_flags: Dict[str, List[str]]
    website: Optional[str] = None
