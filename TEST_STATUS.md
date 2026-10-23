# Test Status

**Last updated:** 2026-10-17

## Automated tests
- **Command executed:** `python -m pytest -q`
- **Result:** **13 passed, 0 failed**
- **Python:** 3.13.5
- **Compilation:** `compileall.compile_dir(..., quiet=1)` — passed for project Python files.
- **Coverage areas:** Client CRUD and validation, presence state distinction, absent URL validation, content persistence/editing, generation retry deduplication, approval transitions/history, scheduling guard, analytics calculations, report generation, selected-client context, and JSON parsing errors.
- **Database:** Tests used isolated temporary SQLite databases.

## Local model
- Ollama endpoint reachability: not checked.
- Configured model availability: not checked.
- Real content-generation request: not run.
- The test suite intentionally mocks no AI generation path because these tests target service/data behavior; real inference remains a required manual verification.

## Application runtime
- Python syntax compilation passed.
- Streamlit was not installed in the inspected build environment, so a live Streamlit launch/smoke test could not be performed here.
- Install dependencies with `pip install -r requirements.txt`, then run `streamlit run app.py`.

## Known unverified behavior
- Live Streamlit UI interaction.
- Real Ollama inference and model-specific JSON compliance.
- End-to-end user demo with installed dependencies.
- External social integrations/publishing are intentionally not implemented.

## Rule
Record exact commands and actual results. Do not treat the existence of tests as proof they passed.
