
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_PATH = BASE_DIR / "logs" / "shadow_mode.jsonl"


def save_event(event):
    """Append an event to the Shadow Mode audit log."""

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")


def log_recommendation(campaign_id, investigation):
    """Save an AI recommendation for human review."""

    recommendation_id = str(uuid4())

    event = {
        "event": "recommendation_created",
        "recommendation_id": recommendation_id,
        "campaign_id": campaign_id,
        "investigation": investigation,
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    save_event(event)

    return recommendation_id


def record_human_decision(recommendation_id, decision):
    """Record a human approval or rejection."""

    decision = decision.upper()

    if decision not in ["APPROVED", "REJECTED"]:
        raise ValueError("Decision must be APPROVED or REJECTED.")

    event = {
        "event": "human_review",
        "recommendation_id": recommendation_id,
        "decision": decision,
        "reviewed_at": datetime.now(timezone.utc).isoformat()
    }

    save_event(event)

    return event
