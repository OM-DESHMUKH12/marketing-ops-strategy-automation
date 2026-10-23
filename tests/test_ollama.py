import pytest
from ai.ollama_client import parse_json_response, OllamaError

def test_parse_json_response_with_fence():
    assert parse_json_response('```json\\n{"ok": true}\\n```') == {"ok":True}

def test_malformed_response_rejected():
    with pytest.raises(OllamaError): parse_json_response("this is not json")
