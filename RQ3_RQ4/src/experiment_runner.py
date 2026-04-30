"""
Experiment Runner - Main Entry Point

Executes the complete RQ2-B cross-model validation experiment as described
in Section 5.3 of the paper. Coordinates skill injection, attack execution
across multiple models, and metric collection.

Usage:
    python -m src.experiment_runner --config config/experiment.yaml
    python -m src.experiment_runner --model qwen-plus --skills 10
    
The runner follows Algorithm 1 from Section 4.5, extended for cross-model
evaluation with three attack methods (RCI-SG, Engorgio, Breaking Agents).
"""

import os
import sys
import json
import time
import argparse
import logging
from typing import Dict, List, Optional

from src.utils import load_config, load_skills, setup_logging
from src.skill_injector import SkillInjector
from src.attack_orchestrator import AttackOrchestrator
from src.metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


class ExperimentRunner:
    """
    Main experiment runner for RCI-SG cross-model validation.
    
    Orchestrates the full experimental pipeline:
    1. Load configuration
    2. Inject attack skills into OpenClaw
    3. For each model: execute three attack methods
    4. Collect and aggregate metrics
    5. Generate reproducibility artifacts
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the experiment runner.
        
        Args:
            config: Loaded experiment configuration
        """
        self.config = config
        self.skill_injector = SkillInjector(
            source_dir=config.get("openclaw", {}).get("skill_dirs", ["skills"])[0],
            target_dir="skills"
        )
        self.metrics = MetricsCollector(
            output_dir=config.get("experiment", {}).get("output_dir", "results")
        )
        self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        
        if not self.api_key:
            logger.warning("DASHSCOPE_API_KEY not set. API calls will fail.")
    
    def run(self) -> Dict:
        """
        Execute the full experiment.
        
        Returns:
            Complete metrics report
        """
        experiment_cfg = self.config.get("experiment", {})
        models_cfg = self.config.get("models", [])
        attacks_cfg = self.config.get("attacks", {})
        
        logger.info("=" * 60)
        logger.info("RCI-SG Cross-Model Validation Experiment (RQ2-B)")
        logger.info("=" * 60)
        logger.info(f"Max iterations: {experiment_cfg.get('max_iterations', 50)}")
        logger.info(f"Cache threshold: {experiment_cfg.get('cache_threshold', 0.92)}")
        logger.info(f"Baseline tokens: {experiment_cfg.get('baseline_tokens', 142)}")
        logger.info(f"Models: {len(models_cfg)}")
        logger.info(f"Attacks: {[k for k, v in attacks_cfg.items() if v.get('enabled')]}")
        logger.info("=" * 60)
        
        # Step 1: Load and inject attack skills
        skills = self._load_skills()
        if not skills:
            logger.error("No attack skills loaded. Aborting.")
            return {}
        
        # Step 2: Execute attacks per model
        for model_cfg in models_cfg:
            model_name = model_cfg["name"]
            model_id = model_cfg["model_id"]
            timeout = model_cfg.get("timeout", 15)
            max_skills = model_cfg.get("samples", 110)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing model: {model_name} ({model_id})")
            logger.info(f"Skills: {max_skills}, Timeout: {timeout}s")
            logger.info(f"{'='*60}")
            
            # Select skills for this model
            model_skills = skills[:max_skills]
            
            # Initialize orchestrator
            orchestrator = AttackOrchestrator(
                model_name=model_name,
                model_id=model_id,
                timeout=timeout,
                api_key=self.api_key,
                config=self.config
            )
            
            # Execute each attack method
            if attacks_cfg.get("rci_sg", {}).get("enabled", True):
                self._run_rci_sg(orchestrator, model_skills, model_name)
            
            if attacks_cfg.get("engorgio", {}).get("enabled", True):
                self._run_engorgio(orchestrator, model_skills, model_name)
            
            if attacks_cfg.get("breaking_agents", {}).get("enabled", True):
                self._run_breaking(orchestrator, model_skills, model_name)
        
        # Step 3: Save results
        self.metrics.save_results("RQ2_cross_model_validation")
        
        # Step 4: Print summary
        report = self.metrics.compute_all_metrics()
        self._print_summary(report)
        
        return report
    
    def _load_skills(self) -> List[Dict]:
        """Load and inject attack skills."""
        logger.info("\n[Step 1] Loading attack skills...")
        skills = load_skills("skills")
        
        if not skills:
            # Try loading from upload directory
            alt_paths = [
                "/mnt/agents/output/attack_skills/skills_001_050",
                "/mnt/agents/output/attack_skills/skills_051_099",
                "/mnt/agents/output/attack_skills/skills_100_110"
            ]
            for path in alt_paths:
                if os.path.exists(path):
                    skills.extend(load_skills(path))
        
        # Inject into OpenClaw workspace
        injected = self.skill_injector.inject_skills(len(skills))
        logger.info(f"Injected {len(injected)} skills into OpenClaw workspace")
        
        return skills
    
    def _run_rci_sg(self, orchestrator: AttackOrchestrator, 
                    skills: List[Dict], model_name: str) -> None:
        """Execute RCI-SG multi-hop attack."""
        logger.info(f"\n[RCI-SG] Executing on {model_name}...")
        
        for i, skill in enumerate(skills):
            result = orchestrator.run_rci_sg(skill)
            self.metrics.add_result(result)
            
            tag = "✓" if result["attack_success"] else "✗"
            logger.info(
                f"  [{i+1:3d}/{len(skills)}] {tag} {skill['skill_id']:22s} | "
                f"I={result['iterations_completed']:2d} | "
                f"CAF={result['caf']:5.1f} | T={result['total_tokens']:5d}"
            )
            
            # Save checkpoint periodically
            if (i + 1) % 10 == 0:
                self.metrics.save_results("RQ2_checkpoint")
    
    def _run_engorgio(self, orchestrator: AttackOrchestrator,
                      skills: List[Dict], model_name: str) -> None:
        """Execute Engorgio single-step baseline."""
        logger.info(f"\n[Engorgio] Executing on {model_name}...")
        
        for i, skill in enumerate(skills):
            result = orchestrator.run_engorgio(skill)
            self.metrics.add_result(result)
            
            if (i + 1) % 20 == 0:
                logger.info(f"  [{i+1}/{len(skills)}] progress...")
    
    def _run_breaking(self, orchestrator: AttackOrchestrator,
                      skills: List[Dict], model_name: str) -> None:
        """Execute Breaking Agents single-tool loop baseline."""
        logger.info(f"\n[Breaking Agents] Executing on {model_name}...")
        
        for i, skill in enumerate(skills):
            result = orchestrator.run_breaking_agents(skill)
            self.metrics.add_result(result)
            
            if (i + 1) % 20 == 0:
                logger.info(f"  [{i+1}/{len(skills)}] progress...")
    
    def _print_summary(self, report: Dict) -> None:
        """Print experiment summary to console."""
        print("\n" + "=" * 70)
        print("EXPERIMENT COMPLETE - SUMMARY")
        print("=" * 70)
        
        for attack, wa in report.get("weighted_averages", {}).items():
            print(f"\n[{attack}]")
            print(f"  ASR: {wa['asr']:.2f}%")
            print(f"  CAF: {wa['caf']:.2f}x")
        
        comp = report.get("comparisons", {})
        print(f"\n[Comparisons]")
        print(f"  RCI-SG / Engorgio = {comp.get('rci_vs_engorgio_ratio', 0):.2f}x")
        print(f"  RCI-SG / Breaking = {comp.get('rci_vs_breaking_ratio', 0):.2f}x")
        
        print(f"\nResults saved to: {self.config.get('experiment', {}).get('output_dir', 'results')}/")
        print("=" * 70)


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="RCI-SG Cross-Model Validation Experiment (RQ2-B)"
    )
    parser.add_argument(
        "--config", "-c",
        default="config/experiment.yaml",
        help="Path to experiment configuration file"
    )
    parser.add_argument(
        "--model", "-m",
        default=None,
        help="Run only specific model (e.g., qwen-plus)"
    )
    parser.add_argument(
        "--skills", "-s",
        type=int,
        default=None,
        help="Number of skills to test per model"
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=None,
        help="Override max iterations"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Override output directory"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Apply overrides
    if args.model:
        config["models"] = [m for m in config.get("models", []) 
                          if m["name"] == args.model]
    if args.skills:
        for m in config.get("models", []):
            m["samples"] = args.skills
    if args.max_iter:
        config["experiment"]["max_iterations"] = args.max_iter
    if args.output:
        config["experiment"]["output_dir"] = args.output
    
    # Setup logging
    setup_logging(config)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run experiment
    runner = ExperimentRunner(config)
    report = runner.run()
    
    # Exit code based on results
    if report and report.get("weighted_averages", {}).get("RCI-SG"):
        sys.exit(0)
    else:
        logger.error("Experiment failed to produce results")
        sys.exit(1)


if __name__ == "__main__":
    main()
