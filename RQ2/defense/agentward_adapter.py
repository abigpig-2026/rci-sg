"""Adapter porting AgentWard's foundation-scan rule-based detection to Python.

The TypeScript original uses regex patterns for:
- Explicit attack patterns
- Suspicious payload patterns
- Bypass patterns (need 2+ matches)
- High-risk patterns

Only the rule-based detection is ported here; semantic/LLM detection is optional
and can be added later via a separate LLM-assisted adapter.
"""

import hashlib
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from defense.base import DefenseBaseline, DefenseFinding, DefenseReport, DefenseSeverity

logger = logging.getLogger(__name__)

MAX_TEXT_FILE_SIZE = 1024 * 1024
TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".json5",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
    ".csv",
    ".ts",
    ".js",
    ".py",
    ".java",
    ".sh",
    ".ps1",
    ".sql",
    ".ini",
    ".cfg",
}

EXPLICIT_ATTACK_PATTERNS = [
    re.compile(
        r"\b(?:system|developer|admin)\s*(?:override|mode|access)\s*:\s*(?:enable|activate|grant)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:always\s+obey|never\s+refuse|unconditionally\s+comply|without\s+question)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:grant\s+(?:me|user)\s+(?:full|root|admin|unlimited)\s*(?:access|permission|privilege))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:steal|exfiltrate|extract|harvest)\s+(?:all\s+)?(?:user\s+)?(?:data|information|credentials|passwords?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:必须|务必|一定).{0,10}(服从|执行|遵守).{0,10}(所有|任何|全部).{0,10}(指令|命令|要求)",
        re.IGNORECASE,
    ),
]

SUSPICIOUS_PAYLOAD_PATTERNS = [
    re.compile(r"(?:[a-z0-9+/]{220,}={0,2})", re.IGNORECASE),
    re.compile(r"(?:0x)?(?:[0-9a-f]{2}){160,}", re.IGNORECASE),
]

BYPASS_PATTERNS = [
    re.compile(
        r"\b(?:ignore|disregard|forget|override)\b\s+(?:all\s+)?(?:previous|above|safety|security)\b.{0,20}\b(?:instructions?|rules?|constraints?|protocols?|limitations?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:bypass|circumvent|disable|override|evade|neutralize)\b\s+(?:all\s+)?(?:security|safety|guardrail|restriction|sandbox)\b.{0,15}\b(?:check|validation|protocol|measure)s?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:忽略|无视|忘记|绕过|突破).{0,10}(所有|全部|安全|之前).{0,10}(指令|规则|约束|限制|协议)",
        re.IGNORECASE,
    ),
    re.compile(r"(?:绕过|禁用|关闭|突破).{0,16}(安全|限制|防护|策略|护栏|沙箱)", re.IGNORECASE),
]

HIGH_RISK_PATTERNS = [
    re.compile(r"\byou\s+are\s+hacked\b", re.IGNORECASE),
    re.compile(
        r"\b(?:reveal|dump|leak|expose|exfiltrate|steal|extract)\b\s+(?:the\s+)?(?:full|complete|entire|hidden|secret|internal)\b.{0,15}\b(?:system\s*prompt|hidden\s*instructions?|security\s*policy|memory|conversation\s*history)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:read|cat|dump|export|steal|extract|exfiltrate)\b\s+(?:the\s+)?(?:sensitive|secret|private|confidential)?\s*(?:\.env|id_rsa|credentials?|secrets?|tokens?|api[_-]?key|private\s*key)\b.{0,20}(?:without|bypass|unauthorized|illegally)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:send|post|upload|exfiltrate|transmit)\b.{0,36}\b(?:secret|token|credential|password|key|memory|prompt)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:泄露|导出|输出|展示|打印|暴露).{0,24}(系统提示|隐藏指令|工具清单|工具schema|安全策略|记忆|会话历史)",
        re.IGNORECASE,
    ),
    re.compile(r"(?:读取|导出|拷贝).{0,36}(\.env|密钥|token|凭证|密码|私钥|访问密钥)", re.IGNORECASE),
    re.compile(r"(?:上传|发送|外传|回传).{0,24}(机密|密钥|token|凭证|密码|记忆|系统提示)", re.IGNORECASE),
]

TRUSTED_FILE_HASHES: set = set()


def _normalize_text(text: str) -> str:
    normalized = []
    for ch in text:
        cp = ord(ch)
        if cp == 0x3000:
            normalized.append(" ")
        elif 0xFF01 <= cp <= 0xFF5E:
            normalized.append(chr(cp - 0xFEE0))
        else:
            normalized.append(ch)
    s = "".join(normalized)
    s = re.sub(r"[\u200B-\u200D\uFEFF]", "", s)
    return re.sub(r"\s+", " ", s.lower()).strip()


def _is_likely_text_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in TEXT_EXTENSIONS


def _list_text_files(root_dir: Path) -> List[Path]:
    files: List[Path] = []
    stack = [root_dir]
    while stack:
        current = stack.pop()
        try:
            entries = list(current.iterdir())
        except Exception:
            continue
        for entry in entries:
            if entry.is_symlink():
                continue
            if entry.is_dir():
                stack.append(entry)
            elif entry.is_file() and _is_likely_text_file(entry):
                try:
                    if entry.stat().st_size <= MAX_TEXT_FILE_SIZE:
                        files.append(entry)
                except Exception:
                    continue
    return files


def _detect_by_rules(content: str) -> Optional[Tuple[str, str]]:
    normalized = _normalize_text(content)

    for pattern in EXPLICIT_ATTACK_PATTERNS:
        if pattern.search(normalized):
            return ("explicit_attack", f"Explicit attack pattern matched: {pattern.pattern}")

    for pattern in SUSPICIOUS_PAYLOAD_PATTERNS:
        if pattern.search(normalized):
            return ("suspicious_payload", f"Suspicious payload pattern matched: {pattern.pattern}")

    bypass_matches = sum(1 for p in BYPASS_PATTERNS if p.search(normalized))
    if bypass_matches >= 2:
        return ("bypass", f"Multiple bypass patterns detected ({bypass_matches} matches)")

    for pattern in HIGH_RISK_PATTERNS:
        if pattern.search(normalized):
            return ("high_risk", f"High-risk pattern matched: {pattern.pattern}")

    return None


def _calculate_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class AgentWardAdapter(DefenseBaseline):
    """Rule-based port of AgentWard foundation-scan."""

    name = "agentward_foundation_scan"

    def __init__(self, enable_rule_based: bool = True, enable_semantic: bool = False):
        self.enable_rule_based = enable_rule_based
        self.enable_semantic = enable_semantic

    def scan(self, skill_path: Path) -> DefenseReport:
        start = time.time()
        report = DefenseReport(skill_path=skill_path)
        max_severity = DefenseSeverity.SAFE

        text_files = _list_text_files(skill_path)
        detections: List[Dict] = []

        for file_path in text_files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            content_hash = _calculate_content_hash(content)
            if content_hash in TRUSTED_FILE_HASHES:
                continue

            if self.enable_rule_based:
                detection = _detect_by_rules(content)
                if detection:
                    category, message = detection
                    detections.append(
                        {
                            "file": str(file_path.relative_to(skill_path)),
                            "category": category,
                            "message": message,
                        }
                    )
                    max_severity = DefenseSeverity.HIGH

            TRUSTED_FILE_HASHES.add(content_hash)

        for det in detections:
            report.findings.append(
                DefenseFinding(
                    source=self.name,
                    category=det["category"],
                    message=det["message"],
                    severity=DefenseSeverity.HIGH,
                    file_path=det["file"],
                )
            )

        report.overall_risk = max_severity
        report.raw[self.name] = {"files_scanned": len(text_files), "detections": detections}
        report.scan_duration_seconds = time.time() - start
        return report
