"""Defense baseline integration for ChainBreaker.

Provides a unified interface to scan skills using multiple defense sources:
- MASB static scanner (skill-security-scan)
- AgentWard foundation-scan rule-based detection
- ClawSec integrity monitor
- OpenClaw security skill plugins
"""

from defense.base import DefenseBaseline, DefenseFinding, DefenseReport, DefenseSeverity
from defense.ensemble import DefenseEnsemble
from defense.masb_adapter import MASBScannerAdapter
from defense.agentward_adapter import AgentWardAdapter
from defense.clawsec_adapter import ClawSecIntegrityAdapter
from defense.openclaw_skill_adapter import OpenClawSkillAdapter

__all__ = [
    "DefenseBaseline",
    "DefenseReport",
    "DefenseFinding",
    "DefenseSeverity",
    "DefenseEnsemble",
    "MASBScannerAdapter",
    "AgentWardAdapter",
    "ClawSecIntegrityAdapter",
    "OpenClawSkillAdapter",
]
