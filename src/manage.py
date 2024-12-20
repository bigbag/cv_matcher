#!/usr/bin/env python3

import asyncio
from pathlib import Path

import click
import uvicorn

from src.client import AIClient
from src.conf import LOG_CONFIG, settings
from src.entities import ModelType
from src.logger import create_logger
from src.services import ResumeAnalysisService

logger = create_logger(__name__)


@click.group()
def cli():
    """CV Matcher CLI tool for analyzing resumes against job descriptions."""
    pass


@cli.command()
@click.option(
    '--resume_path',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help='Path to the resume file',
)
@click.option(
    '--job_desc_path',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help='Path to the job description file',
)
def analyze(resume_path: Path, job_desc_path: Path):
    """Analyze a resume against a job description."""
    client = AIClient(model_type=ModelType.OPENAI, max_tokens=2000)
    service = ResumeAnalysisService(client)

    # Process input files
    resume_text, job_description = service.process_files(resume_path, job_desc_path)

    # Run analysis
    try:
        result = asyncio.run(service.analyze_resume(resume_text, job_description))
        service.show_analysis_result(result)
    except click.ClickException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise click.ClickException("An unexpected error occurred during analysis")


@cli.command()
def start_server():
    uvicorn.run(
        app="src.server:app",
        host=settings.app_host,
        port=settings.app_port,
        loop="uvloop",
        log_config=LOG_CONFIG,
        workers=settings.app_worker_count,
        limit_concurrency=settings.app_limit_concurrency,
        backlog=settings.app_server_backlog,
    )


if __name__ == "__main__":
    cli()
