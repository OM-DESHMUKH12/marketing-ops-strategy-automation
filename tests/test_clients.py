from services.client_service import create_client, get_client, list_clients, update_client, delete_client

def sample(**extra):
    d={"company_name":"Example Industries","industry":"Manufacturing","target_audience":"OEM buyers","brand_voice":"Technical"}
    d.update(extra); return d

def test_create_retrieve_update_delete_client():
    cid=create_client(sample())
    assert get_client(cid)["company_name"]=="Example Industries"
    assert list_clients("manufacturing")[0]["id"]==cid
    update_client(cid,sample(company_name="Example Industries Updated"))
    assert get_client(cid)["company_name"]=="Example Industries Updated"
    delete_client(cid)
    assert get_client(cid) is None

def test_company_name_required():
    import pytest
    with pytest.raises(ValueError): create_client({"company_name":" "})
