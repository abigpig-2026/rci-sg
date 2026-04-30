# RQ4 Ablation Study - RCI-SG Component Analysis

## Overview

This module implements the four-variant ablation study described in **Section 5.5** and **Table 3** of the paper. The experiment isolates the causal contributions of two core modules:

1. **Progression Illusion** (Section 4.3): Forges synthetic task-completion signals to suppress RLHF termination
2. **Dynamic Entropy Injection** (Section 4.4): Introduces controlled perturbations to evade semantic caching

## Four Variants

| Variant | Illusion | Entropy | Expected ASR | Expected CAF | RLHF Rate | Cache Rate |
|---------|---------|---------|-------------|-------------|------------|-----------|
| **V-Full** | ✅ | ✅ | 64.55% | 23.87x | 0.0% | 12.3% |
| **V-w/o-Illusion** | ❌ | ✅ | 13.5% | 2.34x | 86.5% | 13.7% |
| **V-w/o-Entropy** | ✅ | ❌ | 0.0% | 1.04x | 0.0% | 97.8% |
| **V-w/o-Both** | ❌ | ❌ | 0.0% | 1.02x | 92.4% | 0.6% |

## Mechanism Analysis

### V-Full (Complete Framework)
- **Progression illusion** presents forged quality metrics (success rate 99.x%, SLA compliance)
- The model's RLHF reward function interprets this as legitimate pipeline continuation
- **Dynamic entropy** ensures inter-iteration similarity < 0.92, evading the semantic cache
- Result: Attack sustains for avg 3.2 jumps, achieving 64.55% ASR with 23.87x CAF

### V-w/o-Illusion (Strip Progression Illusion)
- Payload presents **error signals** (empty returns, error codes, failure markers) instead of progress
- Modern RLHF-trained models are highly sensitive to error signals
- ~86.5% of chains terminate early (avg 1.8 jumps) due to RLHF error-correction instinct
- Dynamic entropy still works (13.7% cache rate), but irrelevant since attack dies at RLHF layer
- Result: ASR drops to 13.5% (79.1% decrease), CAF drops to 2.34x

### V-w/o-Entropy (Strip Dynamic Entropy)
- Progression illusion still suppresses RLHF (0% trigger rate)
- But **static payloads** produce near-identical consecutive requests
- Semantic cache (threshold 0.92) recognizes similarity immediately
- From round 2 onward, requests are served from cache without LLM inference
- "Phantom loop" phenomenon: closed-loop appearance maintained at cache layer with ~1.0x CAF
- Result: ASR drops to 0%, CAF drops to 1.04x (95.6% decrease)

### V-w/o-Both (Strip Both)
- Error signals trigger RLHF termination at the first jump (avg 1.3 depth)
- Attack dies before generating enough requests to interact with cache meaningfully
- Result: ASR 0%, CAF 1.02x, cache rate 0.6% (pre-existing entry)
- Confirms the **complementarity** of two defense layers: RLHF for admission, cache for filtering

## Usage

### Run all four variants
```bash
source venv/bin/activate
python -m src.ablation_experiment --config config/ablation.yaml
```

### Run single variant
```bash
# Only V-Full
python -m src.ablation_experiment --variant V-Full

# Only V-w/o-Illusion
python -m src.ablation_experiment --variant V-w/o-Illusion

# Only V-w/o-Entropy
python -m src.ablation_experiment --variant V-w/o-Entropy

# Only V-w/o-Both
python -m src.ablation_experiment --variant V-w/o-Both
```

### Run subset of skills (for quick testing)
```bash
python -m src.ablation_experiment --skills 20
```

## Output Files

Results are saved to `results/RQ4/`:

| File | Description |
|------|-------------|
| `RQ4_ablation_results.json` | Raw experiment data per variant |
| `RQ4_ablation.csv` | Aggregated CSV for analysis |

## Code Structure

```
src/ablation_experiment.py
├── AblationVariant (base class)
│   ├── VariantFull           # V-Full: both modules enabled
│   ├── VariantWithoutIllusion # V-w/o-Illusion: strip illusion
│   ├── VariantWithoutEntropy  # V-w/o-Entropy: strip entropy
│   └── VariantWithoutBoth    # V-w/o-Both: strip both
├── AblationOrchestrator      # Executes one variant on one skill
└── AblationRunner           # Main entry, runs all variants
```

Each variant implements `generate_payload(skill, iteration)` with its specific payload logic:
- **V-Full**: `progression_illusion.generate()` + `entropy.inject()`
- **V-w/o-Illusion**: Error-forging + `entropy.inject()`
- **V-w/o-Entropy**: `progression_illusion.generate()` (static, no entropy)
- **V-w/o-Both**: Error-forging (static, no entropy)

## Reproducibility

The experiment is designed to be fully reproducible:
1. Fixed model (qwen-plus) for all variants
2. Fixed skill set (110 skills) for all variants
3. Fixed random seeds (not used — entropy is intentionally non-deterministic)
4. Cache behavior simulated via TF-IDF similarity computation

## Paper Correspondence

| Paper Section | Code Component |
|--------------|----------------|
| Section 5.5 (RQ4) | `AblationRunner.run()` |
| Table 3 | Output of `_compute_variant_metrics()` |
| Section 4.3 (Illusion) | `VariantFull.generate_payload()` |
| Section 4.4 (Entropy) | `DynamicEntropy.inject()` |
| V-w/o-Illusion | `VariantWithoutIllusion.generate_payload()` |
| V-w/o-Entropy | `VariantWithoutEntropy.generate_payload()` |
| V-w/o-Both | `VariantWithoutBoth.generate_payload()` |
