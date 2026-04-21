import os
import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from crew import ResumeTailorCrew

app = FastAPI(title="Resume Tailor API", version="1.0.0")

RUNTIME_DIR = Path(os.getenv("RUNTIME_DIR", "runtime")).resolve()
UPLOADS_DIR = RUNTIME_DIR / "uploads"
OUTPUTS_DIR = RUNTIME_DIR / "outputs"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


class TailorRequest(BaseModel):
    resume_path: str = Field(..., description="Absolute path to resume file (.pdf/.docx)")
    target_role: str = Field(..., description="Target role to tailor for")
    tech_stack: str = Field(..., description="Target tech stack")
    output_path: str = Field(default="tailored_resume.docx", description="Output DOCX path")


class TailorResponse(BaseModel):
    output_docx: str
    download_url: str | None = None
    score: float | None = None
    missing_keywords: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


def _ensure_docx_filename(filename: str) -> str:
    cleaned = Path(filename).name.strip() or "tailored_resume.docx"
    if not cleaned.lower().endswith(".docx"):
        cleaned = f"{cleaned}.docx"
    return cleaned


def _build_unique_output_path(filename: str) -> Path:
    desired = OUTPUTS_DIR / _ensure_docx_filename(filename)
    if not desired.exists():
        return desired
    stem = desired.stem
    suffix = desired.suffix
    return OUTPUTS_DIR / f"{stem}_{uuid.uuid4().hex[:8]}{suffix}"


def _is_supported_resume(filename: str) -> bool:
    suffix = Path(filename).suffix.lower()
    return suffix in {".pdf", ".docx"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/tailor", response_model=TailorResponse)
def tailor(req: TailorRequest) -> TailorResponse:
    try:
        result = ResumeTailorCrew(
            resume_path=req.resume_path,
            target_role=req.target_role,
            tech_stack=req.tech_stack,
            output_path=req.output_path,
        ).run()
        return TailorResponse(
            output_docx=result.output_docx,
            download_url=None,
            score=result.score,
            missing_keywords=result.missing_keywords,
            suggestions=result.suggestions,
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/tailor/upload", response_model=TailorResponse)
def tailor_upload(
    target_role: str = Form(...),
    tech_stack: str = Form(...),
    resume_file: UploadFile = File(...),
    output_filename: str = Form("tailored_resume.docx"),
) -> TailorResponse:
    if not _is_supported_resume(resume_file.filename or ""):
        raise HTTPException(status_code=400, detail="Only .pdf and .docx resumes are supported")

    upload_ext = Path(resume_file.filename or "").suffix.lower()
    upload_path = UPLOADS_DIR / f"{uuid.uuid4().hex}{upload_ext}"
    output_path = _build_unique_output_path(output_filename)

    try:
        with upload_path.open("wb") as f:
            shutil.copyfileobj(resume_file.file, f)

        result = ResumeTailorCrew(
            resume_path=str(upload_path),
            target_role=target_role,
            tech_stack=tech_stack,
            output_path=str(output_path),
        ).run()

        return TailorResponse(
            output_docx=result.output_docx,
            download_url=f"/download/{Path(result.output_docx).name}",
            score=result.score,
            missing_keywords=result.missing_keywords,
            suggestions=result.suggestions,
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        try:
            upload_path.unlink(missing_ok=True)
        except Exception:
            pass


@app.get("/download/{file_name}")
def download_file(file_name: str):
    safe_name = Path(file_name).name
    target = OUTPUTS_DIR / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=target,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=safe_name,
    )
