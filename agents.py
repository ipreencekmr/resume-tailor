import logging
import os
from pathlib import Path
from typing import Dict

import yaml
from crewai import Agent

try:
    from crewai import LLM
except ImportError:  # pragma: no cover
    LLM = None

logger = logging.getLogger(__name__)


class AgentFactory:
    def __init__(self, config_path: str = "config/agents.yml") -> None:
        self.config_path = Path(config_path)
        self.config = self._load_yaml(self.config_path)
        self.default_model = os.getenv(
            "OPENAI_MODEL_DEFAULT",
            os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        )
        self.reasoning_model = os.getenv("OPENAI_MODEL_REASONING", "gpt-4.1")
        self._llm_cache: Dict[str, object] = {}

    @staticmethod
    def _load_yaml(path: Path) -> Dict[str, dict]:
        if not path.exists():
            raise FileNotFoundError(f"Missing config file: {path}")
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _build_llm(self, model: str):
        if LLM is None:
            logger.warning("CrewAI LLM class unavailable, using model string fallback")
            return model
        return LLM(model=model, temperature=0)

    def _resolve_model(self, key: str, cfg: Dict[str, object]) -> str:
        explicit_model = cfg.get("model")
        if isinstance(explicit_model, str) and explicit_model.strip():
            return explicit_model.strip()
        if bool(cfg.get("reasoning_intensive", False)):
            return self.reasoning_model
        return self.default_model

    def _create(self, key: str) -> Agent:
        cfg = self.config[key]
        model = self._resolve_model(key, cfg)
        llm = self._llm_cache.get(model)
        if llm is None:
            llm = self._build_llm(model)
            self._llm_cache[model] = llm
        logger.info("Configured agent '%s' with model '%s'", key, model)
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

    def build_all(self) -> Dict[str, Agent]:
        return {
            "ingestion": self._create("ingestion"),
            "profiling": self._create("profiling"),
            "role_intelligence": self._create("role_intelligence"),
            "tailoring": self._create("tailoring"),
            "ats_optimization": self._create("ats_optimization"),
            "evaluation": self._create("evaluation"),
            "document": self._create("document"),
        }
