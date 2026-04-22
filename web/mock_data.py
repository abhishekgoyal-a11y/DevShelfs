"""Server-side mock payloads (projects loaded from frontend JSON)."""

import json
from pathlib import Path

_BASE = Path(__file__).resolve().parent
_DATA = _BASE / "data"
_PROJECTS_JSON = _DATA / "projects.json"
_AI_TOOLS_JSON = _DATA / "ai-tools.json"


def load_projects():
    """Read curated projects from frontend JSON (single source of truth)."""
    return json.loads(_PROJECTS_JSON.read_text(encoding="utf-8"))


def load_ai_tools():
    """Read curated AI tools from frontend JSON (single source of truth)."""
    return json.loads(_AI_TOOLS_JSON.read_text(encoding="utf-8"))


PROJECTS = load_projects()
AI_TOOLS = load_ai_tools()

HACKATHONS = [
    {
        "id": "h1",
        "platform": "DevPost",
        "type": "online",
        "link": "https://devpost.com",
    },
    {
        "id": "h2",
        "platform": "MLH",
        "type": "offline",
        "link": "https://mlh.io",
    },
    {
        "id": "h3",
        "platform": "ETHGlobal",
        "type": "online",
        "link": "https://ethglobal.com",
    },
    {
        "id": "h4",
        "platform": "Campus Build Week",
        "type": "offline",
        "link": "https://example.com",
    },
]

CONTESTS = [
    {
        "id": "c1",
        "platform": "Codeforces",
        "starts_at": "2026-04-22T14:35:00Z",
        "duration_minutes": 120,
    },
    {
        "id": "c2",
        "platform": "LeetCode",
        "starts_at": "2026-04-24T01:30:00Z",
        "duration_minutes": 90,
    },
    {
        "id": "c3",
        "platform": "AtCoder",
        "starts_at": "2026-04-26T12:00:00Z",
        "duration_minutes": 100,
    },
    {
        "id": "c4",
        "platform": "CodeChef",
        "starts_at": "2026-04-28T15:00:00Z",
        "duration_minutes": 150,
    },
]
