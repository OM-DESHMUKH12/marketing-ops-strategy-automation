# Known Limitations

## Implemented beta boundary
- Streamlit pages, SQLite persistence, client profile CRUD, presence assessments, local Ollama strategy/content generation, calendar, approval history, and metrics/reporting are implemented in the current scaffold.
- Real Ollama inference and Streamlit runtime still require verification in the user's environment.

## Not implemented
- Authentication, role-based access, and secure multi-agency tenant isolation.
- Social platform APIs, automated account discovery, follower/engagement metric retrieval.
- Website crawling or automatic competitor research.
- External publishing or platform scheduler APIs.
- Robust document upload/text extraction (deferred).
- Campaign management UI beyond database foundations.
- Database backup/restore and production migration management.
- Full security review or production deployment hardening.

## AI reliability
- Model output can be inaccurate despite schema validation. Human review is required.
- JSON schema support varies by local model; malformed output produces an error and is not silently replaced.
- Ollama and configured model must be installed locally.
- Prompt injection risks from imported client text are mitigated with prompt boundaries but cannot be considered eliminated.

## Data
- Metrics are manually entered. They are not live platform analytics.
- The sample client websites and positioning are illustrative; the app does not fetch those URLs.
- A status marked Published is not automatically produced by the app. There is no publishing integration.

## Security and deployment
- This beta has no login system. Do not expose it to untrusted networks or use it for multi-tenant production workloads without additional access controls.
- Secrets belong in environment configuration, never in source control.
