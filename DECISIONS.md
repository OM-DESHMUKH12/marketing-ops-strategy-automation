# Architecture Decision Record

Decisions are appended chronologically. Replaced decisions should remain visible with their replacement and consequences.

## ADR-001 — Documentation-first continuity
- **Date:** 2026-10-17
- **Status:** Accepted
- **Decision:** Maintain file-based project status, backlog, changelog, decisions, handoff, and test status from the start.
- **Rationale:** AI coding assistants have finite context windows; repository documentation must enable independent continuation.
- **Consequences:** Substantial implementation changes include continuity-document updates.

## ADR-002 — Defer stack selection until requirements are confirmed
- **Date:** 2026-10-17
- **Status:** Accepted
- **Decision:** Do not treat Streamlit, SQLite, Ollama, or any specific model as selected or implemented yet.
- **Rationale:** The supplied specification mentions these as examples but does not establish the actual application requirements or final stack.
- **Consequences:** Stack-specific code is blocked until the beta workflows and deployment constraints are known.

## ADR-003 — Modular monolith as the default direction
- **Date:** 2026-10-17
- **Status:** Proposed
- **Decision:** Prefer a modular monolith with explicit boundaries unless requirements demonstrate a need for distributed services.
- **Rationale:** Simpler local development, testing, deployment, and AI-agent handoff.
- **Consequences:** Revisit after requirements and deployment scale are established.

## ADR-004 — Human approval for external publication
- **Date:** 2026-10-17
- **Status:** Proposed
- **Decision:** Any future workflow that publishes marketing content externally should require explicit human approval by default.
- **Rationale:** Prevent unintended public actions and preserve editorial control.
- **Consequences:** Design approval state and audit trail if publication features enter beta scope.

## ADR-005 — Distinguish account assessment states
- **Date:** 2026-10-17
- **Status:** Proposed
- **Decision:** If social account discovery is included, represent `Present`, `Absent`, `Unknown`, and `Not Assessed` separately.
- **Rationale:** Lack of evidence must not be misrepresented as evidence of absence.
- **Consequences:** Schema and UI should preserve uncertainty explicitly if this workflow is confirmed.
