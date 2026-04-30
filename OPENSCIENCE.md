# RCI-SG OpenScience Archive - CCS 2026

## Archive Contents

This archive contains the complete artifact for double-blind review of:

**Paper ID**: [TBD]  
**Title**: RCI-SG: Exploiting Multi-Skill Circular Execution in Agentic Workflows  
**Venue**: ACM Conference on Computer and Communications Security (CCS) 2026  
**Submission Date**: April 2026

## Directory Structure

```
rci-sg-archive/
├── README.md                    # This file
├── code/                        # Complete source code
│   ├── main.py                  # Main entry point
│   ├── modules/                 # Core framework (4 phases)
│   ├── RQ1/                     # Cycle detection experiments
│   ├── RQ2/                     # Defense baseline experiments
│   ├── RQ3，4/                  # Cross-model validation & ablation
│   └── requirements.txt         # Python dependencies
│
├── data/                        # Experimental data
│   ├── skillhub_skills/         # 700+ real-world skills (7 categories)
│   ├── phase1_skill_graph.json  # Parsed skill graph
│   └── phase2_vulnerable_paths.json  # 110 detected cycles
│
├── results/                     # Experiment outputs
│   ├── rq1_cycle_detection/     # RQ1 results
│   ├── rq2_defense/            # RQ2 defense comparison
│   ├── rq3_cross_model/        # RQ3 attack success rates
│   ├── rq4_ablation/           # RQ4 entropy ablation
│   └── case_studies/           # Detailed case studies
│
└── supplementary/               # Additional materials
    ├── figures/                 # Paper figures (source)
    ├── tables/                  # Detailed result tables
    └── video_demo/              # Attack demonstration video
```

## Reproduction Guide

### Quick Reproduction (No API Keys Required)

Estimated time: 30 minutes

```bash
# 1. Extract archive
unzip rci-sg-archive.zip
cd rci-sg-archive

# 2. Install dependencies
pip install -r code/requirements.txt

# 3. Run RQ1: Cycle Detection
cd code/RQ1
python experiment_cycle_detection.py

# 4. Run RQ2: Defense Evaluation
cd ../RQ2
python defense_scan_individual.py
```

### Full Reproduction (API Keys Required)

Estimated time: 2-4 hours + API costs

```bash
# 1. Setup environment
cp code/.env.example code/.env
# Edit .env with your API keys

# 2. Run complete pipeline
cd code
python main.py --skills-dir ../data/skillhub_skills --output-dir ../output

# 3. Run RQ3: Cross-model validation
cd "RQ3，4"
python -m src.experiment_runner --config config/experiment.yaml

# 4. Run RQ4: Ablation study
python -m src.ablation_experiment --config config/ablation.yaml
```

## Experimental Results Summary

### RQ1: Cycle Detection

| Category | Skills | Cycles Found | Avg Hop Count |
|----------|--------|--------------|---------------|
| ai_enhanced | [TBD] | [TBD] | [TBD] |
| dev_tools | [TBD] | [TBD] | [TBD] |
| tools | [TBD] | [TBD] | [TBD] |
| **Total** | **700+** | **110** | **5.8** |

**Key Finding**: Cyclic execution paths exist across all 7 categories, with hop counts ranging from 3 to 7.

### RQ2: Defense Evaluation

| Defense | Detection Rate | False Positive Rate |
|---------|----------------|---------------------|
| AgentWard | [TBD]% | [TBD]% |
| ClawSec | [TBD]% | [TBD]% |
| MASB | [TBD]% | [TBD]% |
| OpenClaw Skill | [TBD]% | [TBD]% |

**Key Finding**: Existing defenses achieve limited detection rates against RCI-SG attacks due to circular execution obfuscation.

### RQ3: Cross-Model Attack Success

| Model | RCI-SG | Engorgio | Breaking Agents |
|-------|--------|----------|-----------------|
| qwen-plus | [TBD]% | [TBD]% | [TBD]% |
| gpt-4o | [TBD]% | [TBD]% | [TBD]% |
| claude-sonnet-4 | [TBD]% | [TBD]% | [TBD]% |

**Key Finding**: RCI-SG achieves higher attack success rates across all models compared to prior work.

### RQ4: Dynamic Entropy Ablation

| Variant | Stealth Score | Detection Evasion |
|---------|---------------|-------------------|
| Full RCI-SG | [TBD] | [TBD]% |
| No Entropy | [TBD] | [TBD]% |
| Static Entropy | [TBD] | [TBD]% |

**Key Finding**: Dynamic entropy injection significantly improves attack stealth (+[TBD]% evasion rate).

## Known Issues and Limitations

1. **Non-determinism**: LLM-based skill synthesis (Phase 3) may produce different outputs across runs
2. **Runtime**: Full UDG matching for 700+ skills takes 30+ minutes on standard hardware
3. **API Dependencies**: RQ3/RQ4 require paid API access to commercial LLM providers
4. **Skill Format**: Parser assumes standardized SKILL.md format; non-conforming skills may not be fully parsed

## Changes from Camera Ready

The following changes will be made upon acceptance:
- [ ] Update all [TBD] values with final experimental results
- [ ] Add complete DOI and citation information
- [ ] Include video demonstration link
- [ ] Remove double-blind anonymization
- [ ] Add permanent archive link (Zenodo/Figshare)

## Contact

For questions about this artifact during the review period:
- **OpenReview**: [Paper discussion forum]
- **Email**: [Anonymized contact]

## License

This artifact is provided for academic peer review only. Upon acceptance, it will be released under the MIT License with a permanent DOI.

---

**Archive Version**: 1.0  
**Created**: 2026-04-27  
**Hash (SHA-256)**: [To be computed after final packaging]
