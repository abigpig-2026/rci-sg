"""Base abstractions for ChainBreaker defense baselines."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class DefenseSeverity(str, Enum):
    """Severity levels for a defense finding."""

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        mapping = {
            "safe": 0,
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }
        return mapping[self.value]


@dataclass
class DefenseFinding:
    """A single finding from a defense scan."""

    source: str
    category: str
    message: str
    severity: DefenseSeverity = DefenseSeverity.SAFE
    file_path: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "category": self.category,
            "message": self.message,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "details": self.details,
        }


@dataclass
class DefenseReport:
    """Aggregated result of scanning a skill with one or more defense baselines."""

    skill_path: Path
    overall_risk: DefenseSeverity = DefenseSeverity.SAFE
    findings: List[DefenseFinding] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)
    scan_duration_seconds: float = 0.0
    blocked: bool = False
    block_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_path": str(self.skill_path),
            "overall_risk": self.overall_risk.value,
            "findings": [f.to_dict() for f in self.findings],
            "raw": self.raw,
            "scan_duration_seconds": self.scan_duration_seconds,
            "blocked": self.blocked,
            "block_reason": self.block_reason,
        }


class DefenseBaseline(ABC):
    """Abstract base class for a defense baseline adapter."""

    name: str = "base"

    @abstractmethod
    def scan(self, skill_path: Path) -> DefenseReport:
        """Scan a skill package and return a defense report."""
        ...
