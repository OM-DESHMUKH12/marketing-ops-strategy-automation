import json
import pytest
from services.client_service import create_client
from services.content_service import save_content, get_content, update_content, list_content

def test_content_persists_and_can_be_edited():
    cid=create_client({"company_name":"Content Test"})
    data={"title":"Technical post","platform":"LinkedIn","content_type":"Social post","topic":"Precision","caption":"Draft copy","hashtags":["#B2B"]}
    item_id=save_content(cid,data)
    item=get_content(item_id)
    assert item["caption"]=="Draft copy"
    assert json.loads(item["content_json"])["hashtags"]==["#B2B"]
    update_content(item_id,"Edited","LinkedIn","Social post","Precision","Revised copy",item["content_json"],"2026-10-20")
    assert get_content(item_id)["caption"]=="Revised copy"
    assert len(list_content(cid))==1

def test_generation_retry_key_deduplicates():
    cid=create_client({"company_name":"Retry Test"})
    data={"title":"Retry safe","platform":"LinkedIn","content_type":"Post","caption":"x","_generation_key":"stable-key"}
    a=save_content(cid,data); b=save_content(cid,data)
    assert a==b
