# Requirements

## Status
`IN PROGRESS` — the provided specification covers AI-agent continuity documentation, not the full Marketing Operations product. Product workflows must be supplied or confirmed before implementation can be considered complete.

## Confirmed project-process requirements
- **FR-PROC-001:** Maintain the required root Markdown continuity files.
- **FR-PROC-002:** Maintain detailed technical documents under `docs/`.
- **FR-PROC-003:** Keep status, backlog, changelog, test status, and handoff synchronized after substantial changes.
- **FR-PROC-004:** Distinguish implemented code from tested/verified behavior.
- **FR-PROC-005:** Enable a new coding agent to resume from repository documentation without the original chat.
- **FR-PROC-006:** Never include secrets in source control or handoff documentation.

## Product functional requirements
`BLOCKED` pending the complete product brief. Do not invent specific marketing workflows. Confirm:
- Target users and their permissions.
- Primary user problem and first end-to-end workflow.
- Required inputs, outputs, and data sources.
- Client/workspace/project concepts, if any.
- Required reports, exports, or integrations.
- Whether AI is required and what tasks it should perform.
- Human approval and audit needs.
- Deployment and data-retention expectations.

## Non-functional requirements
- Clear, actionable error handling.
- Safe configuration and secret handling.
- Testable module boundaries.
- Persistent data if the confirmed workflows require it.
- Documented setup and reproducible verification commands.
- AI/external outputs validated before use.
- No claims of integration or verification without evidence.

## Acceptance criteria
1. The beta's core workflow can be completed end to end.
2. Input validation and failure cases are tested.
3. Persistent state survives application restart when persistence is in scope.
4. External integrations have clear failure behavior and are testable independently.
5. Setup instructions work in a clean environment.
6. Test status records actual results.
7. Another agent can identify the next task using project files alone.

## Beta versus future scope
- **Beta:** To be decided after product requirements are confirmed.
- **Future:** Additional channels, automation, analytics, or integrations only after core workflows are stable and explicitly prioritized.
