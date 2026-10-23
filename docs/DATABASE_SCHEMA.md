# Database Schema

## Status
No database has been selected or implemented. This document is a placeholder until domain requirements are confirmed.

## Candidate approach
A lightweight relational database may be suitable for a local beta, but SQLite is not an accepted decision yet. Record the final choice in `DECISIONS.md`.

## Schema
Tables, fields, primary keys, foreign keys, indexes, constraints, and relationships: `NOT STARTED`. Derive them from confirmed domain entities and user journeys rather than guessing.

## Migration strategy
To be selected with the database. Prefer versioned, repeatable migrations; do not rely on manual production schema edits.

## Persistence rules
- Define ownership and access boundaries for stored client data.
- Use transactions for multi-step state changes.
- Validate values at application boundaries and enforce critical invariants in the database where possible.
- Keep secrets out of ordinary application tables and logs.
- Test persistence across restart and migration from the previous schema version.
