import pytest
from services.client_service import create_client
from services.presence_service import upsert_account, list_accounts, presence_summary

def test_absent_is_distinct_from_unknown():
    cid=create_client({"company_name":"Presence Test"})
    upsert_account(cid,{"platform":"Instagram","account_status":"Absent"})
    upsert_account(cid,{"platform":"LinkedIn","account_status":"Unknown"})
    rows={x["platform"]:x for x in list_accounts(cid)}
    assert rows["Instagram"]["account_status"]=="Absent"
    assert rows["LinkedIn"]["account_status"]=="Unknown"
    summary=presence_summary(cid)
    assert summary["known_absent"] is True
    assert summary["has_unknown"] is True

def test_absent_with_url_rejected():
    cid=create_client({"company_name":"Presence Test"})
    with pytest.raises(ValueError):
        upsert_account(cid,{"platform":"Instagram","account_status":"Absent","profile_url":"https://instagram.com/example"})
