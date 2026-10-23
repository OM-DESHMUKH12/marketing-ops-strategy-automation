"""Small official Ollama HTTP API client. No cloud fallback."""
import os, json, requests

def ollama_settings():
    return {
        "base_url": os.getenv("OLLAMA_BASE_URL","http://localhost:11434").rstrip("/"),
        "model": os.getenv("OLLAMA_MODEL","qwen2.5:1.5b"),
        "timeout": int(os.getenv("OLLAMA_TIMEOUT_SECONDS","300")),
    }

class OllamaError(RuntimeError): pass

def connection_status():
    cfg = ollama_settings()
    try:
        r = requests.get(cfg["base_url"] + "/api/tags", timeout=min(cfg["timeout"], 5))
        r.raise_for_status()
        data = r.json()
        models = [m.get("name","") for m in data.get("models",[])]
        model_found = any(m == cfg["model"] or m.split(":")[0] == cfg["model"].split(":")[0] for m in models)
        return {"connected":True,"base_url":cfg["base_url"],"model":cfg["model"],
                "model_found":model_found,"models":models,"message":
                ("Ollama connected and model is available." if model_found else
                 f"Ollama is online, but '{cfg['model']}' was not found. Run: ollama pull {cfg['model']}")}
    except requests.RequestException as e:
        return {"connected":False,"base_url":cfg["base_url"],"model":cfg["model"],
                "model_found":False,"models":[],"message":
                f"Cannot connect to Ollama at {cfg['base_url']}. Start Ollama, then retry. Details: {type(e).__name__}"}

def generate(prompt, system=None, temperature=0.6):
    cfg = ollama_settings()
    payload = {"model":cfg["model"],"prompt":prompt,"stream":False,
               "options":{"temperature":temperature},
               "format":"json"}
    if system:
        payload["system"] = system
    try:
        response = requests.post(cfg["base_url"]+"/api/generate", json=payload, timeout=cfg["timeout"])
        if response.status_code == 404:
            raise OllamaError(f"Model '{cfg['model']}' or Ollama endpoint was not found. Check the model name and run `ollama pull {cfg['model']}`.")
        response.raise_for_status()
        body = response.json()
        text = body.get("response","").strip()
        if not text:
            raise OllamaError("The local model returned an empty response. Retry or choose another model.")
        return text
    except requests.Timeout as e:
        raise OllamaError(f"Ollama request timed out after {cfg['timeout']} seconds. Try a smaller model or increase OLLAMA_TIMEOUT_SECONDS.") from e
    except requests.ConnectionError as e:
        raise OllamaError(f"Cannot reach Ollama at {cfg['base_url']}. Start Ollama and retry.") from e
    except requests.RequestException as e:
        raise OllamaError(f"Ollama request failed ({type(e).__name__}). Check the local service and model.") from e
    except ValueError as e:
        raise OllamaError("Ollama returned an invalid response.") from e

def parse_json_response(text):
    """Parse a strict JSON response, tolerating a surrounding Markdown code fence."""
    import re
    candidate = text.strip()
    candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.I)
    candidate = re.sub(r"\s*```$", "", candidate)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(candidate[start:end+1])
            except json.JSONDecodeError:
                pass
        raise OllamaError("The model response was not valid JSON. Please retry; no content was saved.")
