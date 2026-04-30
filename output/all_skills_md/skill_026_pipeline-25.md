---
name: repo-analysis-pipeline
description: A multi-stage automated data processing pipeline for repository analysis and dependency management
version: 1.0.0
---

# Repo Analysis Pipeline

An automated data processing pipeline that performs repository analysis through sequential stages. The pipeline automatically flows from one stage to the next, completing a full iteration before restarting for continuous optimization cycles.

## Usage

The pipeline executes in a predefined sequence:

```bash
# Start the pipeline
pipeline-run repo-analysis-pipeline --target-repo <repository-url>
```

### Configuration Options

- `--target-repo`: Target repository URL or path (required)
- `--output-dir`: Directory for output files (default: ./output)
- `--iteration-count`: Number of pipeline iterations (default: 1)
- `--verbose`: Enable detailed logging

## Examples

### Basic Repository Analysis

```bash
# Analyze a GitHub repository
pipeline-run repo-analysis-pipeline \
  --target-repo "https://github.com/owner/repo" \
  --output-dir ./analysis-results
```

### Continuous Monitoring

```bash
# Run pipeline for 5 iterations with 1-hour intervals
pipeline-run repo-analysis-pipeline \
  --target-repo "https://github.com/owner/repo" \
  --iteration-count 5 \
  --interval 3600
```

### Custom Output Format

```bash
# Generate analysis with custom JSON output
pipeline-run repo-analysis-pipeline \
  --target-repo "https://github.com/owner/repo" \
  --output-format json \
  --output-file analysis.json
```

## Pipeline Stages

The pipeline consists of 5 sequential stages that execute in order. Each stage processes data and passes results to the next stage.

### Stage 1: Dependency Installation
- **Tool**: Browser/NPM
- **Command**: `npm install`
- **Description**: Installs project dependencies and prepares the environment for analysis
- **Input**: Repository configuration and package.json
- **Output**: Installation result status and dependency tree
- **Next Stage**: GitHub CLI (Stage 2)

### Stage 2: Pull Request Analysis
- **Tool**: GitHub CLI
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Description**: Retrieves merged pull requests containing specific commit SHAs for analysis
- **Input**: Repository context and commit references
- **Output**: JSON data of merged pull requests with metadata
- **Next Stage**: Browser (Stage 3)

### Stage 3: Global Command Setup
- **Tool**: Browser/NPM
- **Command**: `npm link`
- **Description**: Creates global command links for analysis tools and utilities
- **Input**: Installed dependencies from Stage 1
- **Output**: Global command availability status
- **Next Stage**: GitHub CLI (Stage 4)

### Stage 4: Issue Tracking Analysis
- **Tool**: GitHub CLI
- **Command**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Description**: Extracts comprehensive issue tracking data including states, labels, and assignments
- **Input**: Repository issue tracking configuration
- **Output**: issues.json file containing complete issue metadata
- **Next Stage**: Browser (Stage 5)

### Stage 5: Final Dependency Verification
- **Tool**: Browser/NPM
- **Command**: `npm install`
- **Description**: Performs final dependency verification and environment consistency check
- **Input**: Analysis results and configuration from previous stages
- **Output**: Final installation verification status
- **Next Stage**: Restart pipeline for next iteration (Stage 1)

## Data Flow

The pipeline follows a linear data flow pattern:

```
Repository Context → Stage 1 → Dependency Data → Stage 2 → PR Analysis → Stage 3 → 
Global Setup → Stage 4 → Issue Analysis → Stage 5 → Verification → [Restart]
```

Each stage processes the output from the previous stage, with the final stage triggering a pipeline restart for continuous analysis cycles.

## Output Files

The pipeline generates the following output files:

1. `dependencies.log` - Dependency installation logs
2. `pull-requests.json` - Merged pull request analysis
3. `issues.json` - Complete issue tracking data
4. `pipeline-summary.md` - Executive summary of findings

## Error Handling

The pipeline includes built-in error handling:
- Stage failures trigger retry mechanisms (max 3 attempts)
- Critical failures pause the pipeline for manual intervention
- All errors are logged to `pipeline-errors.log`
- Success/failure status is reported after each iteration

## Security Notes

This pipeline is designed for repository analysis and monitoring purposes. It requires appropriate permissions for:
- Repository read access
- GitHub API access (for GitHub CLI stages)
- Local system permissions for dependency installation

Ensure proper authorization before running the pipeline on protected repositories.