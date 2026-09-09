import os
from typing import Dict, Any, List
from dotenv import load_dotenv

from google.adk.agents import Agent, SequentialAgent, LoopAgent, ParallelAgent
from google.adk.tools import ToolContext, exit_loop
from google.adk.models import Gemini
import wikipedia

load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.5-flash")

# Ensure output directory exists
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "movie_pitches")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# Helper Callbacks & Tools
# ==========================================

def append_to_state(
    tool_context: ToolContext,
    key: str,
    content: str
) -> Dict[str, str]:
    """Appends content to a list or string stored under state[key].

    Args:
        key (str): The state dictionary key to modify.
        content (str): The text or content to append.

    Returns:
        Dict[str, str]: Status message dictionary.
    """
    current_val = tool_context.state.get(key, "")
    if isinstance(current_val, list):
        tool_context.state[key] = current_val + [content]
    elif isinstance(current_val, str):
        tool_context.state[key] = (current_val + "\n\n" + content).strip()
    else:
        tool_context.state[key] = content
    return {"status": "success"}


def wikipedia_search_tool(query: str) -> str:
    """Searches Wikipedia for summary information on a historical figure.

    Args:
        query (str): The name or topic to search on Wikipedia.

    Returns:
        str: Summary text from Wikipedia or error message.
    """
    try:
        return wikipedia.summary(query, sentences=5)
    except Exception as e:
        return f"Error fetching Wikipedia summary: {str(e)}"


def write_file_tool(
    filename: str,
    content: str
) -> Dict[str, str]:
    """Writes content to a text file in the movie_pitches directory.

    Args:
        filename (str): Name of the file (e.g. 'Marcus_Aurelius_Movie_Pitch.txt').
        content (str): Text content to write.

    Returns:
        Dict[str, str]: Status response.
    """
    if not filename.endswith(".txt"):
        filename += ".txt"
    # Clean filename
    safe_filename = "".join(c for c in filename if c.isalnum() or c in (" ", "_", "-")).rstrip()
    if not safe_filename.endswith(".txt"):
        safe_filename += ".txt"
    filepath = os.path.join(OUTPUT_DIR, safe_filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "success", "filepath": filepath}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ==========================================
# Agents Definition
# ==========================================

# 1. Researcher Agent
researcher = Agent(
    name="researcher",
    model=Gemini(model=model_name),
    description="Researches historical figures using Wikipedia search tools and stores research in session state.",
    instruction="""
    INSTRUCTIONS:
    - Identify the historical subject or theme requested in HISTORICAL_SUBJECT.
    - Use 'wikipedia_search_tool' to collect relevant historical facts, background, key life events, and struggles.
    - Use 'append_to_state' with key 'research' to save your findings.
    
    HISTORICAL_SUBJECT: { HISTORICAL_SUBJECT? }
    EXISTING_RESEARCH: { research? }
    CRITICAL_FEEDBACK: { CRITICAL_FEEDBACK? }
    """,
    tools=[wikipedia_search_tool, append_to_state],
    output_key="research"
)

# 2. Screenwriter Agent
screenwriter = Agent(
    name="screenwriter",
    model=Gemini(model=model_name),
    description="Crafts a compelling three-act movie plot outline based on historical research.",
    instruction="""
    INSTRUCTIONS:
    - Create or update a 3-Act movie plot outline using the RESEARCH facts provided.
    - Make sure to address any issues raised in CRITICAL_FEEDBACK if available.
    - Write an engaging narrative highlighting character motivations, key turning points, and thematic arcs.
    
    RESEARCH: { research? }
    CRITICAL_FEEDBACK: { CRITICAL_FEEDBACK? }
    """,
    output_key="PLOT_OUTLINE"
)

# 3. Critic Agent
critic = Agent(
    name="critic",
    model=Gemini(model=model_name),
    description="Reviews the plot outline to ensure narrative quality and historical grounding.",
    instruction="""
    INSTRUCTIONS:
    Consider these questions about the PLOT_OUTLINE:
    - Does it meet a satisfying three-act cinematic structure?
    - Do the characters' struggles seem engaging?
    - Does it feel grounded in a real time period in history?
    - Does it sufficiently incorporate historical details from the RESEARCH?

    If the PLOT_OUTLINE does a good job with these questions, exit the writing loop with your 'exit_loop' tool.
    If significant improvements can be made, use the 'append_to_state' tool to add your feedback to the field 'CRITICAL_FEEDBACK'.
    Explain your decision and summarize the feedback provided.

    PLOT_OUTLINE: { PLOT_OUTLINE? }
    RESEARCH: { research? }
    """,
    tools=[append_to_state, exit_loop]
)

# 4. Box Office Researcher Agent
box_office_researcher = Agent(
    name="box_office_researcher",
    model=Gemini(model=model_name),
    description="Considers the box office potential of this film",
    instruction="""
    PLOT_OUTLINE: { PLOT_OUTLINE? }
    INSTRUCTIONS: Write a report on the box office potential of a movie like that described in PLOT_OUTLINE based on the reported box office performance of other recent historical/biographical films.
    """,
    output_key="box_office_report"
)

# 5. Casting Agent
casting_agent = Agent(
    name="casting_agent",
    model=Gemini(model=model_name),
    description="Generates casting ideas for this film",
    instruction="""
    PLOT_OUTLINE: { PLOT_OUTLINE? }
    INSTRUCTIONS: Generate ideas for casting for the characters described in PLOT_OUTLINE by suggesting actors who have received positive feedback from critics and/or fans when they have played similar roles.
    """,
    output_key="casting_report"
)

# 6. File Writer Agent
file_writer = Agent(
    name="file_writer",
    model=Gemini(model=model_name),
    description="Writes the final film pitch document to disk.",
    instruction="""
    INSTRUCTIONS:
    - Create a marketable, contemporary movie title suggestion for the movie described in the PLOT_OUTLINE.
    - Use your 'write_file_tool' to create a new txt file with the following arguments:
      - for filename: use the movie title
      - for content: include PLOT_OUTLINE, BOX_OFFICE_REPORT, and CASTING_REPORT formatted clearly.
    - Inform the user once the file has been successfully written to disk!

    PLOT_OUTLINE: { PLOT_OUTLINE? }
    BOX_OFFICE_REPORT: { box_office_report? }
    CASTING_REPORT: { casting_report? }
    """,
    tools=[write_file_tool]
)


# ==========================================
# Workflow Orchestration
# ==========================================

# Writers Room Loop Agent (Iterative loop of research, screenwriting, and critical review)
writers_room = LoopAgent(
    name="writers_room",
    description="Iterates through research and writing to improve a movie plot outline.",
    sub_agents=[researcher, screenwriter, critic],
    max_iterations=5,
)

# Preproduction Parallel Agent (Fan-out execution of Box Office Analysis and Casting Ideas)
preproduction_team = ParallelAgent(
    name="preproduction_team",
    sub_agents=[box_office_researcher, casting_agent]
)

# Sequential Film Concept Team Agent
film_concept_team = SequentialAgent(
    name="film_concept_team",
    description="Write a film plot outline and save it as a text file.",
    sub_agents=[writers_room, preproduction_team, file_writer]
)

# Root Greeter Agent
root_agent = Agent(
    name="greeter",
    model=Gemini(model=model_name),
    description="Greets the user and collects the historical subject for the film pitch.",
    instruction="""
    INSTRUCTIONS:
    - Greet the user enthusiastically and ask them which historical character or figure they would like to make a movie pitch about.
    - Save their requested historical figure under the state key 'HISTORICAL_SUBJECT'.
    - Transfer control to 'film_concept_team' once the subject is identified.
    """,
    output_key="HISTORICAL_SUBJECT",
    sub_agents=[film_concept_team]
)
