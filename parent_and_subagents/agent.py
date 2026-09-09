import os
from typing import List, Dict, Any
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.models import Gemini

# Load environment variables
load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.5-flash")

# ==========================================
# Tools
# ==========================================

def save_attractions_to_state(
    tool_context: ToolContext,
    attractions: List[str]
) -> Dict[str, str]:
    """Saves the list of attractions to state["attractions"].

    Args:
        attractions (List[str]): A list of strings to add to the list of attractions.

    Returns:
        Dict[str, str]: Status dictionary indicating success.
    """
    # Load existing attractions from state. If none exist, start an empty list
    existing_attractions = tool_context.state.get("attractions", [])

    # Update the 'attractions' key with a combination of old and new lists
    tool_context.state["attractions"] = existing_attractions + attractions

    # Return status message
    return {"status": "success"}


# ==========================================
# Sub-Agents
# ==========================================

# 1. Travel Brainstormer Agent
travel_brainstormer = Agent(
    name="travel_brainstormer",
    model=Gemini(model=model_name),
    description="Helps the user brainstorm destination countries if they don't know where they would like to visit.",
    instruction="""
    INSTRUCTIONS:
    - Welcome the user warmly and help them decide on travel destinations.
    - Provide a curated list of top destination countries based on categories (e.g. Adventure, History, Food, Relaxation).
    - Ask clarifying questions to narrow down their travel goals.
    """
)

# 2. Attractions Planner Agent
attractions_planner = Agent(
    name="attractions_planner",
    model=Gemini(model=model_name),
    description="Helps the user build a list of things to do once they know which country they would like to visit.",
    instruction="""
    INSTRUCTIONS:
    - Help the user explore attractions for the specific country they want to visit.
    - When they reply selecting an attraction, use your 'save_attractions_to_state' tool to save their selected attraction and then provide more possible attractions.
    - If they ask to view their saved list, provide a bulleted list of { attractions? } and then suggest some more.
    """,
    tools=[save_attractions_to_state]
)


# ==========================================
# Root Agent (Parent Agent)
# ==========================================

root_agent = Agent(
    name="steering",
    model=Gemini(model=model_name),
    description="The main travel assistant that steers the user to either travel brainstorming or attractions planning.",
    instruction="""
    INSTRUCTIONS:
    - Welcome the user to their travel adventure.
    - Ask them if they already know where they'd like to travel, or if they would like some help deciding.
    - If they need help deciding, send them to 'travel_brainstormer'.
    - If they know what country they'd like to visit, send them to the 'attractions_planner'.
    """,
    sub_agents=[travel_brainstormer, attractions_planner]
)
