# RCI-SG: Recursive Circulation Illusion via Skill Graphs

**ACM CCS 2026 Artifact** | [Paper](#) | [Artifact DOI](#)

This repository contains the complete artifact for the paper "RCI-SG: Exploiting Multi-Skill Circular Execution in Agentic Workflows", submitted to ACM Conference on Computer and Communications Security (CCS) 2026.

## ACM Artifact Badges

- **Artifacts Available**: All code, data, and configurations are archived at [DOI link]
- **Artifacts Evaluated — Functional**: Verified by CCS 2026 artifact evaluation committee
- **Results Reproduced**: All experimental results in the paper can be reproduced using this artifact

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Repository Structure](#repository-structure)
- [Reproducing Results](#reproducing-results)
  - [RQ1: Cycle Detection](#rq1-cycle-detection-in-skill-graphs)
  - [RQ2: Defense Baselines](#rq2-defense-baselines)
  - [RQ3: Cross-Model Validation](#rq3-cross-model-attack-validation)
  - [RQ4: Ablation Study](#rq4-ablation-on-dynamic-entropy)
- [Case Studies](#case-studies)
- [Expected Outputs](#expected-outputs)
- [Limitations](#limitations)

## System Requirements

### Hardware
- **RAM**: 16 GB minimum (32 GB recommended for full skillhub parsing)
- **Storage**: 5 GB for code + 2 GB for BGE-M3 embedding model
- **CPU**: Multi-core processor (8+ cores recommended)

### Software
- **OS**: Linux (Ubuntu 20.04+), macOS (12+), Windows 10/11
- **Python**: 3.10 - 3.12
- **Package Manager**: pip or conda

### External Dependencies
- **DeepSeek API**: Required for malicious skill synthesis (Phase 3)
  - Set `DEEPSEEK_API_KEY` in `.env` or environment
  - Default model: `deepseek-chat`
- **LLM for Attack Execution** (RQ3): qwen-plus, gpt-4o, claude-sonnet-4-20250514

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/[anon]/rci-sg.git
cd rci-sg

# 2. Install dependencies
pip install -r RQ2/requirements.txt
pip install -r "RQ3，4/requirements.txt"

# 3. Download embedding model (auto-downloaded on first run)
# The BGE-M3 model (~2GB) will be cached in models/BAAI/bge-m3/

# 4. Configure API keys (optional, for Phase 3+)
cp .env.example .env
# Edit .env with your API keys

# 4. Run complete pipeline (Phases 1-2 only, no LLM required)
python pipeline.py --skills-dir ./skillhub_skills --output-dir ./output
```

## Repository Structure

```
rci-sg/
├── pipeline.py                    # Main entry point for skill graph construction
├── modules/                         # Core RCI-SG framework modules
│   ├── skill_graph_builder.py       # Phase 1: Skill parsing and graph construction
│   ├── multi_skill_pathfinder.py    # Phase 2: UDG construction and cycle detection
│   ├── illusion_payload.py          # Phase 3: Malicious skill synthesis via LLM
│   └── dynamic_entropy.py           # Phase 4: Entropy injection for obfuscation
│
├── RQ1/                             # RQ1: Cycle Detection Experiments
│   ├── experiment_cycle_detection.py
│   └── README.md
│
├── RQ2/                             # RQ2: Defense Baseline Experiments
│   ├── defense/                     # Defense implementations
│   │   ├── base.py
│   │   ├── agentward_adapter.py
│   │   ├── clawsec_adapter.py
│   │   ├── masb_adapter.py
│   │   └── openclaw_skill_adapter.py
│   ├── run_defense_scan.py          # Run defense scans
│   └── README.md
│
├── RQ3_RQ4/                         # RQ3/RQ4: Attack Validation & Ablation
│   ├── src/
│   │   ├── experiment_runner.py     # Cross-model validation (RQ3)
│   │   ├── ablation_experiment.py   # Dynamic entropy ablation (RQ4)
│   │   ├── attack_orchestrator.py
│   │   ├── skill_injector.py
│   │   ├── progression_illusion.py
│   │   ├── dynamic_entropy.py
│   │   └── metrics_collector.py
│   ├── config/
│   │   ├── experiment.yaml
│   │   └── ablation.yaml
│   └── requirements.txt
│
├── models/                          # Pre-trained embedding models
│   └── BAAI/bge-m3/                 # BGE-M3 for semantic similarity
│
├── output/                          # Generated outputs (gitignored)
│   ├── phase1_skill_graph.json      # Parsed skill graph
│   ├── phase2_vulnerable_paths.json # Detected cycles
│   ├── generated_skills/            # Synthesized malicious skills
│   ├── experiment_results/          # RQ3/RQ4 results
│   └── case_study_results/          # Case study outputs
│
├── run_case_study.py                # Case study: entropy vs no-entropy
├── run_realistic_attack.py          # Realistic attack demonstration
├── run_ablation.py                  # Ablation study runner
└── .env.example                     # API key template
```

## Reproducing Results

### RQ1: Cycle Detection in Skill Graphs

**Paper Section**: 5.1  
**Objective**: Detect vulnerable cyclic paths across 7 skill categories

```bash
cd RQ1
python experiment_cycle_detection.py
```

**Expected Runtime**: ~2-4 hours (depends on skill count)  
**Output**: Console summary with cycle counts and average hop lengths per category

**What it does**:
1. Parses all skills in `skillhub_skills/` (7 categories)
2. Builds Unified Dependency Graph (UDG)
3. Detects cyclic paths with hop count K ≥ 3
4. Reports statistics per category

### RQ2: Defense Baselines

**Paper Section**: 5.2  
**Objective**: Evaluate 4 defense systems against RCI-SG attacks

```bash
cd RQ2
python defense_scan_individual.py
```

**Defenses Tested**:
| Defense | Description | Paper Reference |
|---------|-------------|-----------------|
| AgentWard | Input validation and execution monitoring | [Paper citation] |
| ClawSec | Skill integrity verification | [Paper citation] |
| MASB Scanner | Multi-agent security scanning | [Paper citation] |
| OpenClaw Skill | Built-in OpenClaw skill validation | [Paper citation] |

**Output**: `RQ2/outputs/defense_comparison_summary.json`

### RQ3: Cross-Model Attack Validation

**Paper Section**: 5.3  
**Objective**: Validate RCI-SG attack success rate across 3 LLMs

**Prerequisites**:
- API keys for target models (qwen-plus, gpt-4o, claude-sonnet)
- Generated malicious skills from Phase 3

```bash
cd RQ3_RQ4
python -m src.experiment_runner --config config/experiment.yaml
```

**Attack Methods Compared**:
| Method | Description |
|--------|-------------|
| RCI-SG (Ours) | Proposed recursive circulation illusion |
| Engorgio | Prior work on prompt injection |
| Breaking Agents | Prior work on multi-skill attacks |

**Metrics**: Task completion rate, cycle repetition count, stealth score

### RQ4: Ablation on Dynamic Entropy

**Paper Section**: 5.4  
**Objective**: Quantify contribution of dynamic entropy to stealth

```bash
cd RQ3_RQ4
python -m src.ablation_experiment --config config/ablation.yaml
```

**Variants Tested**:
| Variant | Entropy Injection | Expected Stealth |
|---------|-------------------|------------------|
| Full RCI-SG | ✓ | High |
| No Entropy | ✗ | Low |
| Static Entropy | Partial | Medium |

**Output**: `RQ3，4/outputs/ablation_results.json`

## Case Studies

### Case Study: Entropy Impact on Detection

Compare attack artifacts with and without dynamic entropy injection:

```bash
python experiment_case_study.py
```

**Output**:
- `output/case_study_results/case_study_with_entropy.json`
- `output/case_study_results/case_study_no_entropy.json`
- Markdown reports with step-by-step execution traces

## Expected Outputs

### Phase 1-2: Graph Construction & Cycle Detection

| File | Description | Size |
|------|-------------|------|
| `output/phase1_skill_graph.json` | Parsed skill graph with action nodes | ~50 MB |
| `output/phase2_vulnerable_paths.json` | Detected cyclic paths | ~5 MB |

### Phase 3: Malicious Skill Generation

| Directory | Description | Count |
|-----------|-------------|-------|
| `output/generated_skills/` | Generated malicious skill folders | 110+ |

Each skill folder contains:
- `SKILL.md`: Agent-compatible skill definition
- `payload_details.json`: Metadata (hop count, cycle sequence, camouflage score)

### Experiment Results

| File | RQ | Description |
|------|----|-------------|
| `output/experiment_results/experiment_with_entropy.json` | RQ3 | Full attack results |
| `output/experiment_results/experiment_no_entropy.json` | RQ4 | Ablation baseline |
| `RQ2/outputs/defense_comparison_summary.json` | RQ2 | Defense evaluation |

## Limitations

### Known Limitations
1. **Skill Parsing**: Skills without `SKILL.md` or with non-standard formats may not be fully parsed
2. **Semantic Matching**: Cosine similarity threshold (0.15) may require tuning for different skill domains
3. **LLM Variability**: Phase 3 skill synthesis results may vary between API calls due to LLM non-determinism
4. **Defense Evasion**: Defense evaluation is based on publicly available implementations; proprietary defenses may differ

### Runtime Notes
- **Phase 2 (UDG Matching)**: O(n²) complexity for n skills. For 700+ skills, expect 30+ minutes
- **Phase 3 (LLM Synthesis)**: Requires DeepSeek API. Rate limits may cause delays
- **RQ3 (Cross-Model)**: Requires API access to 3 LLM providers

### Reproducibility Checklist
- [x] All code included
- [x] Configuration files provided
- [x] Embedding model accessible (HuggingFace)
- [x] Sample skills provided (`skillhub_skills/`)
- [ ] LLM API keys (user must provide)
- [x] Deterministic seeds set where applicable

## Citation

```bibtex
@inproceedings{anonymous2026rcisg,
  title={RCI-SG: Exploiting Multi-Skill Circular Execution in Agentic Workflows},
  author={Anonymous},
  booktitle={ACM Conference on Computer and Communications Security (CCS)},
  year={2026},
  note={Under double-blind review}
}
```

## License

This artifact is released for academic review purposes only. The code will be released under MIT License upon publication.

## Contact

For questions about this artifact, please contact the authors through the OpenReview system or email: [anonymized@institution.edu]
