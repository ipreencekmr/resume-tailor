import os
import uuid
from pathlib import Path

import gradio as gr

from crew import ResumeTailorCrew

RUNTIME_DIR = Path(os.getenv("RUNTIME_DIR", "runtime")).resolve()
OUTPUTS_DIR = RUNTIME_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_tailored_resume(resume_file: str, target_role: str):
    if not resume_file:
        raise gr.Error("Please upload a resume (.pdf or .docx).")
    if not target_role or not target_role.strip():
        raise gr.Error("Please provide a target role.")

    resume_path = Path(resume_file)
    if resume_path.suffix.lower() not in {".pdf", ".docx"}:
        raise gr.Error("Unsupported file type. Please upload .pdf or .docx.")

    output_name = f"tailored_resume_{uuid.uuid4().hex[:8]}.docx"
    output_path = OUTPUTS_DIR / output_name

    result = ResumeTailorCrew(
        resume_path=str(resume_path),
        target_role=target_role.strip(),
        tech_stack=os.getenv("UI_DEFAULT_TECH_STACK", ""),
        output_path=str(output_path),
    ).run()

    score_text = "N/A"
    if result.score is not None:
        score_text = str(result.score)

    return gr.update(value=result.output_docx, interactive=True), score_text


def build_app():
    with gr.Blocks(title="Tailor your resume") as demo:
        gr.Markdown("# Tailor your resume")

        resume_upload = gr.File(
            label="Attach Resume",
            file_types=[".pdf", ".docx"],
            type="filepath",
        )
        role_input = gr.Textbox(
            label="Provide Role",
            placeholder="e.g., Senior Backend Engineer",
            lines=1,
        )
        generate_btn = gr.Button("Generate", variant="primary")

        download_btn = gr.DownloadButton(
            label="Download Tailored Resume",
            value=None,
            interactive=False,
        )
        ats_score = gr.Textbox(
            label="ATS Score",
            value="",
            interactive=False,
        )

        generate_btn.click(
            fn=generate_tailored_resume,
            inputs=[resume_upload, role_input],
            outputs=[download_btn, ats_score],
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(
        server_name=os.getenv("GRADIO_HOST", "0.0.0.0"),
        server_port=int(os.getenv("GRADIO_PORT", "7860")),
    )
