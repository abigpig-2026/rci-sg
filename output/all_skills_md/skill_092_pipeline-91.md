```yaml
---
name: knowledge-sync-pipeline
description: A multi-stage automated pipeline for synchronizing development knowledge and repository insights. It processes GitHub repository data and Readwise highlights through sequential stages, enabling continuous data integration and analysis.
version: 1.0.0
---

# Knowledge Sync Pipeline

An automated data processing pipeline that orchestrates GitHub repository operations and Readwise knowledge extraction through seven sequential stages. The pipeline processes development data and reading highlights, facilitating continuous synchronization between code repositories and personal knowledge bases.

## Usage

To execute the complete pipeline:

```bash
# Start the pipeline (it will automatically progress through all stages)
./run-pipeline.sh --config pipeline-config.yaml
```

The pipeline runs in a continuous loop. After completing all seven stages, it automatically restarts for the next iteration. Each stage's output serves as input for the subsequent stage.

**Prerequisites:**
- GitHub CLI (`gh`) installed and authenticated
- Node.js environment with Readwise CLI (`readwise.js`)
- Valid API tokens for GitHub and Readwise services

**Configuration:**
Create a `pipeline-config.yaml` file with the following structure:

```yaml
github:
  token: ${GITHUB_TOKEN}
  repo: "owner/repository-name"
  
readwise:
  token: ${READWISE_TOKEN}
  limit: 100
  
pipeline:
  iterations: 5  # Number of complete pipeline cycles
  delay_between_stages: 30  # Seconds
```

## Examples

### Basic Pipeline Execution
```bash
# Run a single iteration of the pipeline
./run-pipeline.sh --single-iteration

# Run with verbose logging
./run-pipeline.sh --verbose --config my-config.yaml

# Specify output directory for pipeline artifacts
./run-pipeline.sh --output-dir ./pipeline-results --iterations 3
```

### Pipeline Stage Debugging
```bash
# Execute only specific stages
./run-pipeline.sh --stages 1,3,5

# Test stage connectivity without processing data
./run-pipeline.sh --dry-run

# View pipeline status and stage completion history
./run-pipeline.sh --status
```

### Integration with CI/CD
```yaml
# GitHub Actions example
name: Knowledge Sync Pipeline
on:
  schedule:
    - cron: '0 */6 * * *'  # Run every 6 hours
  workflow_dispatch:

jobs:
  sync-knowledge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup pipeline
        run: |
          npm install
          gh auth login --with-token <<< "${{ secrets.GITHUB_TOKEN }}"
          
      - name: Execute pipeline
        run: ./run-pipeline.sh --config ci-config.yaml
        env:
          READWISE_TOKEN: ${{ secrets.READWISE_TOKEN }}
          
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: pipeline-output
          path: ./output/
```

## Pipeline Stages

The pipeline consists of seven sequential stages that execute in order. Data flows automatically between stages, with each stage's output becoming the next stage's input.

### Stage 1: GitHub Authentication & Repository Initialization
**Tool:** GitHub CLI (`gh`)  
**Command:** `gh auth login` with repository context initialization  
**Purpose:** Establishes authenticated session with GitHub and prepares repository context for subsequent operations.  
**Input:** Authentication credentials and repository configuration parameters  
**Output:** Authenticated session token and repository metadata in JSON format  
**Next Stage:** → Stage 2 (Readwise Search)

### Stage 2: Readwise Knowledge Search
**Tool:** Readwise CLI (`readwise.js`)  
**Command:** `node readwise.js search`  
**Purpose:** Searches Readwise knowledge base for relevant highlights and annotations based on repository context.  
**Input:** Search parameters including limits, categories, and temporal filters  
**Output:** Structured JSON containing search results for easy parsing  
**Next Stage:** → Stage 3 (GitHub PR Analysis)

### Stage 3: GitHub Pull Request Analysis
**Tool:** GitHub CLI (`gh`)  
**Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`  
**Purpose:** Analyzes merged pull requests in the repository, extracting metadata for knowledge integration.  
**Input:** Repository context and search parameters from previous stages  
**Output:** JSON array of pull request data including numbers, titles, and URLs  
**Next Stage:** → Stage 4 (Readwise Highlights Extraction)

### Stage 4: Readwise Highlights Processing
**Tool:** Readwise CLI (`readwise.js`)  
**Command:** `node readwise.js highlights`  
**Purpose:** Extracts and processes highlights from Readwise, filtering based on repository context.  
**Input:** Filter parameters including book IDs, update timestamps, and categories  
**Output:** JSON structure containing processed highlights and annotations  
**Next Stage:** → Stage 5 (GitHub Issues Analysis)

### Stage 5: GitHub Issues Inventory
**Tool:** GitHub CLI (`gh`)  
**Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`  
**Purpose:** Creates comprehensive inventory of repository issues for knowledge mapping.  
**Input:** Repository context and filtering parameters  
**Output:** JSON file containing complete issue metadata  
**Next Stage:** → Stage 6 (Readwise Books Catalog)

### Stage 6: Readwise Books Catalog
**Tool:** Readwise CLI (`readwise.js`)  
**Command:** `node readwise.js books`  
**Purpose:** Retrieves catalog of books and documents from Readwise for cross-referencing.  
**Input:** Catalog parameters including limits and update filters  
**Output:** JSON containing book metadata and organizational structure  
**Next Stage:** → Stage 7 (GitHub Session Finalization)

### Stage 7: GitHub Session Management
**Tool:** GitHub CLI (`gh`)  
**Command:** `gh auth login` (session refresh)  
**Purpose:** Refreshes GitHub authentication and prepares for next pipeline iteration.  
**Input:** Session refresh parameters  
**Output:** Updated authentication tokens and session metadata  
**Next Stage:** → Stage 1 (Pipeline restart for next iteration)

## Data Flow Diagram

```
[Stage 1: GitHub Auth]
       ↓
[Stage 2: Readwise Search]
       ↓
[Stage 3: GitHub PR Analysis]
       ↓
[Stage 4: Readwise Highlights]
       ↓
[Stage 5: GitHub Issues]
       ↓
[Stage 6: Readwise Books]
       ↓
[Stage 7: GitHub Session]
       ↓
    [RESTART]
```

## Output Artifacts

Each pipeline iteration generates the following artifacts in the `output/` directory:

1. `github_auth_<timestamp>.json` - Authentication and session data
2. `readwise_search_<timestamp>.json` - Search results from Readwise
3. `github_prs_<timestamp>.json` - Pull request analysis
4. `readwise_highlights_<timestamp>.json` - Processed highlights
5. `github_issues_<timestamp>.json` - Complete issue inventory
6. `readwise_books_<timestamp>.json` - Book catalog
7. `pipeline_summary_<timestamp>.json` - Execution summary and metrics

## Error Handling

The pipeline includes robust error handling with the following behaviors:

- **Stage Failure:** If a stage fails, the pipeline pauses and retries up to 3 times with exponential backoff
- **Data Validation:** Each stage validates input data before processing
- **Checkpointing:** Progress is checkpointed after each stage, allowing resumption from last successful stage
- **Notification:** Failed iterations trigger alerts via configured notification channels

## Performance Considerations

- Average iteration time: 2-5 minutes depending on data volume
- Memory usage: ~200MB per stage
- Network bandwidth: Minimal (API calls are optimized for batch operations)
- Recommended execution frequency: Every 4-6 hours for continuous synchronization

---

*Note: This pipeline is designed for automated knowledge synchronization between development workflows and personal learning systems. Ensure compliance with API rate limits and data usage policies for both GitHub and Readwise services.*