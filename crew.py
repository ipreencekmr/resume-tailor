import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from crewai import Crew, Process

from agents import AgentFactory
from tasks import TaskFactory
from utils.doc_generator import generate_resume_docx
from utils.parser import ResumeParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class ResumeTailorResult:
    output_docx: str
    score: Optional[float]
    missing_keywords: list[str]
    suggestions: list[str]
    raw_outputs: Dict[str, Any]


def _to_dict(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if raw is None:
        return {}
    if isinstance(raw, str):
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text.replace("json", "", 1).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}
    return {}


def _task_output_raw(task: Any) -> Any:
    out = getattr(task, "output", None)
    if out is None:
        return None
    if hasattr(out, "raw"):
        return out.raw
    return str(out)


class ResumeTailorCrew:
    def __init__(
        self,
        resume_path: str,
        target_role: str,
        tech_stack: str,
        output_path: str = "tailored_resume.docx",
    ) -> None:
        self.resume_path = resume_path
        self.target_role = target_role
        self.tech_stack = tech_stack
        self.output_path = output_path

    def run(self) -> ResumeTailorResult:
        logger.info("Starting resume tailoring workflow")

        parsed_resume = ResumeParser().parse(self.resume_path)
        agents = AgentFactory().build_all()
        task_map = TaskFactory().build_all(
            agents=agents,
            parsed_resume=parsed_resume,
            target_role=self.target_role,
            tech_stack=self.tech_stack,
        )
        tasks = TaskFactory.ordered_tasks(task_map)

        crew = Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        crew.kickoff()

        raw_outputs = {name: _task_output_raw(task) for name, task in task_map.items()}
        document_payload = _to_dict(raw_outputs.get("document"))
        ats_payload = _to_dict(raw_outputs.get("ats_optimization"))
        evaluation_payload = _to_dict(raw_outputs.get("evaluation"))

        final_payload = document_payload or ats_payload
        if not final_payload:
            raise RuntimeError("Failed to produce final structured resume payload")

        output_docx = generate_resume_docx(final_payload, self.output_path)

        return ResumeTailorResult(
            output_docx=output_docx,
            score=evaluation_payload.get("overall_score"),
            missing_keywords=evaluation_payload.get("missing_keywords", [])
            if isinstance(evaluation_payload, dict)
            else [],
            suggestions=evaluation_payload.get("improvement_suggestions", [])
            if isinstance(evaluation_payload, dict)
            else [],
            raw_outputs=raw_outputs,
        )
