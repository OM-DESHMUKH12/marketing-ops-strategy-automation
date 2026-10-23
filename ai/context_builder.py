"""Build concise, explicit context from saved client and presence data."""
import json
from services.client_service import client_context
from services.presence_service import presence_summary

def build_context(client_id, extra=None):
    context = client_context(client_id)
    summary = presence_summary(client_id)
    context["presence_assessment"] = {
        "has_present_accounts": summary["has_present"],
        "known_absence_recorded": summary["known_absent"],
        "unknown_or_unassessed_exists": summary["has_unknown"],
        "note": "Unknown and Not assessed do not mean Absent. Do not claim verification unless a trusted source is recorded.",
    }
    if extra:
        context["request"] = extra
    # Bound prompt size and prevent accidentally huge profile fields from dominating context.
    serialized = json.dumps(context, ensure_ascii=False, default=str)
    return serialized[:18000]
