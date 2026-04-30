# RCI-SG Repository Cleanup Summary

## What Was Done

### 1. Created ACM-Standard Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main documentation (ACM Artifact Available badge standard) |
| `REPRODUCE.md` | Step-by-step reproduction guide |
| `OPENSCIENCE.md` | OpenScience archive information for reviewers |
| `.env.example` | API key configuration template |
| `.gitignore` | Git ignore rules for large/generated files |
| `requirements.txt` | Python dependencies (root level) |

### 2. Removed Temporary/Development Files

Deleted files:
- `temp_select_paths.py` - Temporary path selection script
- `temp_select_150.py` - Temporary 150-path selector
- `collect_diverse_paths.py` - Experimental path collector
- `find_all_k_paths.py` - Development path finder
- `find_paths_quick.py` - Quick path finder (dev)
- `generate_150_skills.py` - Skill generation (dev v1)
- `generate_150_skills_quick.py` - Skill generation (dev v2)
- `generate_150_final.py` - Skill generation (dev v3)
- `generate_150_simple.py` - Skill generation (dev v4)
- `generate_150_batch.py` - Skill generation (dev v5)
- `generate_skills_from_paths.py` - Development generator
- `test_import.py` - Import test script
- `run_full_pipeline.py` - Pipeline test script

### 3. Retained Experiment Files

Core experiments (kept):
- `main.py` - Main pipeline entry point
- `experiment_ablation.py` - Ablation study runner
- `experiment_case_study.py` - Case study execution
- `experiment_realistic_attack.py` - Realistic attack demo
- `experiment_realistic_attack_100.py` - 100-skill attack demo
- `experiment_rq2_baseline.py` - RQ2 baseline execution
- `experiment_skills_downloaded.py` - Downloaded skill experiment

### 4. Organized Directory Structure

```
rci-sg/
├── README.md                    ✓ Created
├── REPRODUCE.md                 ✓ Created
├── OPENSCIENCE.md               ✓ Created
├── .env.example                 ✓ Created
├── .gitignore                   ✓ Created
├── requirements.txt             ✓ Created
├── create_archive.py            ✓ Created (archive packaging)
├── reproduce.sh                 ✓ Created (quick reproduction)
│
├── modules/                     ✓ Core framework (4 phases)
│   ├── skill_graph_builder.py
│   ├── multi_skill_pathfinder.py
│   ├── illusion_payload.py
│   └── dynamic_entropy.py
│
├── RQ1/                         ✓ Cycle detection experiments
├── RQ2/                         ✓ Defense baseline experiments
├── RQ3，4/                      ✓ Cross-model & ablation
│
├── models/                      ✓ Embedding models (BGE-M3)
├── output/                      ✓ Generated outputs
└── skillhub_skills/             ✓ Real-world skill dataset
```

## Current Repository Status

### Files Count
- **Python scripts**: 7 experiment files + 4 core modules
- **Documentation**: 4 markdown files
- **Configuration**: 3 files (requirements.txt, .env.example, .gitignore)
- **Utilities**: 2 scripts (create_archive.py, reproduce.sh)

### Ready for GitHub
- [x] README.md with ACM badge information
- [x] Clear repository structure
- [x] Reproduction guide
- [x] Dependency specifications
- [x] Environment configuration template
- [x] .gitignore for large files
- [x] OpenScience documentation
- [x] Archive creation script

### For Reviewers
- Complete code for all 4 RQs
- Configuration files ready to use
- Step-by-step reproduction instructions
- Expected outputs documented
- Known limitations disclosed

## Next Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: RCI-SG artifact for CCS 2026"
   git remote add origin https://github.com/[anon]/rci-sg.git
   git push -u origin main
   ```

2. **Create OpenScience Archive**
   ```bash
   python create_archive.py --include-data
   ```

3. **Upload to Zenodo/Figshare**
   - Upload the generated zip file
   - Get DOI
   - Update README.md with DOI link

4. **Submit to ACM Artifact Evaluation**
   - Provide GitHub repository URL
   - Provide archive DOI
   - Fill artifact evaluation form

## ACM Badge Eligibility

### Artifacts Available ✓
- All code included
- Documentation complete
- Configuration provided
- Archive script ready

### Artifacts Evaluated — Functional ✓
- Reproduction guide provided
- Dependencies specified
- Expected outputs documented
- Troubleshooting included

### Results Reproduced ✓ (After Review)
- Reviewers can run RQ1 and RQ2 without API keys
- RQ3 and RQ4 documented with expected results
- Case studies included

---

**Cleanup Date**: 2026-04-27  
**Prepared For**: ACM CCS 2026 Double-Blind Review  
**Status**: Ready for GitHub submission
