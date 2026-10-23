"""Optional local-model copy review. Review output is advisory and never auto-approves content."""
from ai.ollama_client import generate, parse_json_response, OllamaError
from ai.context_builder import build_context

def review_content(client_id, content):
    context = build_context(client_id)
    prompt = f"""Review this marketing draft for brand fit, unsupported factual claims, prohibited topics, clarity and CTA.
Client context: {context}
Draft JSON: {content}
Return JSON with keys score (0-100 integer), strengths (array), issues (array), suggested_edits (array), human_review_required (boolean).
This is an advisory review, not an approval decision."""
    result=parse_json_response(generate(prompt, "You are a cautious marketing copy editor. Return only JSON."))
    if not isinstance(result,dict) or not isinstance(result.get("issues",[]),list):
        raise OllamaError("Review response had an unexpected shape. Retry.")
    result["human_review_required"] = True
    return result
