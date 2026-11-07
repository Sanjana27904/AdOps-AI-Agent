
from pathlib import Path

# Locate the project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Locate the SKILL.md file
SKILL_PATH = BASE_DIR / "skills" / "SKILL.md"


def load_skill_instructions():
    """Load reusable instructions from SKILL.md."""

    if not SKILL_PATH.exists():
        raise FileNotFoundError(
            f"Skill instructions not found: {SKILL_PATH}"
        )

    return SKILL_PATH.read_text(encoding="utf-8")


# Load the skill instructions
SKILL_INSTRUCTIONS = load_skill_instructions()


# Combine the agent's role with its skill instructions
SYSTEM_PROMPT = f"""
You are an AI Advertising Operations Agent.

Follow the instructions below whenever you investigate
advertising campaign data.

{SKILL_INSTRUCTIONS}
"""
