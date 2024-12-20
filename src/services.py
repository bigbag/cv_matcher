from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

import click
from markitdown import MarkItDown
from request_id_helper import set_request_id
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.analysis import JobAnalyzer
from src.entities import DetailedMatchResult
from src.interfaces import AIClientInterface
from src.logger import TimeLogger, create_logger

logger = create_logger(__name__)


@dataclass
class ResumeAnalysisService:
    client: AIClientInterface
    analyzer: JobAnalyzer = field(init=False, repr=False)
    markitdown: MarkItDown = field(init=False, repr=False)
    console: Console = field(default_factory=Console, init=False)

    def __post_init__(self):
        self.analyzer = JobAnalyzer(client=self.client)
        self.markitdown = MarkItDown()

    @set_request_id()
    def process_files(self, resume_path: Path, job_desc_path: Path) -> Tuple[str, str]:
        """Process input files and return resume and job description texts."""
        with TimeLogger("Processing input files"):
            try:
                resume_text = self.markitdown.convert(str(resume_path)).text_content
                if not resume_text:
                    raise ValueError("Could not extract text from resume")

                job_description = job_desc_path.read_text()
                return resume_text, job_description

            except Exception as e:
                logger.error(f"Error processing files: {str(e)}")
                raise click.ClickException(str(e))

    @set_request_id()
    async def analyze_resume(self, resume_text: str, job_description: str) -> Optional[DetailedMatchResult]:
        """Run the complete resume analysis workflow."""
        try:
            with TimeLogger("Extracting job requirements"):
                job_requirements = await self.analyzer.extract_job_requirements(job_description)
                if not job_requirements:
                    raise ValueError("Could not extract job requirements")

            with TimeLogger("Unifying resume format"):
                unified_resume = await self.analyzer.unify_resume(resume_text)
                if not unified_resume:
                    raise ValueError("Could not unify resume")

            with TimeLogger("Matching resume"):
                return await self.analyzer.match_resume(
                    resume_text=unified_resume,
                    job_description=job_description,
                    job_requirements=job_requirements,
                )

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            raise click.ClickException(str(e))

    def show_analysis_result(self, result: DetailedMatchResult) -> None:
        """Display the analysis results in a rich formatted console output."""
        # Create overall score panel
        score_color = "green" if result.overall_score >= 70 else "yellow" if result.overall_score >= 50 else "red"
        score_text = Text.assemble(
            ("Overall Match Score: ", "bold white"), (f"{result.overall_score}%", f"bold {score_color}")
        )
        self.console.print(Panel(score_text, title="Resume Analysis Result"))

        # Create criteria scores table
        table = Table(title="Detailed Scoring Criteria")
        table.add_column("Criterion", style="cyan")
        table.add_column("Score", justify="right", style="magenta")
        table.add_column("Weight", justify="right", style="yellow")
        table.add_column("Description", style="green")

        for criterion in result.criteria_scores:
            table.add_row(
                criterion.name,
                f"{criterion.score}%" if criterion.score is not None else "N/A",
                f"{criterion.weight}%",
                criterion.description,
            )

        self.console.print(table)

        # Display match reasons
        self.console.print(Panel(result.match_reasons, title="Match Reasons"))

        # Display red flags if any
        if result.red_flags:
            red_flags_table = Table(title="Red Flags", style="red")
            red_flags_table.add_column("Category", style="bold red")
            red_flags_table.add_column("Issues", style="red")

            for category, flags in result.red_flags.items():
                red_flags_table.add_row(category, "\n".join(f"• {flag}" for flag in flags))

            self.console.print(red_flags_table)
