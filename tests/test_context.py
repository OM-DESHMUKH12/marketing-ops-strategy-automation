from services.client_service import create_client
from services.presence_service import upsert_account
from ai.context_builder import build_context

def test_context_uses_selected_client_and_presence():
    a=create_client({"company_name":"Company A","target_audience":"OEMs"})
    b=create_client({"company_name":"Company B","target_audience":"Local gym members"})
    upsert_account(a,{"platform":"LinkedIn","account_status":"Present","profile_url":"https://example.com/company-a"})
    ctx_a=build_context(a); ctx_b=build_context(b)
    assert "Company A" in ctx_a and "Company B" not in ctx_a
    assert "Present" in ctx_a
    assert "Company B" in ctx_b and "Company A" not in ctx_b
