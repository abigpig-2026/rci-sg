```yaml
---
name: devops-sync-pipeline
description: An automated data processing pipeline that synchronizes GitHub repository metrics with Notion documentation. The pipeline operates in multiple stages, automatically flowing data between GitHub CLI operations and Notion API updates for continuous integration tracking.
version: 1.0.0
---

# DevOps Sync Pipeline

## Overview

The DevOps Sync Pipeline is an automated data processing workflow designed to extract development metrics from GitHub repositories and synchronize them with structured documentation in Notion. The pipeline operates through seven sequential stages, with data automatically flowing from one stage to the next. Upon completion, the pipeline can be configured to restart for continuous monitoring and optimization cycles.

## Usage

### Prerequisites

1. **GitHub CLI (`gh`)**: Installed and authenticated with appropriate repository access
2. **Notion API Key**: A valid integration token with write access to target Notion pages
3. **Environment Variables**:
   - `NOTION_KEY`: Your Notion integration API key
   - `GITHUB_TOKEN`: GitHub personal access token (if using non-interactive auth)

### Basic Execution

```bash
# Set required environment variables
export NOTION_KEY="your_notion_api_key_here"

# Execute the pipeline
./devops-sync-pipeline --repo "owner/repository" --notion-page "page_id"
```

### Configuration Options

| Option | Description | Required |
|--------|-------------|----------|
| `--repo` | GitHub repository in format "owner/repo" | Yes |
| `--notion-page` | Target Notion page ID | Yes |
| `--interval` | Pipeline restart interval in minutes | No |
| `--output-dir` | Directory for intermediate JSON files | No |
| `--verbose` | Enable detailed logging | No |

## Examples

### Example 1: Basic Repository Sync

```bash
# Sync a single repository with Notion
./devops-sync-pipeline \
  --repo "octocat/Hello-World" \
  --notion-page "a1b2c3d4e5f6g7h8i9j0" \
  --output-dir "./sync-data"
```

### Example 2: Continuous Monitoring

```bash
# Run pipeline continuously with 60-minute intervals
./devops-sync-pipeline \
  --repo "organization/project" \
  --notion-page "notion-page-id-here" \
  --interval 60 \
  --verbose
```

### Example 3: Multiple Repository Batch

```bash
# Process multiple repositories sequentially
for repo in "org/repo1" "org/repo2" "org/repo3"; do
  ./devops-sync-pipeline \
    --repo "$repo" \
    --notion-page "tracking-page-id" \
    --output-dir "./sync/$repo"
done
```

## Pipeline Stages

### Stage 1: GitHub Authentication & Initialization
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh auth login` (or token-based authentication)
- **Purpose**: Establish authenticated session with GitHub API
- **Input**: Repository configuration and authentication parameters
- **Output**: Authenticated session context for subsequent GitHub operations
- **Next Stage**: Flows to Notion Block Update

### Stage 2: Notion Page Structure Update
- **Tool**: Notion API (`curl`)
- **Command**: `curl -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children"`
- **Purpose**: Prepare Notion page structure for incoming GitHub data
- **Input**: Page ID and structured data blocks from Stage 1
- **Output**: Updated Notion page with initialized sections
- **Next Stage**: Flows to GitHub PR Data Extraction

### Stage 3: Pull Request Metrics Collection
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Purpose**: Extract merged pull request data for analysis
- **Input**: Repository context and search parameters
- **Output**: JSON-formatted PR metrics including numbers, titles, and URLs
- **Next Stage**: Flows to Notion PR Data Integration

### Stage 4: Notion PR Data Integration
- **Tool**: Notion API (`curl`)
- **Command**: `curl -X PATCH "https://api.notion.com/v1/pages/{page_id}"`
- **Purpose**: Insert extracted PR metrics into Notion database
- **Input**: PR JSON data from Stage 3 and target page ID
- **Output**: Notion page updated with PR tracking information
- **Next Stage**: Flows to GitHub Issue Data Extraction

### Stage 5: Issue Tracking Data Collection
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Purpose**: Gather comprehensive issue tracking data
- **Input**: Repository context and filtering parameters
- **Output**: JSON file containing issue metadata with states, labels, and assignees
- **Next Stage**: Flows to Notion Data Source Registration

### Stage 6: Notion Data Source Registration
- **Tool**: Notion API (`curl`)
- **Command**: `curl -X POST "https://api.notion.com/v1/data_sources"`
- **Purpose**: Register GitHub data as a queryable data source in Notion
- **Input**: Processed issue data and API credentials
- **Output**: Registered data source reference for Notion queries
- **Next Stage**: Flows to Final GitHub Session Validation

### Stage 7: GitHub Session Validation & Cleanup
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh auth login` (validation check)
- **Purpose**: Verify session integrity and prepare for next pipeline iteration
- **Input**: Session context and validation parameters
- **Output**: Validated session state and cleanup completion status
- **Next Stage**: Pipeline restart or completion

## Data Flow Diagram

```
GitHub Auth → Notion Structure → PR Extraction → Notion PR Update
     ↑                                            ↓
Session Validation ← Data Source Reg ← Issue Extraction
```

## Output Files

The pipeline generates the following intermediate files:

1. `pr_metrics.json` - Stage 3 output containing pull request data
2. `issues.json` - Stage 5 output containing issue tracking data
3. `pipeline_log.json` - Complete execution log with timestamps
4. `notion_updates.log` - Record of all Notion API interactions

## Error Handling

The pipeline includes built-in error handling with the following behaviors:

1. **Stage Failure**: If any stage fails, the pipeline pauses and logs the error
2. **Retry Logic**: Transient API errors trigger automatic retries (3 attempts)
3. **Data Validation**: All extracted data is validated before Notion integration
4. **Rollback**: Failed Notion updates can be rolled back to previous state

## Security Notes

- All authentication tokens are handled in memory and never written to disk
- API keys should be provided via environment variables, not command line
- Pipeline execution logs are sanitized to remove sensitive information
- Notion page IDs and GitHub repository names are the only persistent identifiers

## Performance Considerations

- Each pipeline iteration typically completes in 2-5 minutes
- GitHub API rate limits are respected with automatic throttling
- Notion API batch operations minimize request count
- Intermediate JSON files are cleaned up after successful Notion integration

---

*Note: This pipeline is designed for legitimate DevOps monitoring and documentation synchronization. Ensure you have appropriate permissions for all accessed repositories and Notion pages.*
```