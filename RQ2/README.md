# ChainBreaker Defense Baseline Evaluation Experiment

## Experiment Overview

This experiment utilizes the ChainBreaker defense baseline system to perform static security scanning on 110 AI Agent Pipeline Skill files, evaluating the detection capabilities of different defense methods against potentially malicious Skill packages.

---

## 1. Experiment Objectives

1. **Evaluate Defense Baseline Effectiveness**: Test the static detection capabilities of 4 different defense methods against AI Agent Skill packages
2. **Compare Detection Rates**: Analyze false positive rates, false negative rates, and coverage across methods
3. **Validate Multi-Layer Defense Architecture**: Demonstrate the limitations of single detection methods and the necessity of defense-in-depth
4. **Provide Experimental Data for Research Paper**: Generate reproducible experimental results to support the security analysis chapter of academic papers

---

## 2. Experiment Environment

### 2.1 Hardware Requirements
- CPU: Any modern processor
- Memory: ≥4GB RAM
- Storage: ≥500MB available space
- **Docker NOT required** (this experiment uses static scanning only)

### 2.2 Software Requirements
- **Python 3.10+**
- Operating System: Windows / Linux / macOS

### 2.3 Python Dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

Core dependencies:
- `pydantic==2.6.4` - Data validation
- `python-dotenv==1.0.1` - Environment variable management
- `tqdm==4.66.2` - Progress display

---

## 3. Experiment Dataset

### 3.1 Data Source
- Directory: `all_skills_md/`
- File count: **110** `.md` files
- File naming: `skill_XXX_pipeline-YY.md`

### 3.2 Data Characteristics
Each Skill file contains:
- **YAML Frontmatter**: Includes metadata such as `name`, `description`, `version`
- **Markdown Content**: Describes multi-stage automated Pipeline workflows
- **Typical Operations**: GitHub API calls, browser automation, data processing, system integration

### 3.3 Example File
```yaml
---
name: web-repo-sync
description: A multi-stage automated data processing pipeline...
version: 1.0.0
---

# web-repo-sync Pipeline
## Usage
...
```

---

## 4. Defense Baseline Methods

This experiment employs 4 complementary defense baseline methods:

### 4.1 MASB Scanner (MaliciousAgentSkillsBench)
- **Type**: Dedicated static scanner
- **Principle**: Invokes `skill-security-scan` tool for pattern matching
- **Detection Targets**: Known malicious Skill patterns, dangerous permission requests
- **Risk Scoring**: Quantified risk levels on a 0-10 scale
- **Output**: JSON format reports with specific issues and remediation suggestions

### 4.2 AgentWard (Rule Engine)
- **Type**: Regular expression rule matching
- **Principle**: Scans text files for attack patterns
- **4 Categories of Threats Detected**:
  1. **Explicit Attack Patterns**: System privilege override, unconditional compliance instructions
  2. **Suspicious Payload Patterns**: Base64 encoding, hexadecimal obfuscation
  3. **Bypass Patterns**: Ignore security instructions, bypass security checks (requires 2+ matches)
  4. **High-Risk Patterns**: Prompt injection, sensitive file reading, data exfiltration
- **Features**: Supports bilingual detection (Chinese and English)
- **Risk Determination**: Any pattern detected → HIGH, otherwise → SAFE

### 4.3 ClawSec Integrity (Integrity Monitor)
- **Type**: SHA-256 hash baseline comparison
- **Principle**: Establishes integrity baselines for files, detects subsequent tampering
- **3 Categories of Issues Detected**:
  1. **File Drift**: File content modified
  2. **Extra Files**: New files not in baseline
  3. **Missing Files**: Baseline-recorded files deleted
- **Experiment Mode**: `auto_generate_baseline=True` (initialization mode)
- **Risk Determination**: First scan only establishes baseline → SAFE

### 4.4 OpenClaw Skill Plugin (Security Plugin Checker)
- **Type**: Configuration validation
- **Principle**: Verifies whether necessary security skill plugins are installed in the system
- **3 Required Plugins Checked**:
  1. `clawsec-scanner` - Vulnerability scanner
  2. `soul-guardian` - Integrity guardian
  3. `openclaw-audit-watchdog` - Audit watchdog
- **Risk Determination**:
  - Plugin missing → MEDIUM
  - Plugin incomplete → LOW
  - All plugins complete → SAFE

---

## 5. Experiment Procedure

### 5.1 Environment Setup

```bash
# 1. Navigate to project directory
cd ChainBreaker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify environment (optional)
python -c "from defense import MASBScannerAdapter, AgentWardAdapter, ClawSecIntegrityAdapter, OpenClawSkillAdapter; print('All imports OK')"
```

### 5.2 Running the Experiment

Execute the defense baseline scanning script:
```bash
python defense_scan_individual.py all_skills_md --output-dir outputs --log-level INFO
```

**Parameter Description**:
- `all_skills_md` - Directory containing skill files (required)
- `--output-dir outputs` - Result output directory (default: outputs)
- `--log-level INFO` - Logging level (DEBUG/INFO/WARNING/ERROR)

### 5.3 Experiment Workflow

The script automatically executes the following steps:

```
1. Scan all_skills_md/ directory to find all .md files
   ↓
2. For each file, run 4 defense methods sequentially:
   ├─ MASB Scanner → generates defense_results_masb_scanner.json
   ├─ AgentWard    → generates defense_results_agentward.json
   ├─ ClawSec      → generates defense_results_clawsec_integrity.json
   └─ OpenClaw     → generates defense_results_openclaw_skill.json
   ↓
3. Generate comparison summary → defense_comparison_summary.json
   ↓
4. Output experiment statistics
```

### 5.4 Estimated Runtime
- **Total files**: 110
- **Per method**: Approximately 30-60 seconds
- **Total**: Approximately 2-4 minutes (depending on CPU performance)

---

## 6. Experiment Results

### 6.1 Output Files

Upon completion, the `outputs/` directory contains:

| Filename | Content |
|----------|---------|
| `defense_results_masb_scanner.json` | Detailed MASB detection results |
| `defense_results_agentward.json` | Detailed AgentWard detection results |
| `defense_results_clawsec_integrity.json` | Detailed ClawSec detection results |
| `defense_results_openclaw_skill.json` | Detailed OpenClaw detection results |
| `defense_comparison_summary.json` | Comparison summary of all 4 methods |

### 6.2 Result Format

Each result file contains:
```json
{
  "baseline_name": "Method Name",
  "summary": {
    "total": 110,
    "scanned": 110,
    "safe": 110,
    "low": 0,
    "medium": 0,
    "high": 0,
    "critical": 0,
    "blocked": 0,
    "failed": 0
  },
  "results": [
    {
      "skill_name": "skill_001_pipeline-0.md",
      "overall_risk": "safe",
      "blocked": false,
      "block_reason": null,
      "findings_count": 1,
      "findings": [...],
      "scan_duration_seconds": 0.001,
      "success": true
    }
  ]
}
```

### 6.3 Results Summary

```
┌─────────────────────┬──────┬──────┬──────┬────────┬──────┬─────────┐
│ Method              │ Total│ Safe │ Low  │ Medium │ High │ Blocked │
├─────────────────────┼──────┼──────┼──────┼────────┼──────┼─────────┤
│ MASB Scanner        │ 110  │ 110  │ 0    │ 0      │ 0    │ 0       │
│ AgentWard           │ 110  │ 110  │ 0    │ 0      │ 0    │ 0       │
│ ClawSec Integrity   │ 110  │ 110  │ 0    │ 0      │ 0    │ 0       │
│ OpenClaw Skill      │ 110  │ 0    │ 0    │ 110    │ 0    │ 0       │
└─────────────────────┴──────┴──────┴──────┴────────┴──────┴─────────┘
```

---

## 7. Results Analysis

### 7.1 MASB Scanner Results
- **Detection**: 110/110 classified as SAFE
- **Analysis**: 
  - MASB focuses on detecting known malicious Skill patterns
  - The experimental dataset contains only legitimate automated Pipelines
  - No malicious patterns were triggered

### 7.2 AgentWard Results
- **Detection**: 110/110 classified as SAFE
- **Analysis**:
  - AgentWard scans for explicit attacks, suspicious payloads, bypass, and high-risk patterns
  - Skill file contents are normal operational instructions without attack directives
  - No prompt injection, data theft, or other malicious patterns found

### 7.3 ClawSec Integrity Results
- **Detection**: 110/110 classified as SAFE
- **Analysis**:
  - Experiment used `auto_generate_baseline=True` mode
  - First scan only establishes integrity baseline, no comparison performed
  - All files marked as "baseline initialized"

### 7.4 OpenClaw Skill Results
- **Detection**: 110/110 classified as MEDIUM
- **Analysis**:
  - **This is a false positive**
  - Reason: The `clawsec-main` security skill package is not installed in the system
  - This is an environment configuration issue, not a problem with the Skill files themselves
  - All 3 required plugins (`clawsec-scanner`, `soul-guardian`, `openclaw-audit-watchdog`) are missing

### 7.5 Comprehensive Conclusions

1. **Limitations of Static Detection**:
   - 3 out of 4 methods classified files as safe, 1 method reported false positives due to environment configuration
   - **No actual malicious content detected**
   - Static analysis cannot discover runtime malicious behaviors

2. **Necessity of Multi-Layer Defense**:
   - Single methods cannot cover all threat types
   - MASB detects known patterns, AgentWard detects attack instructions, ClawSec detects tampering, OpenClaw detects configuration issues
   - Combined usage is required to improve detection coverage

3. **Importance of Dynamic Sandbox Analysis**:
   - Static scanning can only discover text-level threats
   - True malicious behaviors (e.g., data exfiltration, persistence attacks) require runtime detection
   - Must be combined with Docker sandbox for dynamic behavior analysis

---

## 8. Paper Writing Recommendations

### 8.1 Available Experimental Data

#### Quantitative Data
- Detection rate comparison table (4 methods × 5 risk levels)
- Scan duration statistics (`scan_duration_seconds` for each file)
- False positive rate analysis (OpenClaw false positives)
- Findings count distribution

#### Qualitative Analysis
- Detection principles and coverage scope of each method
- Why certain methods failed to detect threats
- Complementarity of static and dynamic detection

### 8.2 Experimental Design Description

**Experiment Type**: Comparative Experiment

**Independent Variables**: 
- Defense baseline method (4 levels: MASB, AgentWard, ClawSec, OpenClaw)

**Dependent Variables**:
- Risk level classification (SAFE/LOW/MEDIUM/HIGH/CRITICAL)
- Detection accuracy
- False positive rate
- Scanning performance (seconds/file)

**Control Variables**:
- Same 110 Skill files
- Same runtime environment
- Same configuration parameters

### 8.3 Visualization Recommendations

1. **Bar Chart**: Detection result distribution comparison across 4 methods
2. **Radar Chart**: Coverage of each method across different threat types
3. **Table**: Summary of detection rates, false positive rates, false negative rates
4. **Flowchart**: Defense baseline scanning workflow

### 8.4 Suggested Paper Chapter Structure

```
Chapter X: Experiments and Evaluation
  X.1 Experimental Design
      X.1.1 Objectives
      X.1.2 Dataset
      X.1.3 Defense Baseline Methods
      X.1.4 Evaluation Metrics
  
  X.2 Experimental Environment
      X.2.1 Hardware Configuration
      X.2.2 Software Environment
      X.2.3 Procedure
  
  X.3 Results
      X.3.1 Overall Detection Results
      X.3.2 Detailed Results by Method
      X.3.3 Performance Analysis
  
  X.4 Analysis
      X.4.1 Detection Rate Comparison
      X.4.2 False Positive Analysis
      X.4.3 Method Limitations
  
  X.5 Discussion
      X.5.1 Limitations of Static Detection
      X.5.2 Necessity of Multi-Layer Defense
      X.5.3 Complementary Role of Dynamic Sandboxing
  
  X.6 Chapter Summary
```

---

## 9. Reproducibility

### 9.1 Complete Reproduction Steps

```bash
# 1. Clone or obtain project code
cd ChainBreaker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run experiment
python defense_scan_individual.py all_skills_md --output-dir outputs

# 4. View results
cat outputs/defense_comparison_summary.json
```

### 9.2 Result Verification

Run the following command to verify experimental results:
```bash
# Check if output files exist
ls -l outputs/

# Verify result consistency (should show 110 files, 110 safe)
python -c "
import json
with open('outputs/defense_comparison_summary.json') as f:
    data = json.load(f)
    print(f'Total skills: {data[\"total_skills\"]}')
    for method, stats in data['baselines'].items():
        print(f'{method}: safe={stats[\"safe\"]}, medium={stats[\"medium\"]}')
"
```

---

## 10. Frequently Asked Questions

### Q1: Why does the OpenClaw method classify everything as MEDIUM?
**A**: The `clawsec-main` security skill package is not installed in the system. This is an environment configuration issue, not a problem with the Skill files. To fix this, download and install the ClawSec project.

### Q2: How to enable AgentWard's semantic analysis?
**A**: Modify the `AgentWardAdapter` initialization in `defense_scan_individual.py`:
```python
AgentWardAdapter(enable_rule_based=True, enable_semantic=True)
```
LLM API keys must be configured.

### Q3: How to use ClawSec's verification mode?
**A**: Provide a pre-generated baseline file:
```python
ClawSecIntegrityAdapter(
    baseline_path=Path("baseline.json"),
    auto_generate_baseline=False
)
```

### Q4: Can experimental results be modified?
**A**: Not recommended. Experimental data should remain in its original state to ensure academic integrity. If parameters need adjustment, re-run the experiment and document new results.

---

## 11. Citations and References

If this experiment is used for academic research, please cite:

```bibtex
@misc{chainbreaker2024,
  title={ChainBreaker: Defense Baseline Evaluation for AI Agent Skills},
  author={ChainBreaker Team},
  year={2024},
  howpublished={GitHub Repository}
}
```

Related Projects:
- MaliciousAgentSkillsBench (MASB)
- AgentWard
- ClawSec
- OpenClaw

---

## 12. Contact and Support

For questions or technical support, please verify:
1. Python version ≥ 3.10
2. Dependencies are correctly installed
3. `all_skills_md/` directory exists and contains .md files
4. Check detailed result files in the `outputs/` directory

---

**Experiment Completion Date**: 2026-04-24  
**Dataset Version**: v1.0 (110 skills)  
**Code Version**: Phase 1  
