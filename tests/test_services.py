from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import click
import pytest

from src.entities import DetailedMatchResult, ScoringCriterion
from src.services import ResumeAnalysisService


@pytest.fixture
def mock_ai_client():
    return MagicMock()


@pytest.fixture
def mock_job_analyzer():
    return AsyncMock()


@pytest.fixture
def mock_markitdown():
    mock = MagicMock()
    mock_convert_result = MagicMock()
    mock_convert_result.text_content = "Mocked resume content"
    mock.convert.return_value = mock_convert_result
    return mock


@pytest.fixture
def service(mock_ai_client, mock_markitdown):
    with (
        patch('src.services.JobAnalyzer'),
        patch('src.services.MarkItDown', return_value=mock_markitdown),
        patch('src.services.Console'),
    ):
        service = ResumeAnalysisService(client=mock_ai_client)
        return service


@pytest.fixture
def sample_match_result():
    return DetailedMatchResult(
        overall_score=75,
        criteria_scores=[
            ScoringCriterion(
                name="Skills",
                score=80,
                weight=30,
                description="Good skills match",
                factors=["Python", "AWS"],
                key="skills",
            ),
            ScoringCriterion(
                name="Experience",
                score=70,
                weight=40,
                description="Relevant experience",
                factors=["2 years", "DevOps"],
                key="experience",
            ),
        ],
        match_reasons="Strong technical background",
        website="https://www.example.com",
        red_flags={"Experience": ["Junior level experience"]},
    )


def test_process_files_success(service, tmp_path):
    # Create temporary test files
    resume_path = tmp_path / "resume.md"
    job_desc_path = tmp_path / "job.txt"

    resume_path.write_text("# Resume\nSkills: Python")
    job_desc_path.write_text("Job Description")

    resume_text, job_description = service.process_files(resume_path, job_desc_path)

    assert isinstance(resume_text, str)
    assert isinstance(job_description, str)
    assert len(resume_text) > 0
    assert len(job_description) > 0


def test_process_files_missing_file(service):
    with pytest.raises(click.ClickException):
        service.process_files(Path("nonexistent.md"), Path("nonexistent.txt"))


@pytest.mark.asyncio
async def test_analyze_resume_success(service):
    # Mock the analyzer methods with coroutine return values
    service.analyzer.extract_job_requirements.return_value = ["Python", "AWS"]
    service.analyzer.unify_resume.return_value = "Unified resume content"
    service.analyzer.match_resume.return_value = DetailedMatchResult(
        overall_score=75,
        criteria_scores=[],
        match_reasons="Good match",
        red_flags={},
    )

    # Convert all return values to coroutines
    service.analyzer.extract_job_requirements = AsyncMock(return_value=["Python", "AWS"])
    service.analyzer.unify_resume = AsyncMock(return_value="Unified resume content")
    service.analyzer.match_resume = AsyncMock(
        return_value=DetailedMatchResult(
            overall_score=75,
            criteria_scores=[],
            match_reasons="Good match",
            red_flags={},
        )
    )

    result = await service.analyze_resume("resume text", "job description")

    assert isinstance(result, DetailedMatchResult)
    assert result.overall_score == 75
    service.analyzer.extract_job_requirements.assert_awaited_once_with("job description")
    service.analyzer.unify_resume.assert_awaited_once_with("resume text")
    service.analyzer.match_resume.assert_awaited_once()


@pytest.mark.asyncio
async def test_analyze_resume_failure(service):
    # Set up async mock with an exception
    service.analyzer.extract_job_requirements = AsyncMock(side_effect=Exception("API Error"))
    service.analyzer.unify_resume = AsyncMock()
    service.analyzer.match_resume = AsyncMock()

    with pytest.raises(click.ClickException):
        await service.analyze_resume("resume text", "job description")

    # Verify only the first method was called before the exception
    service.analyzer.extract_job_requirements.assert_awaited_once_with("job description")
    service.analyzer.unify_resume.assert_not_awaited()
    service.analyzer.match_resume.assert_not_awaited()


def test_show_analysis_result(service, sample_match_result, capsys):
    # Test that the method runs without errors
    service.show_analysis_result(sample_match_result)

    # Since we're using rich console, we can't easily test the exact output
    # but we can verify that some output was produced
    captured = capsys.readouterr()
    assert len(captured.out) > 0
