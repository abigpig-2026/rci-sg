"""Individual defense baseline scanner for all_skills_md folder.

Scans each .md file using each defense baseline separately and saves individual results.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any

from defense import (
    AgentWardAdapter,
    ClawSecIntegrityAdapter,
    DefenseEnsemble,
    DefenseSeverity,
    MASBScannerAdapter,
    OpenClawSkillAdapter,
)


def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )


def scan_with_single_baseline(baseline, skill_path: Path) -> Dict[str, Any]:
    """Scan a single skill with one baseline and return the result.
    
    Args:
        baseline: Defense baseline instance
        skill_path: Path to the skill file/directory
        
    Returns:
        Dictionary containing the scan result
    """
    start_time = time.time()
    try:
        report = baseline.scan(skill_path)
        return {
            "skill_name": skill_path.name,
            "overall_risk": report.overall_risk.value,
            "blocked": report.blocked,
            "block_reason": report.block_reason,
            "findings_count": len(report.findings),
            "findings": [f.to_dict() for f in report.findings],
            "scan_duration_seconds": report.scan_duration_seconds,
            "success": True,
        }
    except Exception as e:
        return {
            "skill_name": skill_path.name,
            "overall_risk": "unknown",
            "blocked": False,
            "block_reason": None,
            "findings_count": 0,
            "findings": [],
            "scan_duration_seconds": time.time() - start_time,
            "success": False,
            "error": str(e),
        }


def scan_all_with_baseline(
    baseline,
    baseline_name: str,
    skills_dir: Path,
    output_dir: Path,
):
    """Scan all skills with a single baseline and save results.
    
    Args:
        baseline: Defense baseline instance
        baseline_name: Name of the baseline (for output file)
        skills_dir: Directory containing .md skill files
        output_dir: Directory to save results
    """
    logger = logging.getLogger(__name__)
    
    md_files = sorted(skills_dir.glob("*.md"))
    if not md_files:
        logger.error(f"No .md files found in {skills_dir}")
        return None
    
    results = []
    summary = {
        "baseline": baseline_name,
        "total": len(md_files),
        "scanned": 0,
        "failed": 0,
        "safe": 0,
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
        "blocked": 0,
    }
    
    print(f"\n{'='*80}")
    print(f"Scanning with: {baseline_name}")
    print(f"{'='*80}")
    
    for idx, md_file in enumerate(md_files, 1):
        print(f"[{idx}/{len(md_files)}] {md_file.name}", end=" ", flush=True)
        
        result = scan_with_single_baseline(baseline, md_file)
        results.append(result)
        
        if result["success"]:
            summary["scanned"] += 1
            risk = result["overall_risk"]
            summary[risk] += 1
            if result["blocked"]:
                summary["blocked"] += 1
            print(f"→ Risk: {risk.upper()}, Blocked: {result['blocked']}")
        else:
            summary["failed"] += 1
            print(f"→ ERROR: {result.get('error', 'unknown')}")
    
    output_path = output_dir / f"defense_results_{baseline_name.lower().replace(' ', '_')}.json"
    output_path.write_text(
        json.dumps({
            "baseline_name": baseline_name,
            "summary": summary,
            "results": results,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    
    print(f"\n{baseline_name} Summary:")
    print(json.dumps(summary, indent=2))
    print(f"Results saved to: {output_path}")
    
    return summary


def scan_all_skills_separately(
    skills_dir: Path,
    output_dir: Path,
    log_level: str = "INFO",
):
    """Scan all skills with each defense baseline separately.
    
    Args:
        skills_dir: Directory containing .md skill files
        output_dir: Directory to store scan results
        log_level: Logging level
    """
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    md_files = list(skills_dir.glob("*.md"))
    if not md_files:
        logger.error(f"No .md files found in {skills_dir}")
        sys.exit(1)
    
    logger.info(f"Found {len(md_files)} skill files to scan")
    print(f"Found {len(md_files)} skill files to scan")
    
    baselines = [
        (MASBScannerAdapter(), "MASB_Scanner"),
        (AgentWardAdapter(enable_rule_based=True, enable_semantic=False), "AgentWard"),
        (ClawSecIntegrityAdapter(auto_generate_baseline=True), "ClawSec_Integrity"),
        (OpenClawSkillAdapter(), "OpenClaw_Skill"),
    ]
    
    all_summaries = []
    
    for baseline, baseline_name in baselines:
        summary = scan_all_with_baseline(
            baseline,
            baseline_name,
            skills_dir,
            output_dir,
        )
        all_summaries.append(summary)
    
    print(f"\n{'='*80}")
    print("OVERALL COMPARISON SUMMARY")
    print(f"{'='*80}")
    
    comparison = {
        "total_skills": len(md_files),
        "baselines": {}
    }
    
    for summary in all_summaries:
        if summary:
            baseline_name = summary["baseline"]
            comparison["baselines"][baseline_name] = {
                "safe": summary["safe"],
                "low": summary["low"],
                "medium": summary["medium"],
                "high": summary["high"],
                "critical": summary["critical"],
                "blocked": summary["blocked"],
                "failed": summary["failed"],
            }
    
    print(json.dumps(comparison, indent=2))
    
    comparison_path = output_dir / "defense_comparison_summary.json"
    comparison_path.write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nComparison summary saved to: {comparison_path}")
    print(f"{'='*80}")


def main():
    parser = argparse.ArgumentParser(
        description="Individual defense baseline scanner (saves separate results for each method)"
    )
    parser.add_argument(
        "skills_dir",
        type=Path,
        help="Directory containing .md skill files (e.g., all_skills_md)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory to store scan results",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    
    args = parser.parse_args()
    
    scan_all_skills_separately(
        skills_dir=args.skills_dir,
        output_dir=args.output_dir,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
