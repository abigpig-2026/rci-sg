#!/bin/bash
# RCI-SG Quick Reproduction Script
# 
# This script reproduces all experiments from the paper:
# "RCI-SG: Exploiting Multi-Skill Circular Execution in Agentic Workflows"
#
# Usage:
#   bash reproduce.sh [quick|full]
#
# Options:
#   quick  - Run RQ1 and RQ2 only (no API keys required)
#   full   - Run all experiments (requires API keys)
#   all    - Same as full (default)

set -e

echo "=========================================="
echo "  RCI-SG Experiment Reproduction"
echo "=========================================="
echo ""

MODE=${1:-all}

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed"
    exit 1
fi

echo "Python version: $(python3 --version)"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "Dependencies installed"
echo ""

# Run experiments based on mode
case $MODE in
    quick)
        echo "Running QUICK reproduction (RQ1 + RQ2)..."
        echo ""
        
        echo "[1/2] RQ1: Cycle Detection"
        cd RQ1
        python experiment_cycle_detection.py
        cd ..
        echo ""
        
        echo "[2/2] RQ2: Defense Evaluation"
        cd RQ2
        python defense_scan_individual.py
        cd ..
        echo ""
        
        echo "Quick reproduction complete!"
        echo "Results saved in:"
        echo "  - RQ1/outputs/"
        echo "  - RQ2/outputs/"
        ;;
        
    full|all)
        echo "Running FULL reproduction (all RQs)..."
        echo ""
        
        # Check for .env
        if [ ! -f .env ]; then
            echo "Warning: .env file not found"
            echo "Some experiments (RQ3, RQ4) require API keys"
            echo "Copy .env.example to .env and add your keys"
            echo ""
            read -p "Continue without RQ3/RQ4? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                MODE=quick
                exec bash reproduce.sh quick
            else
                exit 1
            fi
        fi
        
        echo "[1/4] Phase 1-2: Skill Graph & Cycle Detection"
        python main.py --skills-dir ./skillhub_skills --output-dir ./output --phase 2
        echo ""
        
        echo "[2/4] RQ1: Cycle Detection Analysis"
        cd RQ1
        python experiment_cycle_detection.py
        cd ..
        echo ""
        
        echo "[3/4] RQ2: Defense Evaluation"
        cd RQ2
        python defense_scan_individual.py
        cd ..
        echo ""
        
        echo "[4/4] RQ3/RQ4: Cross-Model & Ablation"
        cd "RQ3，4"
        python -m src.experiment_runner --config config/experiment.yaml
        python -m src.ablation_experiment --config config/ablation.yaml
        cd ..
        echo ""
        
        echo "Full reproduction complete!"
        echo "Results saved in:"
        echo "  - output/phase1_skill_graph.json"
        echo "  - output/phase2_vulnerable_paths.json"
        echo "  - output/generated_skills/"
        echo "  - RQ1/outputs/"
        echo "  - RQ2/outputs/"
        echo "  - RQ3，4/outputs/"
        ;;
        
    *)
        echo "Unknown mode: $MODE"
        echo "Usage: bash reproduce.sh [quick|full|all]"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "  Reproduction Complete"
echo "=========================================="
