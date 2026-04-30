"""Ensemble aggregator that combines multiple defense baseline results."""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from defense.base import DefenseBaseline, DefenseFinding, DefenseReport, DefenseSeverity


class DefenseEnsemble(DefenseBaseline):
    """Run multiple defense baselines and aggregate their findings."""

    name = "ensemble"

    def __init__(
        self,
        baselines: Optional[List[DefenseBaseline]] = None,
        block_on: Optional[List[str]] = None,
        block_severity: Optional[DefenseSeverity] = None,
    ):
        self.baselines = baselines or []
        self.block_on = block_on or []  # list of baseline names that can trigger block
        self.block_severity = block_severity or DefenseSeverity.HIGH

    def add(self, baseline: DefenseBaseline) -> "DefenseEnsemble":
        self.baselines.append(baseline)
        return self

    def _compute_overall_risk(self, reports: List[DefenseReport]) -> DefenseSeverity:
        max_risk = DefenseSeverity.SAFE
        for r in reports:
            if r.overall_risk.rank > max_risk.rank:
                max_risk = r.overall_risk
        return max_risk

    def _should_block(self, reports: List[DefenseReport]) -> tuple[bool, Optional[str]]:
        reasons: List[str] = []
        for r in reports:
            if not self.block_on or r.findings[0].source in self.block_on if r.findings else False:
                if r.overall_risk.rank >= self.block_severity.rank:
                    reasons.append(
                        f"{r.findings[0].source if r.findings else 'unknown'}: {r.overall_risk.value}"
                    )
        # Also block if any report explicitly sets blocked
        for r in reports:
            if r.blocked and r.block_reason:
                reasons.append(r.block_reason)
        if reasons:
            return True, "; ".join(reasons)
        return False, None

    def scan(self, skill_path: Path) -> DefenseReport:
        start = time.time()
        reports: List[DefenseReport] = []
        for baseline in self.baselines:
            try:
                reports.append(baseline.scan(skill_path))
            except Exception as exc:
                reports.append(
                    DefenseReport(
                        skill_path=skill_path,
                        overall_risk=DefenseSeverity.SAFE,
                        findings=[
                            DefenseFinding(
                                source=baseline.name,
                                category="scan_error",
                                message=f"Scan failed: {exc}",
                                severity=DefenseSeverity.LOW,
                            )
                        ],
                    )
                )

        overall = self._compute_overall_risk(reports)
        blocked, block_reason = self._should_block(reports)

        all_findings: List[DefenseFinding] = []
        raw: Dict[str, Any] = {}
        total_duration = 0.0
        for r in reports:
            all_findings.extend(r.findings)
            raw[r.findings[0].source if r.findings else "unknown"] = r.to_dict()
            total_duration += r.scan_duration_seconds

        return DefenseReport(
            skill_path=skill_path,
            overall_risk=overall,
            findings=all_findings,
            raw=raw,
            scan_duration_seconds=total_duration,
            blocked=blocked,
            block_reason=block_reason,
        )
