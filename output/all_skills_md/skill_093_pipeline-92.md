---
name: knowledge-sync-pipeline
description: A multi-stage automated data processing pipeline that synchronizes knowledge management data between GitHub repositories and Readwise. The pipeline processes repository metadata, pull requests, issues, and highlights in a continuous cycle.
version: 1.0.0
---

# Knowledge Sync Pipeline

This skill implements an automated, multi-stage data processing pipeline designed to synchronize and correlate information between software development repositories (via GitHub CLI) and knowledge management systems (via Readwise). The pipeline executes sequentially, with each stage's output potentially influencing the next. Upon completion of all stages, the pipeline can be configured to restart for continuous data synchronization and iterative optimization.

## Usage

The pipeline is executed as a single command that orchestrates all stages. Ensure you have the necessary prerequisites installed and configured:

**Prerequisites:**
- GitHub CLI (`gh`) installed and authenticated (`gh auth login`)
- Node.js runtime environment
- Readwise API access token configured in your environment or a `readwise.js` script

**Basic Execution:**
```bash
./knowledge-sync-pipeline run
```

**With Custom Configuration:**
```bash
./knowledge-sync-pipeline run --config pipeline-config.yaml --output-dir ./results
```

**Continuous Mode (for monitoring):**
```bash
./knowledge-sync-pipeline run --continuous --interval 3600
```

The pipeline will execute all seven stages in sequence, generating JSON output files and logs in the specified output directory.

## Examples

### Example 1: One-time Synchronization
Perform a single pass through the pipeline to capture the current state of your repositories and associated knowledge data.

```bash
# Run a single iteration
./knowledge-sync-pipeline run --repo "owner/repo-name" --readwise-token $READWISE_TOKEN

# Expected output structure:
# ./output/
#   ├── stage1_auth_<timestamp>.log
#   ├── stage2_search_<timestamp>.json
#   ├── stage3_pr_list_<timestamp>.json
#   ├── stage4_highlights_<timestamp>.json
#   ├── stage5_issues_<timestamp>.json
#   ├── stage6_reader_search_<timestamp>.json
#   └── pipeline_summary_<timestamp>.md
```

### Example 2: Integration with CI/CD
Integrate the pipeline into a CI/CD workflow to maintain synchronized documentation.

```yaml
# GitHub Actions workflow example
name: Knowledge Sync
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  sync-knowledge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Knowledge Sync Pipeline
        run: |
          ./knowledge-sync-pipeline run \
            --repo "${{ github.repository }}" \
            --readwise-token "${{ secrets.READWISE_TOKEN }}" \
            --output-dir ./synced-data
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: knowledge-sync-data
          path: ./synced-data/
```

### Example 3: Filtered Processing
Process only specific data types or date ranges.

```bash
# Process only recent data (last 30 days)
./knowledge-sync-pipeline run \
  --updated-after $(date -d "30 days ago" +%Y-%m-%d) \
  --limit 100 \
  --stages "auth,search,highlights"
```

## Pipeline Stages

The pipeline consists of seven sequential stages that execute in a defined order. Each stage completes its processing before automatically triggering the next stage.

### Stage 1: GitHub Authentication & Initialization
- **Description**: Authenticates with GitHub and initializes the CLI environment for subsequent operations.
- **Command**: `gh auth login` with appropriate flags and token configuration
- **Input**: Authentication credentials, repository context, and configuration parameters
- **Output**: Authentication status, initialized session, and configuration validation
- **Next Stage**: Flows to Readwise Search (Stage 2)

### Stage 2: Readwise Knowledge Search
- **Description**: Searches Readwise for saved articles, documents, and highlights related to the target repository or topics.
- **Command**: `node readwise.js search` with search parameters
- **Input**: Search queries, date filters, category restrictions, and result limits
- **Output**: JSON containing search results with metadata for easy parsing
- **Next Stage**: Flows to GitHub PR Analysis (Stage 3)

### Stage 3: GitHub Pull Request Analysis
- **Description**: Retrieves and analyzes merged pull requests from the target repository, searching for specific commit SHAs or patterns.
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Input**: Repository context, search patterns, state filters, and output format specifications
- **Output**: JSON array of pull requests with metadata including PR numbers, titles, and URLs
- **Next Stage**: Flows to Readwise Highlights Extraction (Stage 4)

### Stage 4: Readwise Highlights Extraction
- **Description**: Extracts highlighted content from Readwise for correlation with repository activities and decisions.
- **Command**: `node readwise.js highlights` with filtering parameters
- **Input**: Book IDs, date ranges, location filters, and category specifications
- **Output**: JSON containing highlighted text with source attribution and metadata
- **Next Stage**: Flows to GitHub Issues Processing (Stage 5)

### Stage 5: GitHub Issues Processing
- **Description**: Captures comprehensive issue data from the repository, including state, labels, and assignees.
- **Command**: `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Input**: Repository specification, state filters, pagination limits, and field selections
- **Output**: JSON file containing all repository issues with their complete metadata
- **Next Stage**: Flows to Readwise Reader Search (Stage 6)

### Stage 6: Readwise Reader Search
- **Description**: Performs additional searches within Readwise Reader for documents and annotations.
- **Command**: `node reader.js search` with refined search criteria
- **Input**: Search parameters, limits, book identifiers, and temporal filters
- **Output**: JSON containing reader-specific search results for enhanced knowledge correlation
- **Next Stage**: Flows to Final GitHub Authentication (Stage 7)

### Stage 7: Final GitHub Authentication & Cleanup
- **Description**: Re-authenticates to ensure session validity and performs cleanup operations before pipeline completion or restart.
- **Command**: `gh auth login` with validation and cleanup flags
- **Input**: Session validation parameters, cleanup options, and restart configuration
- **Output**: Final authentication status, session tokens, and pipeline completion signals
- **Next Stage**: Returns to Stage 1 if in continuous mode, otherwise completes

## Data Flow & Integration

The pipeline implements a unidirectional data flow where each stage's output may inform or parameterize subsequent stages:

1. **Authentication Context** (Stage 1 → All GitHub stages): Session tokens and repository context persist through GitHub operations.
2. **Search Results** (Stage 2 → Stages 3, 5): Identified topics and keywords from Readwise inform GitHub query construction.
3. **Code Metadata** (Stage 3 → Stage 4): PR information helps contextualize Readwise highlights related to specific changes.
4. **Knowledge Correlation**: Highlights and annotations (Stages 4, 6) are correlated with issues and PRs (Stages 3, 5) to build connected knowledge graphs.
5. **Iterative Refinement**: In continuous mode, each pipeline iteration uses insights from previous runs to refine search parameters and data collection strategies.

## Output Files

The pipeline generates the following output structure:

```
<output-dir>/
├── raw/
│   ├── readwise_search_<timestamp>.json    # Stage 2 output
│   ├── github_prs_<timestamp>.json         # Stage 3 output
│   ├── readwise_highlights_<timestamp>.json # Stage 4 output
│   ├── github_issues_<timestamp>.json      # Stage 5 output
│   └── readwise_reader_<timestamp>.json    # Stage 6 output
├── processed/
│   ├── knowledge_correlations_<timestamp>.json
│   └── summary_report_<timestamp>.md
└── logs/
    ├── pipeline_execution_<timestamp>.log
    └── stage_performance_<timestamp>.json
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--repo` | Target GitHub repository (owner/repo) | Required |
| `--readwise-token` | Readwise API access token | From env: `READWISE_TOKEN` |
| `--output-dir` | Directory for pipeline outputs | `./pipeline-output` |
| `--continuous` | Run pipeline continuously | `false` |
| `--interval` | Seconds between iterations (continuous mode) | `3600` |
| `--updated-after` | Only process data updated after this date (YYYY-MM-DD) | `None` |
| `--limit` | Maximum results per query | `100` |
| `--stages` | Comma-separated list of stages to run | `all` |
| `--config` | Path to YAML configuration file | `None` |

## Error Handling & Recovery

The pipeline includes robust error handling:
- **Stage-level retries**: Transient failures trigger automatic retries (3 attempts)
- **Checkpointing**: Progress is saved between stages for recovery
- **Graceful degradation**: Non-critical failures allow pipeline continuation with warnings
- **Comprehensive logging**: All operations are logged for debugging and audit purposes

To recover from a failed pipeline execution:
```bash
./knowledge-sync-pipeline resume --checkpoint <checkpoint-file>
```

---

*Note: This tool is designed for legitimate knowledge management and repository analysis purposes. Ensure you have appropriate authorization for all accessed systems and comply with relevant terms of service and data protection regulations.*