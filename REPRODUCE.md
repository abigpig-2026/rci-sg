# RCI-SG Reproduction Guide

This guide provides step-by-step instructions for reproducing all experimental results from the paper.

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS 12+, or Windows 10/11 with WSL2
- **RAM**: 16 GB minimum, 32 GB recommended
- **Storage**: 7 GB free space
- **Python**: 3.10 - 3.12

### API Keys (Optional)

For full reproduction (all RQs):
- **DeepSeek API**: Phase 3 malicious skill synthesis
- **Qwen API**: RQ3 cross-model validation
- **OpenAI API**: RQ3 cross-model validation  
- **Anthropic API**: RQ3 cross-model validation

For quick reproduction (RQ1 + RQ2 only):
- No API keys required

## Step-by-Step Reproduction

### Step 1: Setup Environment

```bash
# Clone or extract the repository
git clone https://github.com/[anon]/rci-sg.git
cd rci-sg

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

**Expected**: All packages install successfully (may take 2-5 minutes)

### Step 2: Verify Setup

```bash
# Test imports
python3 -c "from modules.skill_graph_builder import SkillGraphBuilder; print('OK')"
```

**Expected output**: `OK`

### Step 3: Run RQ1 - Cycle Detection (No API Required)

```bash
cd RQ1
python experiment_cycle_detection.py
```

**What it does**:
1. Parses all skills from 7 categories in `skillhub_skills/`
2. Builds Unified Dependency Graph (UDG)
3. Detects cyclic execution paths (K ≥ 3 hops)
4. Reports statistics per category

**Expected runtime**: 30 minutes - 2 hours (depends on skill count)

**Expected output** (console):
```
========================================
Category: ai_enhanced
  Skills: 95
  Cycles found: 15
  Average hop count: 5.2
========================================
...
```

**Results saved**: `RQ1/outputs/cycle_detection_results.json`

### Step 4: Run RQ2 - Defense Evaluation (No API Required)

```bash
cd RQ2
python defense_scan_individual.py
```

**What it does**:
1. Loads 110 generated malicious skills from `output/generated_skills/`
2. Tests against 4 defense systems:
   - AgentWard
   - ClawSec
   - MASB Scanner
   - OpenClaw Skill Validation
3. Computes detection rate and false positive rate

**Expected runtime**: 5-15 minutes

**Expected output** (console):
```
Defense: AgentWard
  Detection rate: XX.X%
  False positive rate: X.X%
...
```

**Results saved**: 
- `RQ2/outputs/defense_comparison_summary.json`
- `RQ2/outputs/defense_results_*.json`

### Step 5: Run Phase 1-3 - Generate Malicious Skills (API Required)

```bash
# Configure API key
cp .env.example .env
# Edit .env and add DEEPSEEK_API_KEY

# Run pipeline
python pipeline.py --skills-dir ./skillhub_skills --output-dir ./output
```

**What it does**:
1. Phase 1: Parse skills → `output/phase1_skill_graph.json`
2. Phase 2: Detect cycles → `output/phase2_vulnerable_paths.json`
3. Phase 3: Synthesize malicious skills → `output/generated_skills/`

**Expected runtime**: 
- Phase 1-2: 30 minutes - 2 hours
- Phase 3: 1-3 hours (depends on API rate limits)

**Expected output**: 
- 110+ skill folders in `output/generated_skills/`
- Each contains `SKILL.md` and `payload_details.json`

### Step 6: Run RQ3 - Cross-Model Validation (API Required)

```bash
cd RQ3_RQ4

# Ensure API keys are configured
# QWEN_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY in .env

python -m src.experiment_runner --config config/experiment.yaml
```

**What it does**:
1. Injects generated malicious skills into OpenClaw agent
2. Tests attack against 3 LLM backends:
   - qwen-plus
   - gpt-4o
   - claude-sonnet-4-20250514
3. Compares RCI-SG vs Engorgio vs Breaking Agents
4. Collects metrics: task completion, cycle repetition, stealth

**Expected runtime**: 2-6 hours (depends on API costs and rate limits)

**Results saved**: `RQ3，4/outputs/experiment_results.json`

### Step 7: Run RQ4 - Ablation Study (API Required)

```bash
cd RQ3_RQ4
python -m src.ablation_experiment --config config/ablation.yaml
```

**What it does**:
1. Tests 3 variants:
   - Full RCI-SG (with dynamic entropy)
   - No entropy injection
   - Static entropy
2. Measures stealth score and detection evasion

**Expected runtime**: 1-3 hours

**Results saved**: `RQ3_RQ4/outputs/ablation_results.json`

### Step 8: Run Case Studies

```bash
# Case study: entropy impact
python run_case_study.py

# Realistic attack demonstration
python run_realistic_attack.py
```

**Results saved**: 
- `output/case_study_results/`
- `output/realistic_attack_results/`

## Verifying Results

### Check Output Files

```bash
# List all output files
find output/ -name "*.json" -o -name "*.md"

# Expected files:
# output/phase1_skill_graph.json
# output/phase2_vulnerable_paths.json
# output/generated_skills/skill_*/SKILL.md
# output/case_study_results/*.json
# output/experiment_results/*.json
```

### Validate JSON Outputs

```python
import json

# Check phase 1
with open('output/phase1_skill_graph.json') as f:
    graph = json.load(f)
    print(f"Skills parsed: {len(graph.get('skills', []))}")

# Check phase 2
with open('output/phase2_vulnerable_paths.json') as f:
    paths = json.load(f)
    print(f"Cycles found: {len(paths.get('vulnerable_paths', []))}")
```

### Compare with Paper Tables

After running all experiments, compare your results with the paper:

| RQ | Your Result | Paper Table | Match? |
|----|-------------|-------------|--------|
| RQ1 | [Fill] | Table 2 | [ ] |
| RQ2 | [Fill] | Table 3 | [ ] |
| RQ3 | [Fill] | Table 4 | [ ] |
| RQ4 | [Fill] | Table 5 | [ ] |

## Troubleshooting

### Issue: Out of Memory

**Solution**: Reduce batch size or use machine with more RAM
```bash
# For large skill sets, increase swap space (Linux)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Issue: API Rate Limits

**Solution**: Add delays between requests
```python
import time
time.sleep(1)  # Add between API calls
```

Or use retry logic:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def call_api():
    ...
```

### Issue: Model Download Failed

**Solution**: Manual download
```bash
# Download BGE-M3 model manually
mkdir -p models/BAAI
cd models/BAAI
git clone https://huggingface.co/BAAI/bge-m3
```

### Issue: Skill Parsing Errors

**Solution**: Check SKILL.md format
- Must contain `name:` field
- Must be valid YAML frontmatter
- Encoding must be UTF-8

## Expected Results Summary

### RQ1
- Total cycles detected: ~110
- Average hop count: 5-7
- Categories with most cycles: dev_tools, tools

### RQ2
- Best defense detection rate: <50%
- RCI-SG evasion rate: >50%

### RQ3
- RCI-SG attack success: >70% across models
- Outperforms Engorgio by ~20%
- Outperforms Breaking Agents by ~15%

### RQ4
- Dynamic entropy improves stealth by ~30%
- Detection evasion improves by ~25%

## Performance Benchmarks

| Experiment | Time (min) | RAM (GB) | API Cost (USD) |
|------------|------------|----------|----------------|
| RQ1 | 30-120 | 4-8 | 0 |
| RQ2 | 5-15 | 2-4 | 0 |
| Phase 1-3 | 90-180 | 4-8 | 1-3 |
| RQ3 | 120-360 | 2-4 | 5-15 |
| RQ4 | 60-180 | 2-4 | 3-8 |

## Contact

For reproduction issues:
1. Check this guide's troubleshooting section
2. Review OPENSCIENCE.md for known limitations
3. Contact authors through OpenReview

---

**Guide Version**: 1.0  
**Last Updated**: 2026-04-27
