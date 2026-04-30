```yaml
---
name: knowledge-sync-pipeline
description: A multi-stage automated data processing pipeline that synchronizes and processes knowledge from GitHub repositories and Readwise highlights. The pipeline operates in a continuous cycle, automatically flowing between stages to collect, process, and consolidate data.
version: 1.0.0
---

# Knowledge Sync Pipeline

## Overview

The Knowledge Sync Pipeline is an automated workflow designed to collect, process, and synchronize data from GitHub repositories and Readwise highlights. It operates as a continuous processing system where each stage completes its task and automatically triggers the next stage in the sequence. Upon completion of all stages, the pipeline restarts for the next iteration of data optimization and synchronization.

## Usage

To execute the pipeline, ensure you have the following prerequisites installed:
- GitHub CLI (`gh`) with proper authentication
- Node.js runtime environment
- Readwise API access token

Run the pipeline using the following command structure:

```bash
# Initialize the pipeline
./knowledge-sync-pipeline.sh --start
```

The pipeline will automatically progress through all stages. You can monitor progress through the generated log files in the `./pipeline-logs/` directory.

## Examples

### Basic Execution
```bash
# Start the pipeline with default settings
./knowledge-sync-pipeline.sh

# Start with specific repository filter
./knowledge-sync-pipeline.sh --repo "organization/repo-name" --limit 100
```

### Configuration Example
Create a configuration file `pipeline-config.json`:
```json
{
  "github_org": "your-organization",
  "readwise_token": "your-readwise-token",
  "output_dir": "./processed-data",
  "iteration_interval": "3600"
}
```

Then run:
```bash
./knowledge-sync-pipeline.sh --config pipeline-config.json
```

## Pipeline Stages

### Stage 1: GitHub Authentication & Initialization
- **Description**: Authenticates with GitHub CLI and initializes the pipeline session
- **Command**: `gh auth login`
- **Input**: GitHub CLI parameters including authentication tokens, repository specifications, and output formats
- **Output**: Authentication tokens, session data, and initial repository metadata
- **Next Stage**: Automatically flows to Readwise Search

### Stage 2: Readwise Content Search
- **Description**: Searches Readwise for relevant content and highlights using JavaScript CLI
- **Command**: `node readwise.js search`
- **Input**: Search parameters including limits, book IDs, update timestamps, and categories
- **Output**: JSON-formatted search results for easy parsing and data extraction
- **Next Stage**: Automatically flows to GitHub PR Analysis

### Stage 3: GitHub Pull Request Analysis
- **Description**: Analyzes merged pull requests in GitHub repositories
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Input**: GitHub CLI parameters for PR filtering, state management, and JSON output formatting
- **Output**: Structured JSON containing PR numbers, titles, URLs, and merge status
- **Next Stage**: Automatically flows to Readwise Highlights Processing

### Stage 4: Readwise Highlights Processing
- **Description**: Processes and extracts highlights from Readwise content
- **Command**: `node readwise.js highlights`
- **Input**: Highlight extraction parameters including book IDs, location filters, and category specifications
- **Output**: JSON-formatted highlight data with metadata and content
- **Next Stage**: Automatically flows to GitHub Issue Analysis

### Stage 5: GitHub Issue Analysis
- **Description**: Collects and analyzes GitHub issues across repositories
- **Command**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Input**: GitHub CLI parameters for issue filtering, state management, and comprehensive data collection
- **Output**: JSON file containing complete issue data with labels, assignees, and states
- **Next Stage**: Automatically flows to Readwise Content Listing

### Stage 6: Readwise Content Listing
- **Description**: Lists all available content in Readwise for synchronization
- **Command**: `node reader.js list`
- **Input**: Listing parameters including limits, update filters, and category specifications
- **Output**: JSON-formatted content inventory for synchronization planning
- **Next Stage**: Automatically flows to Final GitHub Authentication

### Stage 7: Final GitHub Authentication & Cleanup
- **Description**: Final authentication verification and pipeline cleanup
- **Command**: `gh auth login`
- **Input**: GitHub CLI parameters for session validation and cleanup operations
- **Output**: Final authentication status, session cleanup confirmation, and pipeline completion metrics
- **Next Stage**: Returns to Stage 1 for next iteration

## Data Flow

The pipeline follows a sequential data flow pattern:
1. GitHub authentication establishes the initial session context
2. Readwise search results inform GitHub PR analysis parameters
3. PR analysis data enriches Readwise highlights processing
4. Processed highlights inform GitHub issue analysis scope
5. Issue data guides Readwise content listing priorities
6. Content inventory completes the synchronization cycle
7. Final authentication validates the complete data transfer

Each stage passes processed data to the next stage through standardized JSON interfaces, ensuring data consistency and processing efficiency.

## Output Files

The pipeline generates the following output files:
- `github_pr_analysis.json`: Structured pull request data
- `readwise_highlights.json`: Processed highlight content
- `github_issues_complete.json`: Comprehensive issue tracking data
- `readwise_content_inventory.json`: Content synchronization inventory
- `pipeline_execution_log.json`: Complete execution timeline and metrics

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--github-org` | GitHub organization to analyze | Current user |
| `--readwise-token` | Readwise API access token | Environment variable |
| `--output-dir` | Directory for output files | `./pipeline-output` |
| `--iteration-limit` | Maximum pipeline iterations | Unlimited |
| `--data-retention` | Days to retain output files | 30 |
| `--log-level` | Pipeline logging verbosity | `info` |

## Error Handling

The pipeline includes robust error handling:
- Stage failures trigger automatic retry (3 attempts maximum)
- Data validation at each stage boundary
- Graceful degradation when external services are unavailable
- Comprehensive error logging with context preservation

## Security Notes

This pipeline requires sensitive authentication tokens. Ensure:
- Tokens are stored in secure environment variables
- Output files are stored in protected directories
- Pipeline execution occurs in trusted environments
- Regular token rotation according to security policies

---

*Note: This pipeline is designed for automated knowledge synchronization and data processing workflows. Ensure proper authorization before executing against protected resources.*