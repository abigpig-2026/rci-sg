"""Adapter for OpenClaw security skill plugins.

ClawSec provides several security-related OpenClaw skills:
- clawsec-scanner (vulnerability scanner)
- soul-guardian (integrity/drift detection)
- openclaw-audit-watchdog (security audit)

Since these skills execute inside the OpenClaw runtime, this adapter performs
static checks before sandbox launch:
1. Verifies the plugin directories exist and contain required files.
2. Ensures they can be copied into the sandbox OpenClaw skills directory.
3. Reports configuration/status findings.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from defense.base import DefenseBaseline, DefenseFinding, DefenseReport, DefenseSeverity

logger = logging.getLogger(__name__)

REQUIRED_OPENCLAW_SECURITY_SKILLS = [
    "clawsec-scanner",
    "soul-guardian",
    "openclaw-audit-watchdog",
]


def _default_clawsec_skills_dir() -> Path:
    return (
        Path(__file__).resolve().parent.parent.parent
        / "clawsec-main"
        / "skills"
    )


class OpenClawSkillAdapter(DefenseBaseline):
    """Checks that OpenClaw security skill plugins are available and valid."""

    name = "openclaw_skill_plugins"

    def __init__(
        self,
        clawsec_skills_dir: Optional[Path] = None,
        required_skills: Optional[List[str]] = None,
    ):
        self.clawsec_skills_dir = clawsec_skills_dir or _default_clawsec_skills_dir()
        self.required_skills = required_skills or REQUIRED_OPENCLAW_SECURITY_SKILLS

    def _validate_skill(self, skill_name: str) -> Dict[str, Any]:
        skill_dir = self.clawsec_skills_dir / skill_name
        result: Dict[str, Any] = {"name": skill_name, "exists": False, "valid": False, "missing_files": []}

        if not skill_dir.exists():
            return result

        result["exists"] = True
        skill_json = skill_dir / "skill.json"
        if not skill_json.exists():
            result["missing_files"].append("skill.json")
            return result

        try:
            meta = json.loads(skill_json.read_text(encoding="utf-8"))
        except Exception as exc:
            result["error"] = f"Invalid skill.json: {exc}"
            return result

        sbom = meta.get("sbom", {})
        files = sbom.get("files", [])
        missing = []
        for entry in files:
            if entry.get("required", False):
                p = skill_dir / entry["path"]
                if not p.exists():
                    missing.append(entry["path"])

        result["missing_files"] = missing
        result["valid"] = len(missing) == 0
        result["meta"] = {
            "version": meta.get("version"),
            "description": meta.get("description"),
        }
        return result

    def scan(self, skill_path: Path) -> DefenseReport:
        start = time.time()
        report = DefenseReport(skill_path=skill_path)
        max_severity = DefenseSeverity.SAFE
        validations: List[Dict[str, Any]] = []

        for skill_name in self.required_skills:
            v = self._validate_skill(skill_name)
            validations.append(v)

            if not v["exists"]:
                max_severity = DefenseSeverity.MEDIUM
                report.findings.append(
                    DefenseFinding(
                        source=self.name,
                        category="missing_plugin",
                        message=f"OpenClaw security skill '{skill_name}' not found in {self.clawsec_skills_dir}",
                        severity=DefenseSeverity.MEDIUM,
                        details=v,
                    )
                )
            elif not v["valid"]:
                max_severity = DefenseSeverity.LOW
                report.findings.append(
                    DefenseFinding(
                        source=self.name,
                        category="invalid_plugin",
                        message=f"OpenClaw security skill '{skill_name}' is missing required files: {v['missing_files']}",
                        severity=DefenseSeverity.LOW,
                        details=v,
                    )
                )

        if max_severity == DefenseSeverity.SAFE:
            report.findings.append(
                DefenseFinding(
                    source=self.name,
                    category="plugin_status",
                    message="All required OpenClaw security skill plugins are available",
                    severity=DefenseSeverity.SAFE,
                )
            )

        report.overall_risk = max_severity
        report.raw[self.name] = {"validations": validations}
        report.scan_duration_seconds = time.time() - start
        return report
