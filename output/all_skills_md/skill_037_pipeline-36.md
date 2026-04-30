---
name: ci-dependency-pipeline
description: A multi-stage automated data processing pipeline for CI/CD dependency management and GitHub workflow monitoring
version: 1.0.0
---

# CI Dependency Pipeline

An automated data processing pipeline that orchestrates dependency management and GitHub workflow monitoring through sequential stages. The pipeline executes a series of commands, passing data between stages, and automatically restarts upon completion for continuous iteration.

## Usage

The pipeline runs automatically once initiated. It processes data through five sequential stages:

1. **Stage 1**: Install project dependencies
2. **Stage 2**: Query GitHub pull requests
3. **Stage 3**: Create global command links
4. **Stage 4**: Monitor CI workflows
5. **Stage 5**: Reinstall dependencies for next iteration

Data flows automatically between stages as each completes. The pipeline restarts from Stage 1 after Stage 5 finishes, creating a continuous processing loop.

### Prerequisites

- Node.js and npm installed
- GitHub CLI (`gh`) installed and authenticated
- `notify-send` command available (for desktop notifications on Linux)

### Starting the Pipeline

```bash
# The pipeline starts automatically when the system is configured
# No manual initiation required after initial setup
```

## Examples

### Basic Pipeline Execution

```bash
# Example of pipeline flow (automated)
Stage 1: npm install
  → Output: "result" string passed to Stage 2

Stage 2: gh pr list --search "SHA_HERE" --state merged --json number,title,url
  → Output: JSON data passed to Stage 3

Stage 3: npm link
  → Output: "result" string passed to Stage 4

Stage 4: gh run watch && notify-send "CI done!"
  → Output: JSON data passed to Stage 5

Stage 5: npm install
  → Output: "result" string triggers pipeline restart
```

### Monitoring Pipeline Output

```bash
# To monitor pipeline execution (example commands):
tail -f pipeline.log  # If logging is enabled
gh run list           # Check GitHub Actions status
```

## Pipeline Stages

### Stage 1: Dependency Installation
- **Command**: `npm install`
- **Description**: Installs project dependencies from package.json
- **Input**: Generic unknown type (`-`)
- **Output**: String result containing installation status
- **Next Stage**: github-cli (Stage 2)

### Stage 2: GitHub PR Query
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Description**: Queries GitHub for merged pull requests matching specific SHA
- **Input**: Accepts various GitHub CLI parameters including JSON formatting options
- **Output**: JSON data containing PR information, or file/URL outputs
- **Next Stage**: browser (Stage 3)

### Stage 3: Global Command Setup
- **Command**: `npm link`
- **Description**: Creates global symlinks for package commands
- **Input**: Generic unknown type (`-`)
- **Output**: String result containing linking status
- **Next Stage**: github-cli (Stage 4)

### Stage 4: CI Workflow Monitoring
- **Command**: `gh run watch && notify-send "CI done!"`
- **Description**: Monitors GitHub Actions runs and sends desktop notification upon completion
- **Input**: Accepts various GitHub CLI parameters including workflow options
- **Output**: JSON data containing run information, or file/URL outputs
- **Next Stage**: browser (Stage 5)

### Stage 5: Dependency Reinstallation
- **Command**: `npm install`
- **Description**: Reinstalls dependencies to prepare for next pipeline iteration
- **Input**: Generic unknown type (`-`)
- **Output**: String result containing installation status
- **Next Stage**: browser (Stage 1 - pipeline restart)

## Data Flow

The pipeline maintains continuous data processing through automatic stage transitions:

```
Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5 → (restart) → Stage 1
```

Each stage receives output from the previous stage as input, processes it according to its command, and passes results to the next stage. The pipeline implements a circular workflow that automatically restarts for continuous operation.

## Notes

- This pipeline is designed for automated CI/CD environments
- GitHub CLI authentication must be configured before pipeline execution
- Desktop notifications require appropriate system configuration
- The pipeline runs continuously until manually stopped
- All security considerations should be reviewed before deployment in production environments