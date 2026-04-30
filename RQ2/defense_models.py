"""Data models for ChainBreaker Phase 1."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class RiskLevel(str, Enum):
    """Risk classification for a sandbox run."""

    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"


@dataclass
class DefenseFinding:
    """A single finding from a defense scan."""

    source: str
    category: str
    message: str
    severity: str = "safe"
    file_path: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DefenseReport:
    """Aggregated result of defense baseline scanning."""

    skill_path: Path
    overall_risk: str = "safe"
    findings: List[DefenseFinding] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)
    scan_duration_seconds: float = 0.0
    blocked: bool = False
    block_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_path": str(self.skill_path),
            "overall_risk": self.overall_risk,
            "findings": [
                {
                    "source": f.source,
                    "category": f.category,
                    "message": f.message,
                    "severity": f.severity,
                    "file_path": f.file_path,
                    "details": f.details,
                }
                for f in self.findings
            ],
            "raw": self.raw,
            "scan_duration_seconds": self.scan_duration_seconds,
            "blocked": self.blocked,
            "block_reason": self.block_reason,
        }


@dataclass
class SkillPackage:
    """Lightweight representation of a skill under test."""

    name: str
    path: Path
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NetworkEvent:
    """A network request observed during sandbox execution."""

    timestamp: str
    method: str
    url: str
    target_domain: str
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    matched_canary: bool = False


@dataclass
class FileSystemEvent:
    """A filesystem change observed during sandbox execution."""

    path: str
    operation: str  # create, modify, delete
    size_before: Optional[int] = None
    size_after: Optional[int] = None


@dataclass
class ProcessEvent:
    """A process-level event from strace or procps."""

    pid: int
    syscall: str
    args: List[str] = field(default_factory=list)
    timestamp: Optional[str] = None


@dataclass
class DropzoneReport:
    """Results from the Dropzone Canary Protocol checks."""

    exfil_detected: bool = False
    persistence_detected: bool = False
    edos_detected: bool = False
    exfil_evidence: str = ""
    persistence_evidence: str = ""
    edos_evidence: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exfil_detected": self.exfil_detected,
            "persistence_detected": self.persistence_detected,
            "edos_detected": self.edos_detected,
            "exfil_evidence": self.exfil_evidence,
            "persistence_evidence": self.persistence_evidence,
            "edos_evidence": self.edos_evidence,
        }


@dataclass
class TelemetryReport:
    """Aggregated telemetry from a single sandbox run."""

    canary_uuid: str
    canary_hits: List[str] = field(default_factory=list)
    network_events: List[NetworkEvent] = field(default_factory=list)
    filesystem_events: List[FileSystemEvent] = field(default_factory=list)
    process_events: List[ProcessEvent] = field(default_factory=list)
    dropzone: DropzoneReport = field(default_factory=DropzoneReport)
    risk_level: RiskLevel = RiskLevel.BENIGN
    summary: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunResult:
    """Complete result of running one skill through the sandbox."""

    skill: SkillPackage
    prompt: str
    container_id: Optional[str] = None
    exit_code: Optional[int] = None
    logs: str = ""
    telemetry: TelemetryReport = field(default_factory=lambda: TelemetryReport(canary_uuid=""))
    duration_seconds: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    defense_report: Optional[DefenseReport] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill.name,
            "prompt": self.prompt,
            "container_id": self.container_id,
            "exit_code": self.exit_code,
            "logs": self.logs,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
            "error_message": self.error_message,
            "defense_report": self.defense_report.to_dict() if self.defense_report else None,
            "created_at": self.created_at,
            "telemetry": {
                "canary_uuid": self.telemetry.canary_uuid,
                "canary_hits": self.telemetry.canary_hits,
                "network_event_count": len(self.telemetry.network_events),
                "filesystem_event_count": len(self.telemetry.filesystem_events),
                "process_event_count": len(self.telemetry.process_events),
                "dropzone": self.telemetry.dropzone.to_dict(),
                "risk_level": self.telemetry.risk_level.value,
                "summary": self.telemetry.summary,
            },
        }
