# Resume Tailor (CrewAI)

Production-oriented multi-agent resume tailoring pipeline using CrewAI.

## Features
- Parses PDF or DOCX resumes
- Builds structured candidate profile
- Analyzes target role and tech stack
- Rewrites content without fabricating experience
- Optimizes for ATS keyword alignment
- Evaluates fit score and missing keywords
- Generates ATS-friendly `tailored_resume.docx`
- Supports CLI and FastAPI (served with Uvicorn)

## Project Structure

```text
resume-tailor/
  config/
    agents.yml
    tasks.yml
  utils/
    __init__.py
    parser.py
    doc_generator.py
  agents.py
  tasks.py
  crew.py
  api.py
  gradio_app.py
  scripts/
    start_api.sh
    start_ui.sh
    start_all.sh
  Makefile
  main.py
  requirements.txt
  README.md
```

## Python Setup (Mandatory)

Use Python 3.10 to 3.13 (CrewAI currently does not support Python 3.14 runtime dependencies cleanly).

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Or use:

```bash
make setup
# or force a specific interpreter:
make setup PYTHON=python3.12
```

Set your OpenAI key:

```bash
export OPENAI_API_KEY="your_key_here"
export OPENAI_MODEL_DEFAULT="gpt-4.1-mini"
export OPENAI_MODEL_REASONING="gpt-4.1"
```

Model routing:
- `gpt-4.1` is used for reasoning-intensive agents (`role_intelligence`, `tailoring`, `evaluation`).
- `gpt-4.1-mini` is used for all other agents.
- You can still force an exact model per agent in `config/agents.yml` using `model: ...`.

## CLI Usage

```bash
python main.py \
  --resume /absolute/path/to/resume.pdf \
  --role "Senior Backend Engineer" \
  --tech-stack "Python, FastAPI, AWS, PostgreSQL" \
  --output tailored_resume.docx
```

CLI output includes:
- final file path
- evaluation score (if produced)
- missing keywords
- improvement suggestions

## API Usage (Uvicorn + FastAPI)

Run server:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
# or
make api
```
Set `API_RELOAD=1` in `.env` if you want auto-reload with script commands.

Health check:

```bash
curl http://localhost:8000/health
```

Tailor resume:

```bash
curl -X POST http://localhost:8000/tailor \
  -H "Content-Type: application/json" \
  -d '{
    "resume_path": "/absolute/path/to/resume.docx",
    "target_role": "ML Engineer",
    "tech_stack": "Python, LLMs, LangChain, Docker",
    "output_path": "tailored_resume.docx"
  }'
```

Upload resume (UI-friendly `multipart/form-data`):

```bash
curl -X POST http://localhost:8000/tailor/upload \
  -F "resume_file=@/absolute/path/to/resume.pdf" \
  -F "target_role=Senior Backend Engineer" \
  -F "tech_stack=Python, FastAPI, AWS, PostgreSQL" \
  -F "output_filename=tailored_resume.docx"
```

The upload response includes a `download_url` (example: `/download/tailored_resume_abc123.docx`).
You can fetch it with:

```bash
curl -L "http://localhost:8000/download/<file_name_from_response>" -o tailored_resume.docx
```

## Gradio UI

Run UI:

```bash
python gradio_app.py
# or
make ui
```

Open the URL shown in terminal (default `http://0.0.0.0:7860`).

UI includes:
- Title: `Tailor your resume`
- Attach Resume: upload `.pdf` or `.docx`
- Provide Role: input field
- Action Button: `Generate`
- Download Tailored Resume: disabled until successful generation
- ATS Score: score from generated resume output

## Script Commands (Like package.json)

You can use short script-style commands:

```bash
make api   # backend only
make ui    # frontend only
make dev   # backend + frontend together
```

## Sample Input / Output

Sample input values:
- Resume: `candidate_resume.pdf`
- Role: `Senior Data Engineer`
- Tech stack: `Python, Spark, Airflow, AWS, dbt`

Expected output artifacts:
- `tailored_resume.docx`
- Console/API scoring summary (fit score, missing keywords, recommendations)

## Notes
- The pipeline uses `Process.sequential` in CrewAI.
- Agent prompts and task definitions are driven by YAML under `config/`.
- DOCX output avoids tables/graphics for ATS compatibility.
