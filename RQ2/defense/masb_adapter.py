"""Adapter for the MaliciousAgentSkillsBench static scanner (skill-security-scan)."""

import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from defense.base import DefenseBaseline, DefenseFinding, DefenseReport, DefenseSeverity

logger = logging.getLogger(__name__)


class MASBScannerAdapter(DefenseBaseline):
    """Wrapper around MASB's skill-security-scan CLI."""

    name = "masb_scanner"

    def __init__(
        self,
        scan_tool_dir: Optional[Path] = None,
        timeout: int = 60,
        thresholds: Optional[Dict[str, int]] = None,
    ):
        self.scan_tool_dir = scan_tool_dir or self._default_scan_tool_dir()
        self.timeout = timeout
        self.thresholds = thresholds or {
            "critical": 8,
            "high": 6,
            "medium": 4,
            "low": 2,
        }

    @staticmethod
    def _default_scan_tool_dir() -> Path:
        """Locate the skill-security-scan package relative to ChainBreaker."""
        return (
            Path(__file__).resolve().parent.parent.parent
            / "MaliciousAgentSkillsBench-main"
            / "code"
            / "scanner"
            / "skill-security-scan"
        )

    def _is_skill_dir(self, path: Path) -> bool:
        indicators = ["SKILL.md", "skill.json", "api.json", "tool.json"]
        return any((path / f).exists() for f in indicators)

    def _find_skill_dirs(self, root: Path) -> List[Path]:
        skill_dirs = []
        for item in root.rglob("*"):
            if item.is_dir() and self._is_skill_dir(item):
                skill_dirs.append(item)
        # If root itself is a skill dir, include it
        if self._is_skill_dir(root):
            skill_dirs.append(root)
        return list(dict.fromkeys(skill_dirs))  # dedup preserving order

    def _scan_skill(self, skill_dir: Path) -> Optional[Dict[str, Any]]:
        if not self.scan_tool_dir.exists():
            logger.warning(f"MASB scan tool not found at {self.scan_tool_dir}")
            return None

        temp_output = tempfile.mktemp(suffix=".json")
        cmd = [
            sys.executable,
            "-m",
            "skill_security_scan.src.cli",
            "scan",
            str(skill_dir),
            "--format",
            "json",
            "--output",
            temp_output,
            "--no-color",
        ]
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.scan_tool_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            if result.returncode != 0:
                logger.warning(f"MASB scan failed for {skill_dir}: {result.stderr}")
                return None

            if Path(temp_output).exists():
                with open(temp_output, "r", encoding="utf-8") as f:
                    report = json.load(f)
                os.remove(temp_output)
                return report
        except subprocess.TimeoutExpired:
            logger.error(f"MASB scan timeout for {skill_dir}")
        except Exception as exc:
            logger.error(f"MASB scan error for {skill_dir}: {exc}")
        finally:
            if Path(temp_output).exists():
                os.remove(temp_output)
        return None

    def _calculate_risk(self, risk_score: int) -> DefenseSeverity:
        if risk_score >= self.thresholds["critical"]:
            return DefenseSeverity.CRITICAL
        if risk_score >= self.thresholds["high"]:
            return DefenseSeverity.HIGH
        if risk_score >= self.thresholds["medium"]:
            return DefenseSeverity.MEDIUM
        if risk_score >= self.thresholds["low"]:
            return DefenseSeverity.LOW
        return DefenseSeverity.SAFE

    def scan(self, skill_path: Path) -> DefenseReport:
        start = time.time()
        report = DefenseReport(skill_path=skill_path)

        skill_dirs = self._find_skill_dirs(skill_path)
        if not skill_dirs:
            report.findings.append(
                DefenseFinding(
                    source=self.name,
                    category="scan_status",
                    message="No skill directories found",
                    severity=DefenseSeverity.SAFE,
                )
            )
            report.scan_duration_seconds = time.time() - start
            return report

        raw_reports: List[Dict[str, Any]] = []
        max_severity = DefenseSeverity.SAFE

        for skill_dir in skill_dirs:
            scan_result = self._scan_skill(skill_dir)
            if scan_result is None:
                continue
            raw_reports.append({"skill_dir": str(skill_dir), "result": scan_result})

            risk_score = scan_result.get("risk_score", 0)
            severity = self._calculate_risk(risk_score)
            if severity.rank > max_severity.rank:
                max_severity = severity

            findings = scan_result.get("findings", [])
            for issue in findings:
                report.findings.append(
                    DefenseFinding(
                        source=self.name,
                        category=issue.get("category", "unknown"),
                        message=issue.get("message", ""),
                        severity=severity,
                        file_path=issue.get("file"),
                        details=issue,
                    )
                )

        report.overall_risk = max_severity
        report.raw[self.name] = raw_reports
        report.scan_duration_seconds = time.time() - start
        return report
