import logging
import re
from pathlib import Path
from typing import Any, Dict

import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)


class ResumeParser:
    """Parse PDF/DOCX resumes into normalized input payloads."""

    SECTION_PATTERNS = [
        "summary",
        "professional summary",
        "skills",
        "experience",
        "work experience",
        "projects",
        "education",
        "certifications",
    ]

    def parse(self, resume_path: str) -> Dict[str, Any]:
        path = Path(resume_path)
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found: {resume_path}")

        suffix = path.suffix.lower()
        if suffix == ".pdf":
            raw_text = self._read_pdf(path)
        elif suffix == ".docx":
            raw_text = self._read_docx(path)
        else:
            raise ValueError("Unsupported resume format. Use .pdf or .docx")

        if not raw_text.strip():
            raise ValueError("Parsed resume is empty")

        sections = self._extract_sections(raw_text)
        return {
            "source_file": str(path),
            "raw_text": raw_text,
            "detected_sections": sections,
        }

    def _read_pdf(self, path: Path) -> str:
        logger.info("Parsing PDF resume: %s", path)
        pages = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                pages.append(page_text)
        return "\n".join(pages)

    def _read_docx(self, path: Path) -> str:
        logger.info("Parsing DOCX resume: %s", path)
        doc = Document(path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    def _extract_sections(self, raw_text: str) -> Dict[str, str]:
        normalized_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        if not normalized_lines:
            return {"full_text": raw_text}

        section_map: Dict[str, str] = {}
        current_key = "full_text"
        buffer = []

        for line in normalized_lines:
            lowered = re.sub(r"[^a-zA-Z ]", "", line).strip().lower()
            if lowered in self.SECTION_PATTERNS:
                if buffer:
                    section_map[current_key] = "\n".join(buffer).strip()
                    buffer = []
                current_key = lowered.replace(" ", "_")
                continue
            buffer.append(line)

        if buffer:
            section_map[current_key] = "\n".join(buffer).strip()

        return section_map
