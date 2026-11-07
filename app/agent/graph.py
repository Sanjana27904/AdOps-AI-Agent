
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from app.agent.prompts import SYSTEM_PROMPT

from langgraph.graph import StateGraph, START
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from app.tools.campaign_tools import (
    list_campaigns,
    get_campaign_summary,
    get_campaign_daily_data
)

from app.tools.analysis_tools import (
    calculate_metrics,
    detect_anomalies
)


# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL")

if not api_key or not model_name:
    raise ValueError("Groq credentials are missing from .env")


# Initialize Groq
llm = ChatGroq(
    model=model_name,
    api_key=api_key,
    temperature=0
)


# ---------------------------------
# Define tools available to the AI
# ---------------------------------

@tool
def list_available_campaigns():
    """List all campaign IDs available in the advertising database."""

    return list_campaigns()


@tool
def get_campaign_information(campaign_id: str):
    """Retrieve aggregated performance information for a campaign."""

    result = get_campaign_summary(campaign_id)

    if result is None:
        return {"error": f"Campaign {campaign_id} was not found."}

    return result


@tool
def get_campaign_performance_metrics(campaign_id: str):
    """Calculate CTR, conversion rate and budget usage for a campaign."""

    campaign = get_campaign_summary(campaign_id)

    if campaign is None:
        return {"error": f"Campaign {campaign_id} was not found."}

    return calculate_metrics(campaign)

@tool
def investigate_campaign_anomalies(campaign_id: str):
    """Detect significant day-to-day impression decreases in a campaign."""

    daily_data = get_campaign_daily_data(campaign_id)

    if not daily_data:
        return {
            "campaign_id": campaign_id,
            "message": f"No daily data found for {campaign_id}.",
            "anomalies": []
        }

    anomalies = detect_anomalies(daily_data)

    if not anomalies:
        return {
            "campaign_id": campaign_id,
            "message": "No significant impression drops detected.",
            "anomalies": []
        }

    return {
        "campaign_id": campaign_id,
        "message": "Significant impression drops detected.",
        "anomalies": anomalies
    }

# Collect all available tools
tools = [
    list_available_campaigns,
    get_campaign_information,
    get_campaign_performance_metrics,
    investigate_campaign_anomalies
]


# Bind tools to the Groq model
llm_with_tools = llm.bind_tools(tools)


# ---------------------------------
# Define the assistant node
# ---------------------------------

def assistant(state: MessagesState):

    system_message = SystemMessage(
        content=SYSTEM_PROMPT
    )

    response = llm_with_tools.invoke(
        [system_message] + state["messages"]
    )

    return {"messages": [response]}



# ---------------------------------
# Build the LangGraph workflow
# ---------------------------------

builder = StateGraph(MessagesState)

builder.add_node("assistant", assistant)

builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")

builder.add_conditional_edges(
    "assistant",
    tools_condition
)

builder.add_edge("tools", "assistant")


# Compile the workflow
agent = builder.compile()
