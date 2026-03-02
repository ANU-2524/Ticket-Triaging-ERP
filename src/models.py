"""
models.py
=========
Data models for typed ticket results.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TicketResult:
    category: str
    erp_module: str
    issue_type: str
    priority: str
    priority_reasoning: str
    summary: str
    key_details: List[str]
    confidence: float
    first_response: str
    suggested_team: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "TicketResult":
        return cls(
            category=data.get("category", "General"),
            erp_module=data.get("erp_module", "Generic ERP"),
            issue_type=data.get("issue_type", "Support Request"),
            priority=data.get("priority", "Medium"),
            priority_reasoning=data.get("priority_reasoning", ""),
            summary=data.get("summary", ""),
            key_details=data.get("key_details", []),
            confidence=float(data.get("confidence", 0.85)),
            first_response=data.get("first_response", ""),
            suggested_team=data.get("suggested_team", "Tier-1 Support"),
        )

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "erp_module": self.erp_module,
            "issue_type": self.issue_type,
            "priority": self.priority,
            "priority_reasoning": self.priority_reasoning,
            "summary": self.summary,
            "key_details": self.key_details,
            "confidence": self.confidence,
            "first_response": self.first_response,
            "suggested_team": self.suggested_team,
        }
