# AI Model and Prompts

## Status
No AI provider or model is configured or verified. Ollama and open-weight models were examples in the supplied specification, not confirmed implementation choices.

## Provider/model configuration
`NOT STARTED`. Select based on task quality, hardware, latency, context needs, privacy, licensing, and deployment requirements. Keep model/provider configuration external to source code.

## Switching models
When implemented, use a documented configuration setting rather than hard-coding a model throughout the application. Validate provider availability at startup or when the feature is invoked.

## Prompt templates and output schemas
`NOT STARTED`. Store prompts as versioned templates. Define expected output schemas and validate model responses before use.

## Client-context construction
Include only the minimum relevant and authorized information. Avoid passing secrets or unrelated client data. Document truncation and context-size behavior.

## Validation and retry
- Set request timeouts.
- Parse structured output strictly.
- Reject invalid output with actionable error messages.
- Retry only recoverable errors and cap retries.
- Do not treat model output as trusted instructions or executable code.

## Human approval
Generated marketing content must remain a draft until a human explicitly approves it. Any future publication workflow must have a clear approval gate and record its outcome.

## Testing real inference
A real integration test must confirm the configured provider and model are reachable and return output that passes validation. Mocked tests alone do not verify real inference.

## Known limitations
No model performance, reachability, prompt quality, or inference behavior has been measured.
