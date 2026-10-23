# Next Steps — Prioritized Backlog

## MOPS-001 — Install dependencies and smoke-test Streamlit
- **Priority:** P0
- **Status:** `IN PROGRESS`
- **Work:** Install `requirements.txt`; run `streamlit run app.py`; verify navigation and key forms.
- **Acceptance:** App starts without import/runtime errors; all nine pages render.

## MOPS-002 — Verify real local-model inference
- **Priority:** P0
- **Status:** `NOT STARTED`
- **Work:** Start Ollama, pull `qwen3:4b`, confirm Settings reports the model available, generate one strategy and one content draft.
- **Acceptance:** Real output passes Pydantic validation and is saved; offline/malformed errors remain actionable; no cloud fallback.

## MOPS-003 — End-to-end demonstration
- **Priority:** P0
- **Status:** `NOT STARTED`
- **Work:** Follow the README demo using sample clients.
- **Acceptance:** Client → presence → strategy → content → approval → schedule → metrics → report all work and data persists after restart.

## MOPS-004 — Harden application workflows
- **Priority:** P1
- **Status:** `NOT STARTED`
- **Work:** Add automated tests for Ollama failures, persistence across app restart, calendar filters, deletion cascade, and approval revision paths.
- **Acceptance:** Tests pass and edge cases are documented.

## MOPS-005 — Add document ingestion
- **Priority:** P2
- **Status:** `NOT STARTED`
- **Work:** Add restricted file upload and text extraction for supported document formats; treat extracted text as untrusted.
- **Acceptance:** File type/size checks and extraction tests pass.

## MOPS-006 — Decide integration roadmap
- **Priority:** P2
- **Status:** `NOT STARTED`
- **Work:** Evaluate social analytics/publishing APIs and security needs. Do not imply integrations exist before implementing them.
- **Acceptance:** Decisions and limitations are documented; external actions require explicit approval.
