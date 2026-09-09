# 🧠 Veya AI: Multi-Agent Architecture & Mapping

Veya is currently powered by a **6-Agent Pipeline** routed through a central Orchestrator (`AgentSystem`). The entire flow is linear, deterministic, and mapped directly to dynamic SQLite fields instead of static personas.

---

## 🏗️ 1. The Agent Pipeline (How they are mapped)

When a user sends a message, `AgentSystem` (`agent_system.py`) routes the data sequentially through these specialized agents:

1. **OnboardingEngine** (`onboarding_engine.py`)
   - *Mapping*: First intercept. Checks if `onboarding_completed == False`.
   - *Role*: Handles the dynamic 3-step conversation to gather basic profile data before letting the user into the main app.
2. **ContextAgent** (`context_agent.py`)
   - *Mapping*: Runs if onboarding is done.
   - *Role*: The Data Aggregator. Fetches the SQLite `twin_profiles`, recent `chat_memories`, and connects via OAuth to the **Live Google Calendar API** to build the unified `context` dictionary.
3. **TwinBuilder** (`twin_builder.py`)
   - *Mapping*: Receives the unified context.
   - *Role*: Fact Extractor. Scans the user's message for static facts (e.g., "husband is traveling") and writes them into the `vector_memories` table for long-term RAG storage.
4. **PatternAgent** (`pattern_agent.py` & `cognitive_matrix.py`)
   - *Mapping*: Receives the context.
   - *Role*: The Math Engine. Calculates the 7-Dimensional Cognitive State. It doesn't just read the calendar; it calculates *Attention Residue* (transition lags), *Biological Reserves*, and *Downstream Carryover Risk* (e.g., how an evening meeting ruins sleep).
5. **ActionAgent** (`action_agent.py`)
   - *Mapping*: Receives the Cognitive State + Context.
   - *Role*: The Negotiator. Uses the cognitive math to output JSON Action Cards (e.g., "Compress Meeting", "Reschedule to Friday", "Set Reminder").
6. **RagAgent & GeminiEngine** (`rag_agent.py` & `gemini_engine.py`)
   - *Mapping*: Final step.
   - *Role*: The Voice. Uses TF-IDF cosine similarity to pull past relevant memories, sends the exact strict context + history to Vertex AI, and generates the warm, human-like chat reply. 

---

## 🗄️ 2. Database Fields They Use (`veya_app.db`)

The agents rely entirely on these dynamic SQLite tables to store and score data:

### `auth_vault` (Identity)
*   `internal_uuid`: The master key mapping every piece of data together across all tables.
*   `email`, `phone_number`

### `twin_profiles` (State & Cognitive Baseline)
*   `persona_name`: Dynamic user name (adjustable in settings).
*   `work_stress_level`: Baseline multiplier (`Low`, `Moderate`, `High`) used by `PatternAgent` to calculate exhaustion.
*   `life_anchor`: User's core goal (e.g., "Balance & Peace").
*   `biological_phase`: Used to adjust energy reserves in the Cognitive Matrix.
*   `twin_maturity_weeks`: Tracking how long the user has used Veya.

### `chat_memories` (Short-Term Memory)
*   `role` & `content`: Tracks user/assistant interactions.
*   *Usage*: Fetched by `ContextAgent` and passed as `recent_chat_history` to the Vertex AI prompt to prevent AI amnesia.
*   *Reminders*: Action executions (like setting a reminder) are injected here silently as system logs.

### `vector_memories` (Long-Term RAG Engine)
*   `document_text`: The raw text of the fact.
*   `tf_idf_vector`: BLOB storing the scikit-learn numerical vector.
*   *Usage*: Queried by `RagAgent` via Cosine Similarity to remember facts from 3 weeks ago without overflowing the LLM context window.

### `notifications` (System Alerts)
*   `id`, `text`, `is_read`: Backs the new 🔔 Bell UI. Written by the backend action executor and polled dynamically by the frontend.
