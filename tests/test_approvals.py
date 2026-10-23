import pytest
from services.client_service import create_client
from services.content_service import save_content, get_content, schedule_content
from services.approval_service import transition, approval_history

def setup_content():
    cid=create_client({"company_name":"Approval Test"})
    iid=save_content(cid,{"title":"Approval draft","platform":"LinkedIn","content_type":"Post","caption":"hello"})
    return iid

def test_valid_approval_workflow_and_history():
    iid=setup_content()
    transition(iid,"Pending Approval","Ready for review","Reviewer")
    transition(iid,"Approved","Looks good","Reviewer")
    assert get_content(iid)["status"]=="Approved"
    assert len(approval_history(iid))==2
    schedule_content(iid,"2026-10-20")
    assert get_content(iid)["status"]=="Scheduled"

def test_invalid_transitions_rejected():
    iid=setup_content()
    with pytest.raises(ValueError): transition(iid,"Approved")
    with pytest.raises(ValueError): schedule_content(iid,"2026-10-20")

def test_rejection_requires_revision_comment():
    iid=setup_content()
    transition(iid,"Pending Approval","Submitted")
    with pytest.raises(ValueError): transition(iid,"Rejected","")
