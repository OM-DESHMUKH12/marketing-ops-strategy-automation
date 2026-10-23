"""Local-model report narrative based only on recorded analytics."""
from ai.ollama_client import generate, parse_json_response, OllamaError
from services.reporting_service import analytics_summary

def generate_report_insights(client_id, period_start, period_end):
    summary=analytics_summary(client_id,period_start,period_end)
    safe={k:v for k,v in summary.items() if k not in ("metrics","content")}
    result=parse_json_response(generate(
        f"Using only these saved metrics, return JSON with keys observations (array), limitations (array), next_actions (array). Data: {safe}",
        "You are an analytics assistant. Never invent metrics or imply causation from insufficient data. Return only JSON."
    ))
    if not isinstance(result,dict): raise OllamaError("Report insights were malformed.")
    return result
