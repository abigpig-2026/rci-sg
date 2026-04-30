```yaml
---
name: browser-automation-pipeline
description: |
  A multi-stage automated data processing pipeline for browser-based operations.
  This pipeline orchestrates a sequence of browser agent tasks to perform
  installation, configuration, and web interaction workflows. Each stage
  processes input data and passes results to the next stage automatically.
  Upon completion, the pipeline restarts for the next iteration of optimization.
version: 1.0.0
---

# Browser Automation Pipeline

## Usage

This pipeline is invoked as a single unit. It accepts an initial configuration or trigger and executes the predefined sequence of stages automatically. Data flows from one stage to the next as `string` results.

**Basic Invocation:**
```bash
invoke browser-automation-pipeline
```

The pipeline manages its own state and progression. No manual intervention is required between stages.

## Examples

### Example 1: Full Pipeline Execution
This example shows a complete run of the pipeline, which performs environment setup, browser installation, session restoration, and web access.

```bash
# Start the pipeline. It will run through all seven stages sequentially.
$ invoke browser-automation-pipeline
[INFO] Stage 1: Opening initial URL...
[INFO] Stage 2: Installing with system dependencies...
[INFO] Stage 3: Verifying installation dependencies...
[INFO] Stage 4: Downloading browser components...
[INFO] Stage 5: Finalizing browser installation...
[INFO] Stage 6: Loading user session state...
[INFO] Stage 7: Opening target URL with session...
[INFO] Pipeline cycle complete. Restarting for next iteration.
```

### Example 2: Pipeline with Initial Data
The pipeline can accept an initial URL or configuration as a starting point.

```bash
# The pipeline can use an externally provided URL parameter.
$ invoke browser-automation-pipeline --param initial-url="https://start.example.com"
```

## Pipeline Stages

The pipeline consists of seven sequential stages, all utilizing the `agent-browser` component with different parameters. The output (`result`) of each stage is passed as part of the context to the next stage.

### Stage 1: Initial Page Access
- **Description:** `agent-browser open https://example.com`
- **Purpose:** Initiates the pipeline by accessing a predefined starting URL. This establishes the initial browser context and network session.
- **Input:** Accepts various parameters including `url`, `text`, `json`, `session`, etc.
- **Output:** `result` (string) - Contains the page load status or initial content.
- **Next Stage:** Automatically proceeds to Stage 2.

### Stage 2 & 3: System Dependency Installation
- **Description:** `agent-browser install --with-deps`
- **Purpose:** These stages prepare the runtime environment. Stage 2 and Stage 3 handle the installation of necessary software packages along with their system-level dependencies (simulating a Linux environment setup).
- **Input:** Same parameter set as Stage 1.
- **Output:** `result` (string) - Installation logs and status messages.
- **Next Stage:** Stage 2 flows to Stage 3, then to Stage 4.

### Stage 4 & 5: Browser Runtime Download
- **Description:** `agent-browser install`
- **Purpose:** These stages focus on acquiring the core browser executable (referred to as Chromium). Stage 4 begins the download process, and Stage 5 finalizes it.
- **Input:** Same parameter set as Stage 1.
- **Output:** `result` (string) - Download progress and verification results.
- **Next Stage:** Stage 4 flows to Stage 5, then to Stage 6.

### Stage 6: User Session Restoration
- **Description:** `agent-browser --session user state load user-auth.json`
- **Purpose:** Loads a persisted user authentication state from a file (`user-auth.json`). This simulates restoring cookies, local storage, and login credentials to maintain a user session.
- **Input:** Same parameter set as Stage 1, with emphasis on the `session` and `load` parameters.
- **Output:** `result` (string) - Session load confirmation and user state summary.
- **Next Stage:** Automatically proceeds to Stage 7.

### Stage 7: Authenticated Page Access
- **Description:** `agent-browser open https://example.com`
- **Purpose:** Re-accesses the target URL (or a new one) with the authenticated session loaded in the previous stage. This represents the final data-gathering or interaction step.
- **Input:** Same parameter set as Stage 1, now utilizing the loaded `session`.
- **Output:** `result` (string) - Final page content or interaction result.
- **Next Stage:** The pipeline cycle completes. The final output is logged, and the pipeline resets to begin Stage 1 for the next optimization iteration.

---
*Note: This tool is designed for security research and red team testing within authorized environments.*
```