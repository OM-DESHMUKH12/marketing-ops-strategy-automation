# Immediate Handoff

## Project snapshot
- **Product:** AI-Powered Marketing Operations Automation Platform.
- **Phase:** Runnable beta source implementation; runtime/model verification still pending.
- **Main entry point:** `app.py`.
- **Stack:** Python, Streamlit, SQLite, Pydantic, Pandas, Plotly, Pytest, Ollama HTTP API.

## Implemented
- Nine Streamlit navigation pages.
- SQLite schema and automatic initialization.
- Client profile CRUD and search.
- Social presence records with Present/Absent/Unknown/Not assessed distinctions.
- Client context builder.
- Ollama local inference client with connection/model checks and no cloud fallback.
- Pydantic-validated strategy and content generation, persisted only after successful validation.
- Editable content drafts, calendar filtering, revision history, duplicate/delete.
- Explicit approval/rejection transitions and approval history.
- Approved-only scheduling state; no external publishing claim.
- Manually entered metrics, engagement-rate calculation, saved reports.
- Two sample clients and a Pytest suite.

## Verification
- Python compilation: passed.
- `python -m pytest -q`: 13 passed, 0 failed.
- Streamlit launch: not run; Streamlit was not installed in the build environment.
- Real Ollama inference: not run; local endpoint/model status unknown.

## Exact next steps
1. Create a virtual environment and `pip install -r requirements.txt`.
2. Install/start Ollama and run `ollama pull qwen3:4b` (or configure another installed model in `.env`).
3. Run `pytest -q`.
4. Run `streamlit run app.py` and verify all nine pages manually.
5. From Settings, confirm Ollama and the configured model show as available.
6. Load sample clients, run a real strategy generation, generate/save a content draft, approve it, schedule it, enter metric data, and create a report.
7. Fix any runtime or model-specific issues discovered, then update `TEST_STATUS.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, and this handoff.

## Important limitations
- No authentication, authorization, or multi-tenant agency isolation.
- No social platform API, automated account verification, website crawling, or external publishing.
- Analytics require manually entered metrics.
- Document ingestion deferred.
- Not production-ready; do not expose to untrusted networks.

## Next AI instructions
Read `AGENTS.md`, then this file, `PROJECT_STATUS.md`, `NEXT_STEPS.md`, and `TEST_STATUS.md`. Inspect actual source and test output before making claims. Preserve working behavior and update continuity docs after changes.
