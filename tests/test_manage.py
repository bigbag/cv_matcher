from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from src.client import AIClient
from src.entities import ModelType
from src.manage import analyze, cli
from src.services import ResumeAnalysisService


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def mock_service():
    with patch('src.manage.ResumeAnalysisService') as mock:
        service_instance = MagicMock()
        service_instance.process_files.return_value = ('resume content', 'job description content')
        service_instance.analyze_resume = AsyncMock(
            return_value={
                'match_percentage': 85,
                'matching_skills': ['Python', 'Testing'],
                'missing_skills': ['Java'],
                'recommendations': ['Learn Java'],
            }
        )
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def mock_client():
    with patch('src.manage.AIClient') as mock:
        client_instance = MagicMock()
        mock.return_value = client_instance
        yield client_instance


def test_cli_analyze_success(cli_runner, mock_service, mock_client, tmp_path):
    # Create temporary test files
    resume_file = tmp_path / "resume.txt"
    job_desc_file = tmp_path / "job.txt"
    resume_file.write_text("Test resume content")
    job_desc_file.write_text("Test job description")

    result = cli_runner.invoke(
        cli, ['analyze', '--resume_path', str(resume_file), '--job_desc_path', str(job_desc_file)]
    )

    assert result.exit_code == 0
    mock_service.process_files.assert_called_once()
    mock_service.analyze_resume.assert_called_once_with('resume content', 'job description content')
    mock_service.show_analysis_result.assert_called_once()


def test_cli_analyze_missing_files(cli_runner):
    result = cli_runner.invoke(
        cli, ['analyze', '--resume_path', 'nonexistent.txt', '--job_desc_path', 'nonexistent.txt']
    )
    assert result.exit_code != 0
    assert "Path" in result.output and "does not exist" in result.output


@pytest.mark.asyncio
async def test_cli_analyze_service_error(cli_runner, mock_service, mock_client, tmp_path):
    # Create temporary test files
    resume_file = tmp_path / "resume.txt"
    job_desc_file = tmp_path / "job.txt"
    resume_file.write_text("Test resume content")
    job_desc_file.write_text("Test job description")

    # Simulate an error in the service
    mock_service.analyze_resume.side_effect = Exception("Test error")

    result = cli_runner.invoke(
        cli, ['analyze', '--resume_path', str(resume_file), '--job_desc_path', str(job_desc_file)]
    )

    assert result.exit_code != 0
    assert "An unexpected error occurred during analysis" in result.output


@patch('src.manage.uvicorn.run')
def test_start_server(mock_uvicorn_run, cli_runner):
    result = cli_runner.invoke(cli, ['start-server'])

    assert result.exit_code == 0
    mock_uvicorn_run.assert_called_once()
    call_kwargs = mock_uvicorn_run.call_args[1]
    assert call_kwargs['app'] == "src.server:app"
    assert isinstance(call_kwargs['port'], int)
    assert isinstance(call_kwargs['workers'], int)
