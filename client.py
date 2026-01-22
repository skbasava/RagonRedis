import requests

API_BASE = "https://policy-api.example.com/xml"

def fetch_xml(project: str, version: str) -> str | None:
    resp = requests.get(f"{API_BASE}/{project}/{version}", timeout=10)
    if resp.status_code == 200:
        return resp.text
    return None