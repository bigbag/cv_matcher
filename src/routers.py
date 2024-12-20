import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.client import AIClient
from src.entities import DetailedMatchResult, ModelType, PingResponse
from src.logger import create_logger
from src.services import ResumeAnalysisService

logger = create_logger(__name__)
router = APIRouter()


@router.get(
    "/ping",
    tags=["system"],
    summary="Health check endpoint",
    response_model=PingResponse,
)
def get_ping():
    return PingResponse()


async def save_upload_file(upload_file: UploadFile) -> Path:
    """Save an uploaded file to a temporary location and return its path."""
    try:
        suffix = Path(upload_file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await upload_file.read()
            tmp_file.write(content)
            return Path(tmp_file.name)
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}")
        raise HTTPException(status_code=400, detail="Could not process uploaded file")


@router.post(
    "/analyze_resume",
    tags=["ai"],
    summary="Analyze a resume against a job description",
    response_model=DetailedMatchResult,
)
async def analyze_resume(
    resume_file: UploadFile = File(...),
    job_description_file: UploadFile = File(...),
):
    """
    Analyze a resume against a job description using uploaded files.

    Args:
        resume_file: Uploaded resume file
        job_description_file: Uploaded job description file

    Returns:
        DetailedMatchResult: Analysis results including match score and details
    """

    # Initialize the AI client and service
    client = AIClient(model_type=ModelType.OPENAI, max_tokens=2000)
    service = ResumeAnalysisService(client)

    try:
        # Save uploaded files to temporary locations
        resume_path = await save_upload_file(resume_file)
        job_desc_path = await save_upload_file(job_description_file)

        # Process the files and get text content
        resume_text, job_description = service.process_files(resume_path, job_desc_path)

        # Clean up temporary files
        resume_path.unlink()
        job_desc_path.unlink()

        # Analyze the resume
        result = await service.analyze_resume(resume_text, job_description)
        if not result:
            raise HTTPException(status_code=500, detail="Analysis failed to produce results")
        return result
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
