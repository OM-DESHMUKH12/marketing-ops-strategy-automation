# Instructions for Coding Agents

## Mission
Develop the Marketing Operations project incrementally, preserving working behavior and maintaining file-based project memory so another agent can resume without the original conversation.

## Before changing anything
1. Read `PROJECT_STATUS.md`, `NEXT_STEPS.md`, and `HANDOFF.md`.
2. Inspect the actual repository, configuration, and Git status.
3. Read relevant technical documents under `docs/`.
4. Compare documentation claims with source code and tests.
5. Identify the highest-priority unfinished task.

## Project state and stack
The supplied specification does not confirm an application stack or complete product requirements. The repository is currently a documentation-first scaffold. Do not assume Streamlit, SQLite, Ollama, or any particular model has been implemented or selected. Record stack decisions in `DECISIONS.md` before depending on them.

## Architecture principles
- Prefer a modular monolith until measured needs justify otherwise.
- Keep UI, application/use-case logic, domain rules, persistence, and external integrations separated.
- Keep provider-specific AI and external API code behind small interfaces.
- Validate external/model output before it reaches persistent state or user-facing actions.
- Require explicit human approval before publishing or performing consequential external marketing actions.
- Represent social-account checks with distinct `Present`, `Absent`, `Unknown`, and `Not Assessed` states; do not collapse unknown into absent.

## Coding conventions
- Follow the established style and existing patterns; add type hints where appropriate for Python.
- Keep functions focused and names descriptive.
- Validate inputs at boundaries and handle failures explicitly.
- Do not silently swallow exceptions. Log safe, actionable context without secrets or personal data.
- Keep configuration external to source code and provide safe defaults.
- Add or update tests for behavior changes.

## Preserve existing work
- Inspect implementations before editing.
- Do not rewrite working modules just to match personal preference.
- Avoid broad refactors unrelated to the current task.
- Never discard user changes or reset a working tree without explicit authorization.

## Security
- Never commit API keys, passwords, access tokens, private customer data, or local environment files.
- Use `.env.example` for documented variable names with placeholder values only.
- Validate and sanitize untrusted inputs, including model output.
- Use least-privilege credentials and protect logs and stored client data.

## Verification and documentation
- Run the smallest relevant tests first, then broader tests where feasible.
- Record commands and actual results; never invent test outcomes.
- If tests cannot run, state why.
- After substantial changes, update `PROJECT_STATUS.md`, `NEXT_STEPS.md`, `CHANGELOG.md`, `TEST_STATUS.md`, and `HANDOFF.md`; update technical docs affected by the change.
- Use explicit status values: `NOT STARTED`, `IN PROGRESS`, `IMPLEMENTED`, `VERIFIED`, `BLOCKED`.

## Handoff protocol
Before stopping, save complete files, inspect the diff, run relevant checks, record remaining work and exact continuation steps, and recommend a checkpoint commit when Git is available. Do not include secrets in handoff documents.
