"""
triage_engine.py  —  Uses Groq API (free tier)
Get your free key at: https://console.groq.com
"""
import json, re, requests
from .prompts import SYSTEM_PROMPT, build_user_prompt

class TriageEngine:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url     = "https://api.groq.com/openai/v1/chat/completions"
        self.model   = "llama-3.3-70b-versatile"

    def analyze(self, ticket_text: str):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_user_prompt(ticket_text)},
            ],
            "temperature": 0.1,
            "max_tokens": 1024,
        }
        try:
            resp = requests.post(self.url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 401:
                return None, "Invalid API key. Get free key at console.groq.com"
            if resp.status_code == 429:
                return None, "Rate limit hit. Wait a few seconds and retry."
            if resp.status_code != 200:
                return None, f"API error {resp.status_code}: {resp.text[:200]}"
            raw = resp.json()["choices"][0]["message"]["content"].strip()
            return self._parse(raw), None
        except requests.exceptions.ConnectionError:
            return None, "No internet connection."
        except requests.exceptions.Timeout:
            return None, "Request timed out. Try again."
        except Exception as e:
            return None, f"Error: {str(e)}"

    def _parse(self, raw: str) -> dict:
        cleaned = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if m:
                data = json.loads(m.group())
            else:
                raise ValueError("Cannot parse JSON from model response.")
        return self._enrich(data)

    def _enrich(self, d: dict) -> dict:
        d["category"]   = d.get("category")   if d.get("category")   in {"Finance","Inventory","Procurement","HR","General"}                                    else "General"
        d["priority"]   = d.get("priority")   if d.get("priority")   in {"High","Medium","Low"}                                                                 else "Medium"
        d["erp_module"] = d.get("erp_module") if d.get("erp_module") in {"Oracle Fusion","SAP","Microsoft Dynamics","Generic ERP"}                              else "Generic ERP"
        d["issue_type"] = d.get("issue_type") if d.get("issue_type") in {"Issue","Change Request","Support Request","Information Request"}                       else "Support Request"
        d.setdefault("key_details",        [])
        d.setdefault("summary",            "ERP support ticket requiring attention.")
        d.setdefault("first_response",     "Thank you. We have received your ticket and will investigate shortly.")
        d.setdefault("priority_reasoning", "Priority assigned based on ticket content analysis.")
        try:
            c = float(d.get("confidence", 0.85))
            d["confidence"] = c if 0 <= c <= 1 else 0.85
        except Exception:
            d["confidence"] = 0.85
        d["suggested_team"] = {"Finance":"Finance & Accounting Support","Inventory":"Warehouse & Inventory Team","Procurement":"Procurement & Supply Chain Team","HR":"HR Systems Team"}.get(d["category"],"Tier-1 Support")
        return d
