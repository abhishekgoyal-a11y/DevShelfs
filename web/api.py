"""Optional read-only JSON endpoints mirroring frontend mock data."""

from django.conf import settings
from django.http import JsonResponse

from web.mock_data import AI_TOOLS, CONTESTS, HACKATHONS, PROJECTS, load_ai_tools, load_projects


def projects_list(request):
    # In DEBUG, always re-read JSON so edits match the UI without restarting runserver.
    payload = load_projects() if settings.DEBUG else PROJECTS
    return JsonResponse({"results": payload})


def ai_tools_list(request):
    payload = load_ai_tools() if settings.DEBUG else AI_TOOLS
    return JsonResponse({"results": payload})


def hackathons_list(request):
    return JsonResponse({"results": HACKATHONS})


def contests_list(request):
    return JsonResponse({"results": CONTESTS})
