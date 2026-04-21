---
title: Resume Tailor
emoji: 📄
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "6.13.0"
python_version: "3.12"
app_file: app.py
pinned: false
---

# Resume Tailor (CrewAI)

Production-oriented multi-agent resume tailoring pipeline using CrewAI.

<img width="1465" height="710" alt="Screenshot 2026-04-21 at 10 48 15 PM" src="https://github.com/user-attachments/assets/6ab1891f-663a-4a4b-bf6a-0d227db05bc8" />


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
  app.py
  gradio_app.py
  .github/
    workflows/
      deploy-hf-space.yml
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

## Script Commands

You can use short script-style commands:

```bash
make api   # backend only
make ui    # frontend only
make dev   # backend + frontend together
```

## Deploy And Run On Hugging Face Spaces (GitHub Actions)

This repo includes an automated deploy workflow:
- [.github/workflows/deploy-hf-space.yml](/Users/ipreencekmr/Documents/resume-tailor/.github/workflows/deploy-hf-space.yml)

Target Space:
- `ipreencekmr/resume-tailor`
- URL: [https://huggingface.co/spaces/ipreencekmr/resume-tailor](https://huggingface.co/spaces/ipreencekmr/resume-tailor)

### 1. Create Hugging Face token (one-time)

1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click `New token`
3. Create a token with write access to Spaces
4. Copy the generated token (`hf_...`)

### 2. Add GitHub repository secret

In your GitHub repo: `Settings -> Secrets and variables -> Actions -> New repository secret`

- `HF_TOKEN`: Hugging Face User Access Token (write access to Spaces)

### 3. Add runtime secret in Hugging Face Space settings

In Space `ipreencekmr/resume-tailor` -> `Settings -> Variables and secrets`, add:
- Required:
  - `OPENAI_API_KEY`
- Optional:
  - `OPENAI_MODEL_DEFAULT`
  - `OPENAI_MODEL_REASONING`
  - `UI_DEFAULT_TECH_STACK`

### 4. Deploy from GitHub

- Push to `main`, or
- Go to `Actions -> Deploy To Hugging Face Space -> Run workflow`

The workflow uploads this repo to your Space and updates it automatically.

### 5. Access the live application

Open:
- [https://huggingface.co/spaces/ipreencekmr/resume-tailor](https://huggingface.co/spaces/ipreencekmr/resume-tailor)

Once the Space status is `Running`, the Gradio app UI is available with:
- Resume upload
- Role input
- Generate button
- ATS score output
- Download tailored resume after successful generation

### 6. If the app does not load

Check:
1. GitHub Action run logs (deployment step success)
2. Hugging Face Space `Build Logs` / `Runtime Logs`
3. Presence of `OPENAI_API_KEY` in Space secrets

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
