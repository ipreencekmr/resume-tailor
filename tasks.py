import json
from pathlib import Path
from typing import Any, Dict, List

import yaml
from crewai import Task


class TaskFactory:
    def __init__(self, config_path: str = "config/tasks.yml") -> None:
        self.config_path = Path(config_path)
        self.config = self._load_yaml(self.config_path)

    @staticmethod
    def _load_yaml(path: Path) -> Dict[str, dict]:
        if not path.exists():
            raise FileNotFoundError(f"Missing config file: {path}")
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _render(self, key: str, **kwargs: Any) -> str:
        template = self.config[key]["description"]
        return template.format(**kwargs)

    def build_all(
        self,
        agents: Dict[str, Any],
        parsed_resume: Dict[str, Any],
        target_role: str,
        tech_stack: str,
    ) -> Dict[str, Task]:
        resume_payload = json.dumps(parsed_resume, indent=2)

        ingestion_task = Task(
            description=self._render("ingestion", resume_payload=resume_payload),
            expected_output=self.config["ingestion"]["expected_output"],
            agent=agents["ingestion"],
        )

        profiling_task = Task(
            description=self._render("profiling"),
            expected_output=self.config["profiling"]["expected_output"],
            context=[ingestion_task],
            agent=agents["profiling"],
        )

        role_task = Task(
            description=self._render(
                "role_intelligence",
                target_role=target_role,
                tech_stack=tech_stack,
            ),
            expected_output=self.config["role_intelligence"]["expected_output"],
            agent=agents["role_intelligence"],
        )

        tailoring_task = Task(
            description=self._render("tailoring"),
            expected_output=self.config["tailoring"]["expected_output"],
            context=[ingestion_task, profiling_task, role_task],
            agent=agents["tailoring"],
        )

        ats_task = Task(
            description=self._render("ats_optimization"),
            expected_output=self.config["ats_optimization"]["expected_output"],
            context=[tailoring_task, role_task],
            agent=agents["ats_optimization"],
        )

        evaluation_task = Task(
            description=self._render("evaluation"),
            expected_output=self.config["evaluation"]["expected_output"],
            context=[ats_task, role_task],
            agent=agents["evaluation"],
        )

        document_task = Task(
            description=self._render("document"),
            expected_output=self.config["document"]["expected_output"],
            context=[ats_task, evaluation_task],
            agent=agents["document"],
        )

        return {
            "ingestion": ingestion_task,
            "profiling": profiling_task,
            "role_intelligence": role_task,
            "tailoring": tailoring_task,
            "ats_optimization": ats_task,
            "evaluation": evaluation_task,
            "document": document_task,
        }

    @staticmethod
    def ordered_tasks(task_map: Dict[str, Task]) -> List[Task]:
        return [
            task_map["ingestion"],
            task_map["profiling"],
            task_map["role_intelligence"],
            task_map["tailoring"],
            task_map["ats_optimization"],
            task_map["evaluation"],
            task_map["document"],
        ]
