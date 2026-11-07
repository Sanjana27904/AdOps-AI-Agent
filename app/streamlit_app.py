import os
import sys
from pathlib import Path

# --------------------------------------------------
# 1. Set up project path
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

# --------------------------------------------------
# 2. Configure Streamlit
# --------------------------------------------------

st.set_page_config(
    page_title="AdOps Agent",
    page_icon="📊",
    layout="wide",
)

# --------------------------------------------------
# 3. Load Streamlit Cloud secrets
# --------------------------------------------------

try:
    for key in [
        "GROQ_API_KEY",
        "GROQ_MODEL",
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
        "LANGFUSE_BASE_URL",
    ]:
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])

except Exception:
    # Local development can use credentials from .env
    pass

# --------------------------------------------------
# 4. Import project dependencies
# --------------------------------------------------

from langchain_core.messages import HumanMessage, AIMessage
from langfuse.langchain import CallbackHandler

from app.database.db import DB_PATH
from app.database.seed import seed_database

from app.agent.graph import agent

from app.tools.campaign_tools import (
    list_campaigns,
    get_campaign_summary,
    get_campaign_daily_data,
)

from app.tools.analysis_tools import (
    calculate_metrics,
    detect_anomalies,
)

from app.evaluation.shadow_mode import (
    log_recommendation,
    record_human_decision,
)

# --------------------------------------------------
# 5. Initialize SQLite database
# --------------------------------------------------

if not DB_PATH.exists():
    seed_database()

# --------------------------------------------------
# 6. Application heading
# --------------------------------------------------

st.title("📊 AdOps Agent")
st.caption("Autonomous Advertising Operations Assistant")
st.divider()

# --------------------------------------------------
# 7. Select a campaign
# --------------------------------------------------

campaigns = list_campaigns()

if not campaigns:
    st.error("No campaigns found. Please seed the database first.")
    st.stop()

campaign_id = st.selectbox(
    "Select a campaign",
    campaigns,
)

# --------------------------------------------------
# 8. Retrieve campaign data
# --------------------------------------------------

summary = get_campaign_summary(campaign_id)

metrics = calculate_metrics(summary)

daily_data = get_campaign_daily_data(campaign_id)

anomalies = detect_anomalies(daily_data)

# --------------------------------------------------
# 9. Campaign overview
# --------------------------------------------------

st.subheader(f"Campaign Overview — {campaign_id}")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Impressions",
    f"{summary['total_impressions']:,}",
)

col2.metric(
    "Clicks",
    f"{summary['total_clicks']:,}",
)

col3.metric(
    "Total Spend",
    f"{summary['total_spend']:,.2f}",
)

col4.metric(
    "Conversions",
    f"{summary['total_conversions']:,}",
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "CTR",
    f"{metrics['ctr_percent']}%",
)

col2.metric(
    "Conversion Rate",
    f"{metrics['conversion_rate_percent']}%",
)

col3.metric(
    "Budget Usage",
    f"{metrics['budget_usage_percent']}%",
)

if metrics["over_budget"]:
    st.warning(
        f"Campaign has exceeded its budget by "
        f"{summary['total_spend'] - summary['budget']:.2f} units."
    )
else:
    st.success("Campaign is within its allocated budget.")

st.divider()

# --------------------------------------------------
# 10. Daily campaign data
# --------------------------------------------------

with st.expander("View daily campaign data"):
    st.dataframe(
        daily_data,
        use_container_width=True,
    )

# --------------------------------------------------
# 11. Anomaly detection
# --------------------------------------------------

st.subheader("Anomaly Detection")

if anomalies:
    for anomaly in anomalies:
        st.warning(
            f"{anomaly['date']}: Impressions decreased by "
            f"{anomaly['decrease_percent']}% "
            f"({anomaly['previous_impressions']:,} → "
            f"{anomaly['current_impressions']:,})."
        )
else:
    st.success("No significant impression drops detected.")

st.divider()

# --------------------------------------------------
# 12. AI campaign investigation
# --------------------------------------------------

st.subheader("AI Campaign Investigation")

if st.button("Investigate Campaign", type="primary"):

    question = (
        f"Investigate campaign {campaign_id}. "
        "Analyze its performance, budget usage, and anomalies. "
        "Explain the findings and recommend appropriate actions. "
        "Use the available campaign tools and do not invent data."
    )

    with st.spinner("Agent is investigating campaign data..."):

        try:
            langfuse_handler = CallbackHandler()

            response = agent.invoke(
                {
                    "messages": [
                        HumanMessage(content=question)
                    ]
                },
                config={
                    "callbacks": [langfuse_handler]
                },
            )

            investigation = next(
                (
                    message.content
                    for message in reversed(response["messages"])
                    if isinstance(message, AIMessage)
                    and isinstance(message.content, str)
                    and message.content.strip()
                    and not message.tool_calls
                ),
                None,
            )

            if not investigation:

                st.error(
                    "The agent did not return a final investigation."
                )

            else:

                recommendation_id = log_recommendation(
                    campaign_id=campaign_id,
                    investigation=investigation,
                )

                st.session_state["investigation"] = investigation

                st.session_state["recommendation_id"] = (
                    recommendation_id
                )

                st.session_state["investigated_campaign"] = (
                    campaign_id
                )

                st.session_state["decision_recorded"] = False

        except Exception as error:

            st.error(f"Investigation failed: {error}")

# --------------------------------------------------
# 13. Display investigation and human review
# --------------------------------------------------

if (
    st.session_state.get("investigation")
    and st.session_state.get("investigated_campaign") == campaign_id
):

    st.markdown("### Agent Findings")

    st.markdown(
        st.session_state["investigation"]
    )

    st.divider()

    st.subheader("Human Review — Shadow Mode")

    st.info(
        "This recommendation is logged for review only. "
        "Approving it does not make any changes to a live advertising campaign."
    )

    if not st.session_state.get("decision_recorded"):

        st.write(
            "Review the recommendation and choose an action:"
        )

        approve_col, reject_col = st.columns(2)

        with approve_col:

            if st.button("Approve Recommendation"):

                record_human_decision(
                    st.session_state["recommendation_id"],
                    "APPROVED",
                )

                st.session_state["decision_recorded"] = True

                st.session_state["decision"] = "APPROVED"

                st.rerun()

        with reject_col:

            if st.button("Reject Recommendation"):

                record_human_decision(
                    st.session_state["recommendation_id"],
                    "REJECTED",
                )

                st.session_state["decision_recorded"] = True

                st.session_state["decision"] = "REJECTED"

                st.rerun()

    else:

        st.success(
            f"Human review recorded: "
            f"{st.session_state['decision']}"
        )

    st.caption(
        f"Recommendation ID: "
        f"{st.session_state['recommendation_id']}"
    )
