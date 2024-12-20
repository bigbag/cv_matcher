import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.entities import DetailedMatchResult, JobRequirements, ScoringCriterion
from src.interfaces import AIClientInterface
from src.logger import create_logger
from src.promts import EXTRACT_REQUIREMENTS_PROMT, MATCH_REASONS_PROMT, RESUME_INIFIRED_PROMT, RESUME_WEBSITE_PROMT

logger = create_logger(__name__)


def create_scoring_criteria(job_requirements: JobRequirements) -> List[ScoringCriterion]:
    """Create a list of scoring criteria based on job requirements."""
    return [
        ScoringCriterion(
            name='Language Proficiency',
            key='language_proficiency',
            weight=job_requirements.emphasis.language_proficiency_weight,
            description='Evaluate candidate\'s proficiency in required languages',
            factors=['Proficiency in required languages', 'Multilingual abilities relevant to the job'],
        ),
        ScoringCriterion(
            name='Education Level',
            key='education_level',
            weight=job_requirements.emphasis.education_weight,
            description='Evaluate candidate\'s education level and relevance',
            factors=[
                'Highest education level attained',
                'Relevance of degree to the job',
                'Alternative education paths',
            ],
        ),
        ScoringCriterion(
            name='Experience',
            key='experience',
            weight=job_requirements.emphasis.experience_weight,
            description='Evaluate years and quality of experience',
            factors=['Total years of relevant experience', 'Quality of previous roles', 'Significant achievements'],
        ),
        ScoringCriterion(
            name='Technical Skills',
            key='technical_skills',
            weight=job_requirements.emphasis.technical_skills_weight,
            description='Evaluate technical skills match',
            factors=['Required skills proficiency', 'Optional skills coverage', 'Learning ability indicators'],
        ),
        ScoringCriterion(
            name='Certifications',
            key='certifications',
            weight=job_requirements.emphasis.certifications_weight,
            description='Evaluate relevant certifications',
            factors=['Required certifications', 'Additional relevant certifications', 'Equivalent experience'],
        ),
        ScoringCriterion(
            name='Soft Skills',
            key='soft_skills',
            weight=job_requirements.emphasis.soft_skills_weight,
            description='Evaluate demonstrated soft skills',
            factors=['Communication abilities', 'Team collaboration', 'Leadership potential'],
        ),
    ]


@dataclass
class ResumeProcessor:
    """Handles resume-related operations."""

    client: AIClientInterface

    async def unify_resume(self, resume_text: str) -> str:
        """Standardize the resume format."""
        return await self.client.run(
            prompt=RESUME_INIFIRED_PROMT.format(resume_text=resume_text),
            max_tokens=4092,
        )

    async def get_website(self, resume_text: str) -> str:
        """Extract website from resume."""
        return await self.client.run(
            prompt=RESUME_WEBSITE_PROMT.format(resume_text=resume_text),
            max_tokens=100,
        )


@dataclass
class CriteriaEvaluator:
    """Handles evaluation of individual criteria."""

    client: AIClientInterface

    async def evaluate_criterion(
        self, criterion: ScoringCriterion, resume_text: str, job_requirements: JobRequirements
    ) -> int:
        """Evaluate a single criterion and return a score."""
        prompt = self._create_evaluation_prompt(criterion, resume_text, job_requirements)
        try:
            response = await self.client.run(prompt)
            return self._parse_score(response, criterion.name)
        except Exception as e:
            logger.error(f"Error evaluating criterion {criterion.name}: {str(e)}")
            return 0

    def _create_evaluation_prompt(
        self, criterion: ScoringCriterion, resume_text: str, job_requirements: JobRequirements
    ) -> str:
        return f"""
        Evaluate the candidate's resume for the criterion: "{criterion.name}"
        
        Criterion Description: {criterion.description}
        
        Factors to consider:
        {', '.join(criterion.factors)}
        
        Job Requirements:
        {job_requirements.model_dump_json()}
        
        Resume:
        {resume_text}
        
        Provide your evaluation as an integer score from 0 to 100.
        Only return the integer score, no explanation needed.
        """

    def _parse_score(self, response: str, criterion_name: str) -> int:
        try:
            return max(0, min(100, int(re.findall(r'-?\d+', response)[0])))
        except (IndexError, ValueError):
            logger.error(f"Could not parse score from response for {criterion_name}: {response}")
            return 0


@dataclass
class RedFlagAnalyzer:
    """Analyzes and categorizes red flags in the evaluation."""

    def analyze(self, criteria: List[ScoringCriterion]) -> Dict[str, List[str]]:
        """Identify red flags based on criteria scores and weights."""
        red_flags = {"low": [], "medium": [], "high": []}

        for criterion in criteria:
            if criterion.score is None:
                continue

            if criterion.score < 30 and criterion.weight >= 30:
                red_flags["high"].append(f"Low {criterion.name}")
            elif criterion.score < 50 and criterion.weight >= 20:
                red_flags["medium"].append(f"Below average {criterion.name}")
            elif criterion.score < 70:
                red_flags["low"].append(f"Improvement needed in {criterion.name}")

        return red_flags


@dataclass
class JobAnalyzer:
    """Main class for analyzing job requirements and matching resumes."""

    client: AIClientInterface
    _resume_processor: ResumeProcessor = field(init=False, repr=False)
    _criteria_evaluator: CriteriaEvaluator = field(init=False, repr=False)
    _red_flag_analyzer: RedFlagAnalyzer = field(init=False, repr=False)

    def __post_init__(self):
        self._resume_processor = ResumeProcessor(self.client)
        self._criteria_evaluator = CriteriaEvaluator(self.client)
        self._red_flag_analyzer = RedFlagAnalyzer()

    async def unify_resume(self, resume_text: str) -> str:
        """Standardize the resume format."""
        return await self._resume_processor.unify_resume(resume_text)

    async def extract_job_requirements(self, job_description: str) -> Optional[JobRequirements]:
        """Extract structured requirements from job description."""
        return await self.client.run(
            prompt=EXTRACT_REQUIREMENTS_PROMT.format(job_description=job_description),
            result_type=JobRequirements,
        )

    async def match_resume(
        self,
        resume_text: str,
        job_description: str,
        job_requirements: JobRequirements,
    ) -> DetailedMatchResult:
        """Match a resume against job requirements and provide detailed analysis."""
        criteria = create_scoring_criteria(job_requirements)
        total_weight = sum(c.weight for c in criteria)

        # Evaluate each criterion
        for criterion in criteria:
            criterion.score = await self._criteria_evaluator.evaluate_criterion(
                criterion, resume_text, job_requirements
            )

        # Calculate overall score
        overall_score = (
            sum(criterion.score * criterion.weight for criterion in criteria) // total_weight if total_weight > 0 else 0
        )

        # Generate match reasons
        match_reasons = await self.client.run(
            prompt=MATCH_REASONS_PROMT.format(
                criteries=', '.join(f'{c.name}: {c.score}' for c in criteria),
                resume_text=resume_text,
                job_description=job_description,
            ),
        )

        website = await self._resume_processor.get_website(resume_text)
        red_flags = self._red_flag_analyzer.analyze(criteria)

        return DetailedMatchResult(
            overall_score=overall_score,
            criteria_scores=criteria,
            match_reasons=match_reasons.strip(),
            website=website.strip(),
            red_flags=red_flags,
        )
