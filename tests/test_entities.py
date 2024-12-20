import pytest
from pydantic import ValidationError

from src.entities import (
    DetailedMatchResult,
    Emphasis,
    JobRequirements,
    Location,
    ModelConfig,
    ModelType,
    PingResponse,
    ScoreLevel,
    ScoringCriterion,
)


def test_ping_response():
    response = PingResponse()
    assert response.ping == "pong"


def test_model_type():
    assert ModelType.ANTHROPIC.value == "anthropic"
    assert ModelType.OPENAI.value == "openai"


def test_model_config():
    config = ModelConfig(
        model_name="gpt-4",
        api_key="test-key",
        max_tokens=1000,
        temperature=0.7,
    )
    assert config.model_name == "gpt-4"
    assert config.api_key == "test-key"
    assert config.max_tokens == 1000
    assert config.temperature == 0.7


def test_location():
    location = Location(country="USA", city="San Francisco")
    assert location.country == "USA"
    assert location.city == "San Francisco"


def test_emphasis_default_values():
    emphasis = Emphasis()
    assert emphasis.technical_skills_weight == 50
    assert emphasis.soft_skills_weight == 20
    assert emphasis.experience_weight == 20
    assert emphasis.education_weight == 10
    assert emphasis.language_proficiency_weight == 5
    assert emphasis.certifications_weight == 5


def test_emphasis_validation():
    with pytest.raises(ValidationError):
        Emphasis(technical_skills_weight=101)  # Over 100
    with pytest.raises(ValidationError):
        Emphasis(soft_skills_weight=-1)  # Under 0


def test_job_requirements():
    job = JobRequirements(
        required_experience_years=5,
        required_education_level="Bachelor's",
        required_skills=["Python", "SQL"],
        optional_skills=["Docker"],
        certifications_preferred=["AWS"],
        soft_skills=["Communication"],
        keywords_to_match=["agile"],
        location=Location(country="USA", city="New York"),
        emphasis=Emphasis(),
    )
    assert job.required_experience_years == 5
    assert len(job.required_skills) == 2
    assert job.location.city == "New York"


def test_scoring_criterion():
    criterion = ScoringCriterion(
        name="Technical Skills",
        key="tech_skills",
        weight=30,
        description="Technical skills evaluation",
        factors=["Python", "SQL"],
    )
    assert criterion.weight == 30
    assert len(criterion.factors) == 2
    assert criterion.score is None

    with pytest.raises(ValidationError):
        ScoringCriterion(
            name="Invalid",
            key="invalid",
            weight=101,  # Over 100
            description="Test",
            factors=[],
        )


def test_score_level():
    level = ScoreLevel(min_score=80, max_score=100, label="Excellent")
    assert level.min_score == 80
    assert level.max_score == 100
    assert level.label == "Excellent"


def test_detailed_match_result():
    criterion = ScoringCriterion(
        name="Test",
        key="test",
        weight=50,
        description="Test criterion",
        factors=["factor1"],
        score=75,
    )

    result = DetailedMatchResult(
        overall_score=85,
        criteria_scores=[criterion],
        match_reasons="Good technical skills",
        red_flags={"experience": ["Missing required years"]},
        website="https://example.com",
    )

    assert result.overall_score == 85
    assert len(result.criteria_scores) == 1
    assert result.website == "https://example.com"

    with pytest.raises(ValidationError):
        DetailedMatchResult(
            overall_score=101,  # Over 100
            criteria_scores=[],
            match_reasons="",
            red_flags={},
        )
