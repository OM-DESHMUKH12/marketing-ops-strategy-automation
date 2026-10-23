# Changelog

## 2026-10-17 — Runnable beta implementation
- Added `app.py` with nine Streamlit pages and a B2B SaaS-style navy/blue theme.
- Added SQLite schema for clients, social accounts, strategies, campaigns, content, revisions, approvals, schedules, metrics, and reports.
- Added client, presence, content, approval, and reporting services.
- Added local Ollama HTTP client, connection/model status, structured response parsing, Pydantic schemas, context builder, strategy/content generation, content review, and report insights.
- Added sample clients, environment template, dependency list, and setup/demo instructions.
- Added Pytest coverage for core service/data behavior.
- Verification: Python compilation passed; `python -m pytest -q` returned 13 passed, 0 failed.
- Not verified: Streamlit runtime (dependency absent in build environment) and live Ollama inference.
- External social APIs and publishing remain intentionally unimplemented.

## 2026-10-17 — Initial continuity scaffold
- Created multi-agent development instructions, project status, backlog, decisions, handoff, test status, and detailed technical docs.

## Strategy-to-calendar automation
- Added a Content Calendar workflow to turn a saved strategy into dated, individual content drafts.
- Each generated post includes a platform-specific caption, CTA/hashtags where produced, an image prompt, and campaign-plan metadata.
- Supports 7-, 14-, and 30-day windows and 2/3/5 posts per week or daily cadence.
- Optional per-post Hugging Face image generation is available, but off by default to conserve free quota.
- Generated content remains Draft and requires human review/approval; no publishing API is connected.
