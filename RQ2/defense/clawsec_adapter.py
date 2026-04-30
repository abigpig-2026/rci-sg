"""Adapter porting ClawSec's file integrity monitor to Python.

Provides SHA-256 baseline tracking and drift detection for skill files.
This is a simplified port of clawsec-main/skills/clawsec-nanoclaw/guardian/integrity-monitor.ts
adapted for pre-execution static checks on the host.
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from defense.base import DefenseBaseline, DefenseFinding, DefenseReport, DefenseSeverity

logger = logging.getLogger(__name__)


def _sha256_file(file_path: Path) -> str:
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


@dataclass
class _FileBaseline:
    sha256: str
    approved_at: str
    approved_by: str
    mode: str
    priority: str


class ClawSecIntegrityAdapter(DefenseBaseline):
    """Check skill files against an integrity baseline.

    If a baseline file is provided, each file under skill_path is compared.
    Without a baseline, the adapter generates one on first run and treats
    the skill as SAFE (acting as an initialization mode).
    """

    name = "clawsec_integrity"

    def __init__(
        self,
        baseline_path: Optional[Path] = None,
        auto_generate_baseline: bool = True,
        actor: str = "chainbreaker",
    ):
        self.baseline_path = baseline_path
        self.auto_generate_baseline = auto_generate_baseline
        self.actor = actor

    def _load_baseline(self) -> Dict[str, _FileBaseline]:
        if not self.baseline_path or not self.baseline_path.exists():
            return {}
        data = json.loads(self.baseline_path.read_text(encoding="utf-8"))
        files = data.get("files", {})
        return {
            k: _FileBaseline(
                sha256=v.get("sha256", ""),
                approved_at=v.get("approved_at", ""),
                approved_by=v.get("approved_by", ""),
                mode=v.get("mode", "alert"),
                priority=v.get("priority", "medium"),
            )
            for k, v in files.items()
        }

    def _save_baseline(self, baselines: Dict[str, _FileBaseline]) -> None:
        if not self.baseline_path:
            return
        self.baseline_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "1",
            "algorithm": "sha256",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "files": {
                k: {
                    "sha256": v.sha256,
                    "approved_at": v.approved_at,
                    "approved_by": v.approved_by,
                    "mode": v.mode,
                    "priority": v.priority,
                }
                for k, v in baselines.items()
            },
        }
        self.baseline_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _list_files(self, skill_path: Path) -> List[Path]:
        files: List[Path] = []
        try:
            for item in skill_path.rglob("*"):
                if item.is_file() and not item.is_symlink():
                    files.append(item)
        except Exception as exc:
            logger.warning(f"Failed to list files in {skill_path}: {exc}")
        return files

    def scan(self, skill_path: Path) -> DefenseReport:
        start = time.time()
        report = DefenseReport(skill_path=skill_path)
        baselines = self._load_baseline()
        files = self._list_files(skill_path)

        # Build normalized key using relative path
        def _key(p: Path) -> str:
            return str(p.relative_to(skill_path)).replace("\\", "/")

        if not baselines and self.auto_generate_baseline:
            # Initialize baseline from current skill files
            new_baselines: Dict[str, _FileBaseline] = {}
            for f in files:
                key = _key(f)
                new_baselines[key] = _FileBaseline(
                    sha256=_sha256_file(f),
                    approved_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    approved_by=self.actor,
                    mode="alert",
                    priority="medium",
                )
            self._save_baseline(new_baselines)
            report.findings.append(
                DefenseFinding(
                    source=self.name,
                    category="baseline_init",
                    message="Integrity baseline initialized for skill",
                    severity=DefenseSeverity.SAFE,
                )
            )
            report.raw[self.name] = {"initialized": True, "files": len(files)}
            report.scan_duration_seconds = time.time() - start
            return report

        max_severity = DefenseSeverity.SAFE
        drift_count = 0
        missing_count = 0
        extra_count = 0

        current_keys = set()
        for f in files:
            key = _key(f)
            current_keys.add(key)
            current_sha = _sha256_file(f)
            baseline = baselines.get(key)

            if not baseline:
                extra_count += 1
                report.findings.append(
                    DefenseFinding(
                        source=self.name,
                        category="extra_file",
                        message=f"Extra file not in baseline: {key}",
                        severity=DefenseSeverity.MEDIUM,
                        file_path=key,
                    )
                )
                if max_severity.rank < DefenseSeverity.MEDIUM.rank:
                    max_severity = DefenseSeverity.MEDIUM
                continue

            if current_sha != baseline.sha256:
                drift_count += 1
                severity = (
                    DefenseSeverity.HIGH
                    if baseline.priority in ("critical", "high")
                    else DefenseSeverity.MEDIUM
                )
                report.findings.append(
                    DefenseFinding(
                        source=self.name,
                        category="drift",
                        message=f"File drift detected: expected {baseline.sha256[:16]}..., found {current_sha[:16]}...",
                        severity=severity,
                        file_path=key,
                        details={"expected_sha": baseline.sha256, "found_sha": current_sha},
                    )
                )
                if severity.rank > max_severity.rank:
                    max_severity = severity

        for key in baselines:
            if key not in current_keys:
                missing_count += 1
                report.findings.append(
                    DefenseFinding(
                        source=self.name,
                        category="missing_file",
                        message=f"Baseline file missing: {key}",
                        severity=DefenseSeverity.LOW,
                        file_path=key,
                    )
                )

        report.overall_risk = max_severity
        report.raw[self.name] = {
            "files_scanned": len(files),
            "drift_count": drift_count,
            "missing_count": missing_count,
            "extra_count": extra_count,
        }
        report.scan_duration_seconds = time.time() - start
        return report
