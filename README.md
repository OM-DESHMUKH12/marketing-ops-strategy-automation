# AI-Powered Marketing Operations Platform

A runnable beta prototype for digital marketing agencies. Built with Python, Streamlit, SQLite, Pydantic, Pandas, Plotly, Pytest, and local Ollama inference.

## Beta capabilities

- Client onboarding and editable brand/company profiles
- Per-client social presence assessments with distinct `Present`, `Absent`, `Unknown`, and `Not assessed` states
- Client-context builder used by AI prompts
- Local Ollama marketing strategy generation with Pydantic validation and persistence
- Local Ollama content generation for social posts, carousels, short-form video scripts, LinkedIn thought leadership, and campaign content
- Cloud image generation in AI Content Studio through the public Hugging Face Stable Diffusion 3.5 Large Space
- Editable saved drafts, calendar filtering, revisions, duplication, and deletion
- Human approval workflow with transition validation and approval history
- Manual performance metric entry, Plotly analytics, and reports derived from saved metrics
- Settings page for local model connection/model status
- Optional sample clients, clearly marked as examples
- Pytest coverage for core persistence, presence, content, approvals, analytics, and response parsing

## Requirements

- Python 3.10+ (developed with Python 3.13; install versions supported by your environment)
- Ollama installed locally
- Sufficient memory for your chosen model
- Qwen3 4B recommended by the project brief; other Ollama model names may be configured

## Install

From the project directory:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure values if needed:

```dotenv
MARKETING_OPS_DB=data/marketing_ops.db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
OLLAMA_TIMEOUT_SECONDS=120
```

## Start local AI

Install Ollama from its official website, start the local service, then pull the configured model:

```bash
ollama pull qwen3:4b
ollama list
```

The default Ollama API endpoint is `http://localhost:11434`. Ensure the model name in `.env` matches `ollama list`. The app checks `/api/tags` and provides setup guidance if Ollama or the model is missing.

No cloud LLM fallback is used. If local inference fails, the app reports an actionable error and does not save placeholder AI output.

## Cloud image generation

The AI Content Studio includes a separate Hugging Face image-generation panel. Install dependencies with `pip install -r requirements.txt`, then use the image prompt and **Generate image** button. Generated assets are saved under `data/generated_assets/` and can be downloaded from the UI.

The integration uses the public `stabilityai/stable-diffusion-3.5-large` Space and its `/infer` endpoint. Public Space availability, queue time, and free usage limits are controlled by Hugging Face. Image generation sends the prompt to the cloud. Generated images can misrepresent real industrial products; verify them before publishing. This feature does not automatically attach images to saved content items or publish anything.

## Run the app

```bash
streamlit run app.py
```

SQLite initializes automatically at `data/marketing_ops.db` (or the path set by `MARKETING_OPS_DB`). The database is excluded from Git.

## Run tests

```bash
pytest -q
```

The tests use isolated temporary SQLite databases and do not require Ollama. A successful unit test run does **not** prove real model inference works. Verify the local inference separately in Settings and generate at least one strategy or content draft.

## Suggested demo walkthrough

1. Open **Settings** and check the Ollama connection/model state.
2. Click **Load sample clients** to add two editable demonstration businesses.
3. Open **Clients** and review or update the manufacturing or fitness profile.
4. Open **Digital Presence Audit**. Record LinkedIn as Present for the manufacturer and Instagram as Present for the fitness studio; record any missing accounts explicitly as Absent only after assessment.
5. Open **Marketing Strategy**, select a client, configure an objective and ask the local model to generate a strategy. Confirm it is saved.
6. Open **AI Content Studio**, select that client and strategy, generate a LinkedIn thought-leadership post or Instagram reel, edit the copy, and save it.
7. Open **Approvals**, submit the draft for review, then approve or reject it with a note.
8. Open **Content Calendar** and mark approved content as Scheduled. This means ready for external scheduling; no post is published by this prototype.
9. Open **Analytics and Reports**, enter actual metrics (or explicitly labelled sample values), and generate a report from the saved records.

## Navigation

1. Dashboard
2. Clients
3. Digital Presence Audit
4. Marketing Strategy
5. AI Content Studio
6. Content Calendar
7. Approvals
8. Analytics and Reports
9. Settings

## Data and safety notes

- Client data and generated content persist in SQLite after restart.
- Account presence is user-entered; no social platform APIs are connected for independent verification.
- Website URLs are stored but not crawled. Competitor fields are user-supplied; no competitor research is fabricated.
- AI drafts are generated locally and must be reviewed by a human.
- Publishing integrations are not configured. The app does not claim a post was externally scheduled or published.
- Analytics only use saved metrics. Engagement rate is defined as `(likes + comments + shares) / impressions × 100`; it is unavailable when impressions are zero.
- Sample client content is illustrative and must be verified before being used externally.
- This is a beta prototype, not a production-ready multi-tenant SaaS. Authentication, role-based access, agency isolation, external publishing, and automated social API integrations are not implemented.

## Troubleshooting

**Ollama offline:** Start Ollama and check `http://localhost:11434/api/tags`; then retry from Settings.

**Model missing:** Run `ollama pull qwen3:4b`, or change `OLLAMA_MODEL` to a model installed locally and restart Streamlit.

**Slow generation:** Increase `OLLAMA_TIMEOUT_SECONDS`, close memory-heavy apps, or select a smaller model supported by your machine.

**Invalid model output:** The app validates JSON and Pydantic schemas. Retry the request; invalid responses are not saved as AI-generated content.

**Database path:** Set `MARKETING_OPS_DB` before starting the app. Stop Streamlit before manually moving or replacing the database file.

## Project continuity

Read `AGENTS.md`, `PROJECT_STATUS.md`, `NEXT_STEPS.md`, `HANDOFF.md`, and `docs/` when continuing development. Update status and test reports with actual results.
