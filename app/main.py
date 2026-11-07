from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langfuse.langchain import CallbackHandler

from app.agent.graph import agent
from app.evaluation.shadow_mode import (
    log_recommendation,
    record_human_decision
)


def run_agent(question, campaign_id):

    # Initialize Langfuse tracing
    langfuse_handler = CallbackHandler()

    # Execute the agent with Langfuse callback
    response = agent.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ]
        },
        config={
            "callbacks": [langfuse_handler]
        }
    )

    print("\n--- AGENT EXECUTION TRACE ---")

    for message in response["messages"]:

        if isinstance(message, AIMessage) and message.tool_calls:
            for tool_call in message.tool_calls:
                print(f"Tool selected: {tool_call['name']}")
                print(f"Tool arguments: {tool_call['args']}")

        elif isinstance(message, ToolMessage):
            print(f"Tool result: {message.content}")

    print("\n--- FINAL AGENT RESPONSE ---")

    final_message = response["messages"][-1]
    investigation = final_message.content

    print(investigation)

    # Shadow Mode: Save recommendation for human review
    recommendation_id = log_recommendation(
        campaign_id=campaign_id,
        investigation=investigation
    )

    print("\n--- SHADOW MODE ---")
    print("Recommendation saved for human review.")
    print(f"Recommendation ID: {recommendation_id}")
    print("Status: PENDING")

    # Human-in-the-Loop: Ask for a decision
    decision = input(
        "\nApprove this recommendation? (yes/no): "
    ).strip().lower()

    if decision == "yes":
        record_human_decision(
            recommendation_id,
            "APPROVED"
        )
        print("Human review recorded: APPROVED")

    elif decision == "no":
        record_human_decision(
            recommendation_id,
            "REJECTED"
        )
        print("Human review recorded: REJECTED")

    else:
        print("Invalid response. Recommendation remains PENDING.")

    return investigation


if __name__ == "__main__":

    campaign_id = "CMP103"

    question = (
        f"Investigate {campaign_id}. "
        "Has it exceeded its allocated budget? "
        "Explain using the campaign data."
    )

    print("\nAdOps Agent Investigation")
    print("-------------------------")

    answer = run_agent(question, campaign_id)
