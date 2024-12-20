from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from markitdown._markitdown import FileConversionException

from src.entities import DetailedMatchResult, ScoringCriterion
from src.routers import router

client = TestClient(router)


def test_ping_endpoint():
    """Test the health check endpoint."""
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


@pytest.fixture
def sample_files():
    """Fixture providing paths to test files."""
    resume_path = Path("./tests/examples/test_resume.pdf")
    job_desc_path = Path("./tests/examples/job_description.txt")
    return resume_path, job_desc_path


@pytest.fixture
def mock_service():
    """Fixture providing a mocked ResumeAnalysisService."""
    with patch("src.routers.ResumeAnalysisService") as mock:
        service_instance = Mock()
        mock.return_value = service_instance
        service_instance.process_files.return_value = ("resume content", "job description content")

        # Create an async mock for analyze_resume
        async_mock = AsyncMock()
        async_mock.return_value = DetailedMatchResult(
            overall_score=85,
            criteria_scores=[
                ScoringCriterion(
                    name="Technical Skills",
                    key="technical_skills",
                    weight=50,
                    description="Technical skills evaluation",
                    factors=["Python", "FastAPI"],
                    score=85,
                )
            ],
            match_reasons="Strong technical background with relevant skills",
            red_flags={"low": [], "medium": [], "high": []},
            website="https://example.com",
        )
        service_instance.analyze_resume = async_mock
        yield service_instance


@pytest.mark.asyncio
async def test_analyze_resume_success(sample_files, mock_service):
    """Test successful resume analysis."""
    resume_path, job_desc_path = sample_files

    # Create test files
    with open(resume_path, "rb") as resume_file, open(job_desc_path, "rb") as job_desc_file:
        response = client.post(
            "/analyze_resume",
            files={
                "resume_file": ("test_resume.pdf", resume_file, "application/pdf"),
                "job_description_file": ("job_description.txt", job_desc_file, "text/plain"),
            },
        )

    assert response.status_code == 200
    result = response.json()
    assert result["overall_score"] == 85
    assert len(result["criteria_scores"]) > 0
    assert result["match_reasons"] == "Strong technical background with relevant skills"


@pytest.mark.asyncio
async def test_analyze_resume_invalid_file():
    """Test resume analysis with invalid file."""
    with pytest.raises(FileConversionException):
        client.post(
            "/analyze_resume",
            files={
                "resume_file": ("test.pdf", b"invalid content", "application/pdf"),
                "job_description_file": ("job.txt", b"invalid content", "text/plain"),
            },
        )


@pytest.mark.asyncio
async def test_analyze_resume_missing_file():
    """Test resume analysis with missing file."""
    with pytest.raises(RequestValidationError):
        client.post(
            "/analyze_resume",
            files={
                "resume_file": ("test.pdf", b"some content", "application/pdf"),
                # Missing job description file
            },
        )
