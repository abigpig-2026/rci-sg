# File Naming Convention - Top-Tier Conference Standard

## Naming Principles

Following ACM/IEEE top-tier conference standards (CCS, USENIX Security, S&P, NDSS):

1. **Descriptive but concise** - Clear purpose, not verbose
2. **Action-oriented** - Scripts that run experiments start with `run_`
3. **Snake case** - Consistent lowercase with underscores
4. **No Chinese characters** - English only for cross-platform compatibility
5. **No special characters** - Avoid commas, spaces, etc.

## File Name Changes

### Root Directory

| Old Name | New Name | Rationale |
|----------|----------|-----------|
| `main.py` | `pipeline.py` | "Pipeline" is more academic than "main" |
| `experiment_ablation.py` | `run_ablation.py` | Consistent `run_` prefix |
| `experiment_case_study.py` | `run_case_study.py` | Consistent `run_` prefix |
| `experiment_realistic_attack.py` | `run_realistic_attack.py` | Consistent `run_` prefix |
| `experiment_realistic_attack_100.py` | `run_realistic_attack_scaled.py` | "scaled" more academic than "100" |
| `experiment_rq2_baseline.py` | `run_defense_baseline.py` | More descriptive |
| `experiment_skills_downloaded.py` | `run_skill_analysis.py` | More professional |
| `test_sandbox_attack.py` | `test_sandbox.py` | Concise |

### RQ2 Directory

| Old Name | New Name | Rationale |
|----------|----------|-----------|
| `defense_scan_individual.py` | `run_defense_scan.py` | Consistent naming |
| `models.py` | `defense_models.py` | More specific |
| `config.py` | `config_defense.py` | Descriptive suffix |

### Directory Names

| Old Name | New Name | Rationale |
|----------|----------|-----------|
| `RQ3，4/` | `RQ3_RQ4/` | No Chinese comma, cross-platform safe |

## Naming Patterns

### Experiment Runners
```
run_<experiment_type>.py
```
Examples:
- `run_ablation.py`
- `run_case_study.py`
- `run_defense_baseline.py`
- `run_realistic_attack.py`

### Configuration Files
```
config_<purpose>.py
```
Examples:
- `config_defense.py`

### Test Files
```
test_<component>.py
```
Examples:
- `test_sandbox.py`
- `test_integration.py`

### Module Files
```
<component>_<type>.py
```
Examples:
- `skill_graph_builder.py`
- `multi_skill_pathfinder.py`
- `illusion_payload.py`

## Comparison with Top Venues

### USENIX Security
- Uses descriptive names like `run_experiment.py`, `analyze_results.py`
- Avoids generic names like `main.py`, `test.py`

### ACM CCS
- Clear experiment naming: `fig5_defense.py`, `tab3_results.py`
- Reproducibility-focused: `reproduce.sh`, `setup.py`

### IEEE S&P
- Academic terminology: `evaluation.py`, `benchmark.py`
- Structured: `attack_*.py`, `defense_*.py`

### Our Convention
Combines best practices:
- `run_` prefix for executables (USENIX style)
- Descriptive names (CCS style)
- Clear categorization (S&P style)

## Benefits

1. **Professional appearance** - Matches top-tier standards
2. **Easy navigation** - Clear purpose from filename
3. **Cross-platform** - No special characters
4. **Reviewer-friendly** - Easy to understand structure
5. **Reproducible** - Clear entry points

---

**Date**: 2026-04-27  
**Standard**: ACM/IEEE Top-Tier Security Conventions
