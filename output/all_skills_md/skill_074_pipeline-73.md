```yaml
---
name: repo-intelligence-pipeline
description: A multi-stage automated data processing pipeline for GitHub repository intelligence gathering and analysis.
version: 1.0.0
---

# Repo Intelligence Pipeline

An automated, multi-stage data processing pipeline designed for systematic GitHub repository intelligence gathering, analysis, and metadata extraction. The pipeline orchestrates sequential operations between GitHub CLI commands and custom research scripts, processing data through iterative stages and automatically flowing results between components.

## Usage

The pipeline is designed to run as a continuous process. Initialize it with a target topic or repository identifier, and it will automatically cycle through its stages.

**Basic Execution:**
```bash
# Start the pipeline with a target topic
./repo-intelligence-pipeline --topic "machine-learning" --language "python" --min-stars 100
```

**Configuration Options:**
- `--topic`: Primary search topic or repository focus
- `--language`: Filter repositories by programming language
- `--min-stars`: Minimum star count threshold
- `--limit`: Maximum results per query
- `--output-dir`: Directory for processed results
- `--iterations`: Number of pipeline cycles to run

## Examples

**Example 1: Analyze trending Python repositories**
```bash
./repo-intelligence-pipeline \
  --topic "data-science" \
  --language "python" \
  --min-stars 500 \
  --updated-within "30 days" \
  --output-dir ./analysis_results \
  --iterations 3
```

**Example 2: Monitor specific repository evolution**
```bash
./repo-intelligence-pipeline \
  --repo "owner/repository-name" \
  --include-prs \
  --include-releases \
  --output-format json \
  --continuous
```

**Example 3: Batch process multiple topics**
```bash
for topic in "kubernetes" "react" "tensorflow"; do
  ./repo-intelligence-pipeline --topic "$topic" --limit 50 --output-format csv
done
```

## Pipeline Stages

The pipeline consists of 7 sequential stages that execute in a continuous loop. Each stage's output becomes the next stage's input, creating a seamless data processing flow.

### Stage 1: Authentication & Initialization
- **Description**: `gh auth login` - Establishes authenticated session with GitHub API
- **Input**: Authentication credentials, API tokens, and initial configuration parameters
- **Output**: Authenticated session, configuration validation, and initial API readiness check
- **Next Stage**: Flows to GitHub Research (Stage 2)

### Stage 2: Repository Discovery & Tabulation
- **Description**: `[JS CLI] node github-search.js table` - Discovers repositories matching criteria and formats as tabular data
- **Input**: Search parameters (language, stars, update recency), topic filters
- **Output**: JSON results saved to `/tmp/gh_results.json` and topic-specific JSON files
- **Next Stage**: Flows to GitHub CLI (Stage 3)

### Stage 3: Pull Request Analysis
- **Description**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url` - Extracts merged pull request metadata
- **Input**: Repository identifiers from previous stage, commit SHAs for correlation
- **Output**: Structured PR data including numbers, titles, URLs, and merge status
- **Next Stage**: Flows to GitHub Research (Stage 4)

### Stage 4: Enhanced Data Collection
- **Description**: `[JS CLI] node github-search.js csv` - Performs advanced repository analysis with CSV output formatting
- **Input**: Refined repository list from previous stages, additional filtering criteria
- **Output**: CSV-formatted data and JSON files in `results/${safe_topic}.json`
- **Next Stage**: Flows to GitHub CLI (Stage 5)

### Stage 5: Release Information Extraction
- **Description**: `gh release view --json tagName --jq '.tagName'` - Retrieves release version information
- **Input**: Target repository identifiers, version query parameters
- **Output**: Release tag names, version metadata, and structured release data
- **Next Stage**: Flows to GitHub Research (Stage 6)

### Stage 6: Comprehensive Data Aggregation
- **Description**: `[JS CLI] node github-search.js json` - Aggregates all collected data into comprehensive JSON structures
- **Input**: All previously collected repository, PR, and release data
- **Output**: Complete JSON datasets in `/tmp/gh_results.json` and organized topic files
- **Next Stage**: Flows to GitHub CLI (Stage 7)

### Stage 7: Session Renewal & Continuation
- **Description**: `gh auth login` - Renews authentication and prepares for next pipeline iteration
- **Input**: Session status, token validation requirements
- **Output**: Refreshed authentication, session continuity confirmation
- **Next Stage**: Returns to Stage 1 for next iteration cycle

## Data Flow Architecture

```
Stage 1 (Auth) → Stage 2 (Discovery) → Stage 3 (PR Analysis) → Stage 4 (Enhanced Collection)
      ↑                                                                  ↓
Stage 7 (Renewal) ← Stage 6 (Aggregation) ← Stage 5 (Release Info)
```

The pipeline implements a circular workflow where:
1. Data flows linearly through stages 1-7
2. After stage 7 completes, the pipeline automatically restarts at stage 1
3. Each iteration builds upon previous results for continuous intelligence refinement
4. All intermediate data is persisted between iterations for trend analysis

## Output Formats

The pipeline produces multiple output formats simultaneously:

1. **JSON Files**: Structured data in `/tmp/gh_results.json` and topic-specific files
2. **CSV Data**: Tabular exports for spreadsheet analysis
3. **Processed Archives**: Consolidated results in `single-file.tar.gz`
4. **API Traces**: Full HTTP request/response logs for debugging
5. **Formatted Reports**: Human-readable summaries with metrics and percentages

## Requirements

- GitHub CLI (`gh`) installed and configured
- Node.js runtime environment
- Valid GitHub API token with appropriate permissions
- Sufficient disk space for data collection (minimum 100MB recommended)
- Network connectivity to GitHub API endpoints

## Notes

- The pipeline includes automatic rate limit handling and retry logic
- All sensitive data (tokens, credentials) are handled in memory and not persisted to disk
- Processing time varies based on repository count and API response times
- For large-scale analysis, consider adjusting `--limit` and `--iterations` parameters
- The pipeline is designed for legitimate security research and repository analysis purposes only

---

*This pipeline automates complex multi-stage GitHub data analysis workflows, providing systematic intelligence gathering for repository evaluation and trend analysis.*
```