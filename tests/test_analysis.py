from typing import List
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.analysis import CriteriaEvaluator, JobAnalyzer, RedFlagAnalyzer, ResumeProcessor, create_scoring_criteria
from src.entities import DetailedMatchResult, Emphasis, JobRequirements, Location, ScoringCriterion


# Fixtures
@pytest.fixture
def mock_client():
    client = MagicMock()
    client.run = AsyncMock()
    return client


@pytest.fixture
def job_requirements():
    return JobRequirements(
        required_experience_years=5,
        required_education_level="Bachelor's",
        required_skills=["Python", "AI"],
        optional_skills=["Docker"],
        certifications_preferred=["AWS"],
        soft_skills=["Communication"],
        keywords_to_match=["machine learning"],
        location=Location(country="USA", city="San Francisco"),
        emphasis=Emphasis(
            technical_skills_weight=50,
            soft_skills_weight=20,
            experience_weight=20,
            education_weight=10,
            language_proficiency_weight=5,
            certifications_weight=5,
        ),
    )


@pytest.fixture
def sample_resume_text():
    return """
    John Doe
    Software Engineer
    
    Experience:
    - 5 years Python development
    - Machine Learning expertise
    
    Education:
    - Bachelor's in Computer Science
    
    Website: https://johndoe.dev
    """


@pytest.fixture
def sample_job_description():
    return """
    Senior Software Engineer
    
    Requirements:
    - 5+ years experience in Python
    - Machine Learning background
    - Bachelor's degree
    """


# Test create_scoring_criteria function
def test_create_scoring_criteria(job_requirements):
    criteria = create_scoring_criteria(job_requirements)

    assert len(criteria) == 6
    assert all(isinstance(c, ScoringCriterion) for c in criteria)

    # Test specific criterion
    tech_skills = next(c for c in criteria if c.key == "technical_skills")
    assert tech_skills.weight == job_requirements.emphasis.technical_skills_weight
    assert tech_skills.name == "Technical Skills"


# Test ResumeProcessor
@pytest.mark.asyncio
async def test_resume_processor_unify(mock_client, sample_resume_text):
    processor = ResumeProcessor(mock_client)
    mock_client.run.return_value = "Unified Resume"

    result = await processor.unify_resume(sample_resume_text)
    assert result == "Unified Resume"
    mock_client.run.assert_called_once()


@pytest.mark.asyncio
async def test_resume_processor_get_website(mock_client, sample_resume_text):
    processor = ResumeProcessor(mock_client)
    mock_client.run.return_value = "https://johndoe.dev"

    result = await processor.get_website(sample_resume_text)
    assert result == "https://johndoe.dev"
    mock_client.run.assert_called_once()


# Test CriteriaEvaluator
@pytest.mark.asyncio
async def test_criteria_evaluator(mock_client, job_requirements, sample_resume_text):
    evaluator = CriteriaEvaluator(mock_client)
    mock_client.run.return_value = "85"

    criterion = ScoringCriterion(
        name="Test Criterion",
        key="test",
        weight=50,
        description="Test description",
        factors=["factor1", "factor2"],
    )

    score = await evaluator.evaluate_criterion(criterion, sample_resume_text, job_requirements)
    assert score == 85
    mock_client.run.assert_called_once()


def test_criteria_evaluator_parse_score():
    evaluator = CriteriaEvaluator(mock_client)

    # Test basic number parsing
    assert evaluator._parse_score("85", "Test") == 85
    assert evaluator._parse_score("0", "Test") == 0
    assert evaluator._parse_score("100", "Test") == 100

    # Test numbers with spaces and text
    assert evaluator._parse_score("Score is 85", "Test") == 85
    assert evaluator._parse_score("The score is 75 points", "Test") == 75
    assert evaluator._parse_score("Final evaluation: 90", "Test") == 90

    # Test boundary cases
    assert evaluator._parse_score("150", "Test") == 100  # Above maximum
    assert evaluator._parse_score("-10", "Test") == 0  # Below minimum
    assert evaluator._parse_score("100 out of 100", "Test") == 100

    # Test invalid inputs
    assert evaluator._parse_score("invalid", "Test") == 0
    assert evaluator._parse_score("", "Test") == 0
    assert evaluator._parse_score("no numbers here", "Test") == 0
    assert evaluator._parse_score("score: abc", "Test") == 0

    # Test multiple numbers (should take the last one)
    assert evaluator._parse_score("50 60 70", "Test") == 50
    assert evaluator._parse_score("First score: 50, Final score: 80", "Test") == 50


# Test RedFlagAnalyzer
def test_red_flag_analyzer():
    analyzer = RedFlagAnalyzer()
    criteria: List[ScoringCriterion] = [
        ScoringCriterion(
            name="Technical Skills",
            key="technical_skills",
            weight=50,
            description="Test",
            factors=["test"],
            score=25,
        ),
        ScoringCriterion(
            name="Experience",
            key="experience",
            weight=20,
            description="Test",
            factors=["test"],
            score=45,
        ),
        ScoringCriterion(
            name="Education",
            key="education",
            weight=10,
            description="Test",
            factors=["test"],
            score=80,
        ),
    ]

    red_flags = analyzer.analyze(criteria)

    assert "high" in red_flags
    assert "medium" in red_flags
    assert "low" in red_flags
    assert any("Technical Skills" in flag for flag in red_flags["high"])
    assert any("Experience" in flag for flag in red_flags["medium"])


# Test JobAnalyzer
@pytest.mark.asyncio
async def test_job_analyzer_full_flow(mock_client, sample_resume_text, sample_job_description, job_requirements):
    analyzer = JobAnalyzer(mock_client)

    # Mock all necessary responses
    mock_client.run.side_effect = [
        job_requirements,  # For extract_job_requirements
        "Unified Resume",  # For unify_resume
        "85",  # For first criterion evaluation
        "75",  # For second criterion evaluation
        "90",  # For third criterion evaluation
        "80",  # For fourth criterion evaluation
        "Match reasons",  # For match_reasons
        "https://johndoe.dev",  # For website
    ]

    result = await analyzer.match_resume(
        resume_text=sample_resume_text,
        job_description=sample_job_description,
        job_requirements=job_requirements,
    )

    assert isinstance(result, DetailedMatchResult)
    assert result.overall_score > 0
    assert len(result.criteria_scores) == 6
    assert result.match_reasons == "Match reasons"
    assert result.website == "https://johndoe.dev"
    assert isinstance(result.red_flags, dict)


@pytest.mark.asyncio
async def test_job_analyzer_extract_requirements(mock_client, sample_job_description):
    analyzer = JobAnalyzer(mock_client)
    mock_client.run.return_value = JobRequirements(
        required_experience_years=5,
        required_education_level="Bachelor's",
        required_skills=["Python"],
        optional_skills=[],
        certifications_preferred=[],
        soft_skills=[],
        keywords_to_match=[],
        location=Location(country="USA", city="San Francisco"),
        emphasis=Emphasis(),
    )

    result = await analyzer.extract_job_requirements(sample_job_description)
    assert isinstance(result, JobRequirements)
    assert result.required_experience_years == 5
    mock_client.run.assert_called_once()


@pytest.mark.asyncio
async def test_job_analyzer_unify_resume(mock_client, sample_resume_text):
    analyzer = JobAnalyzer(mock_client)
    mock_client.run.return_value = "Unified Resume"

    result = await analyzer.unify_resume(sample_resume_text)
    assert result == "Unified Resume"
    mock_client.run.assert_called_once()
