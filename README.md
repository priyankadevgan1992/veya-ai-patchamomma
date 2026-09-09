# GENAI106: Google Agent Development Kit (ADK) Multi-Agent Systems Lab

This workspace contains a complete implementation of the **GENAI106 Multi-Agent Systems** lab using Google Agent Development Kit (Google ADK).

---

## 🌟 What was Built

### 1. `parent_and_subagents/` (Hierarchical Agent Tree & Session State)
Demonstrates hierarchical parent-to-subagent routing and state dictionary manipulation:
- **`steering` (Root Agent)**: Evaluates user intent and routes to sub-agents.
- **`travel_brainstormer` (Sub-Agent)**: Helps users brainstorm destination countries.
- **`attractions_planner` (Sub-Agent)**: Recommends attractions and uses `save_attractions_to_state` tool to store items into `ToolContext.state["attractions"]`. Uses ADK **Key Templating** (`{ attractions? }`) to format saved attractions in prompts.
- **Peer Transfers**: Demonstrates moving control between `travel_brainstormer` and `attractions_planner`.

### 2. `workflow_agents/` (SequentialAgent, LoopAgent & ParallelAgent Workflow)
Demonstrates workflow orchestration across specialized agents to build a movie pitch document:
- **`greeter` (Root Agent)**: Asks user for a historical character.
- **`writers_room` (`LoopAgent`)**: Runs an iterative loop up to `max_iterations=5`:
  - `researcher`: Queries Wikipedia for historical details and writes to `state["research"]`.
  - `screenwriter`: Outlines a 3-Act plot structure based on historical research.
  - `critic`: Evaluates the outline. If satisfied, calls `exit_loop`. Otherwise, appends feedback to `CRITICAL_FEEDBACK`.
- **`preproduction_team` (`ParallelAgent`)**: Runs concurrent fan-out reports:
  - `box_office_researcher`: Analyzes box office potential based on recent biographical films.
  - `casting_agent`: Generates actor recommendations for major roles.
- **`file_writer` (`Agent`)**: Formats all reports and saves the final output as a `.txt` file into `movie_pitches/`.
- **`film_concept_team` (`SequentialAgent`)**: Sequences `writers_room` -> `preproduction_team` -> `file_writer`.

---

## 🚀 Setup & Execution Instructions

### Step 1: Set up Environment Variables
Create a `.env` file in `parent_and_subagents/` and `workflow_agents/` (or copy `.env.example`):

```bash
# If using Gemini API Key:
GOOGLE_API_KEY=your_gemini_api_key_here
MODEL=gemini-2.5-flash
```

Or for Vertex AI:
```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
GOOGLE_CLOUD_LOCATION=us-central1
MODEL=gemini-2.5-flash
```

### Step 2: Run via CLI (`adk run`)

**Testing Parent & Sub-Agents:**
```bash
adk run parent_and_subagents
```
- Type: `hello`
- Reply: `I could use some help deciding.` (Routes to `travel_brainstormer`)
- Or reply: `I would like to go to Egypt.` (Routes to `attractions_planner`)
- Pick an attraction: `I'll go to the Pyramids`
- Ask: `What is on my list?`

**Testing Workflow Agents:**
```bash
adk run workflow_agents
```
- Type: `hello`
- Give a historical character: e.g. `Ada Lovelace`, `Marcus Aurelius`, or `Zhang Zhongjing`.
- Watch the iterative loop, parallel report generation, and check `movie_pitches/` for the generated file!

---

## 🌐 Run via ADK Web UI (`adk web`)

Launch the visual web interface with event hierarchy graph and live session state inspection:

```bash
adk web
```
Then open `http://localhost:8000` in your browser.
Select `parent_and_subagents` or `workflow_agents` from the drop-down menu!
