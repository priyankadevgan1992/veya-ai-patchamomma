# Veya AI Vision Realization Plan
**Goal:** Implement remaining core features from the user's vision document: Conversational Onboarding, Mixed Planner View, Anxiety Detection/Voice Call, and Actionable Insights.

## 1. Conversational Onboarding (The Setup)
*   **Current state:** We just dump questions in chat or use manual settings.
*   **Action:** Update the `GeminiEngine` prompt in `veya_agents/gemini_engine.py` to ensure it only asks **one question at a time**, wraps it in conversational banter, and notes that it will learn the rest over time. If `onboarding_completed=False`, it should prioritize getting to know them gently.

## 2. Mixed Planner View (Tomorrow)
*   **Current state:** `index.html` and `main.py` hardcode 3 "suggested" events.
*   **Action:**
    *   Update `main.py` `/api/planning/tomorrow`.
    *   Separate the payload into two lists: `existing_events` (mocked from calendar) and `suggested_events` (from Veya).
    *   Update `index.html` and `app.js` to render a "Real Calendar" section and a "Veya's Suggestions" section side-by-side or stacked in the planner tab.

## 3. Anxiety Detection & Voice Call Trigger
*   **Current state:** Cognitive matrix measures stress, but Action Agent doesn't specifically look for real-time anxiety spikes (e.g. typing pattern / frantic keywords).
*   **Action:** 
    *   Update `veya_agents/action_agent.py` to look for high-stress keywords ("so stressed out", "overwhelmed", "can't breathe", "anxious").
    *   If detected, generate a `VOICE_CALL_OFFER` Action Card.
    *   *UI:* Add a `<audio>` or mock call UI modal in `index.html` that pops up when this action is clicked, simulating an empathetic AI voice chat.

## 4. Actionable Contextual Insights
*   **Current state:** Insights tab shows static scores (Energy 75, Focus 82).
*   **Action:**
    *   Update `/api/insights` in `main.py` to return actionable contextual rules based on the stress score.
    *   Example: "You are super stressed. If you are WFH, go to the balcony. If in office, sit in light."
    *   Add a "Nudge Me" button in the UI next to this advice. When clicked, it hits the `/api/actions/execute` endpoint to schedule a reminder.

## Execution Order
1. Update Planner View endpoints and UI.
2. Add Anxiety Detection & Voice Call UI.
3. Update Insights to be actionable with "Nudge me".
4. Update Gemini System Prompt for conversational onboarding.

Does this plan accurately capture your vision? Once approved, I will implement all of these changes.
