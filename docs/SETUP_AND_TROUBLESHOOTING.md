# Setup and Troubleshooting

## Current state
This repository currently contains documentation only. There is no application runtime, dependency manifest, or launch command.

## Development setup (after stack selection)
1. Install the selected runtime and supported version.
2. Create an isolated environment.
3. Install dependencies using the committed lockfile or documented package manager.
4. Copy `.env.example` to a local environment file if one is introduced; never commit secrets.
5. Apply database migrations if persistence is in scope.
6. Run the documented smoke test.
7. Launch the application using the command recorded in `README.md`.

## Ollama (only if selected)
Ollama installation, model pull commands, hardware requirements, endpoint configuration, and health checks must be documented after Ollama is selected and actually tested. Do not assume a local service is running.

## Troubleshooting principles
- Include the exact error message, environment, and reproduction steps.
- Check configuration and service reachability before debugging application logic.
- Do not log credentials or private customer data.
- Record only solutions that have been reproduced.
