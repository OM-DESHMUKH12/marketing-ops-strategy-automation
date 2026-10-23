"""Thin orchestration helpers for generating and persisting content."""
from ai.content_generator import generate_content
from services.content_service import save_content

def generate_and_save(client_id, options):
    draft = generate_content(client_id, options)
    strategy_id = options.get("strategy_id") or None
    content_id = save_content(client_id, draft, strategy_id=strategy_id,
                              scheduled_date=options.get("scheduled_date"))
    return content_id, draft
