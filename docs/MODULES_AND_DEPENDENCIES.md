# Modules and Dependencies

## Current modules
Only documentation exists in this scaffold. Application module names and interfaces should be established after requirements and stack selection.

## Proposed module boundaries
- **Presentation:** UI rendering and input capture.
- **Application:** use cases and orchestration.
- **Domain:** entities, value objects, business rules, state transitions.
- **Persistence:** repositories and migrations.
- **AI integration:** provider adapter, prompt registry, output validation.
- **External integrations:** isolated adapters for each required platform.
- **Configuration/observability:** settings, logging, health checks.

## Dependency rules
- Domain rules should not import UI or vendor SDKs.
- Application use cases depend on interfaces, not concrete provider clients.
- Provider-specific logic remains inside integration adapters.
- Avoid circular imports and duplicated business rules.
- Add dependencies only when justified; pin and document them according to the chosen package manager.

## Entry points
None implemented yet. Select and document the actual entry point once the runtime stack is decided.
