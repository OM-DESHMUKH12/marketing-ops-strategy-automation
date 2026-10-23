# Testing Guide

## Current state
No test framework or test suite is configured yet.

## Planned verification layers
1. **Unit tests:** domain rules and pure validation logic.
2. **Application tests:** use cases with persistence/integrations mocked where appropriate.
3. **Persistence tests:** schema, constraints, migrations, and restart persistence.
4. **Integration tests:** real configured provider or external service, clearly separated from default offline tests.
5. **End-to-end tests:** the highest-priority user journey.
6. **Manual checks:** usability and demo flow, recorded separately from automated results.

## Test-writing rules
- Include happy paths, invalid input, boundary cases, and failure handling.
- Make tests deterministic and independent.
- Never use real production credentials or data in tests.
- Do not mark a test as passing without executing it.

## Commands
To be defined after the technology stack is selected. Record exact commands in `TEST_STATUS.md`.

## Initial end-to-end scenario
Blocked until a core user journey is confirmed. Once known, document setup/fixtures, exact steps, expected persistent state, error cases, and teardown.
