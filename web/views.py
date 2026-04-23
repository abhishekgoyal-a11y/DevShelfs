from __future__ import annotations

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from web import mock_data
from web.mock_data import CONTESTS, HACKATHONS, load_ai_tools, load_projects
from web.utils import (
    find_category_name_from_slug,
    format_duration_minutes,
    format_utc_local,
    group_ai_by_category,
    order_projects_for_display,
    pick_featured_list,
)

SITE_ABOUT = (
    "DevShelf is a personal, living catalog: one place to showcase shipped projects and the "
    "AI tools worth keeping. It favors clarity—what something is, how it fits your workflow, "
    "and where to go next—over noise."
)

PROJECT_BODY = {
    "smart-study-assistant",
    "notes-qa-bot",
    "ai-email-reply-generator",
}


def _projects_data():
    return load_projects() if settings.DEBUG else mock_data.PROJECTS


def _ai_tools_data():
    return load_ai_tools() if settings.DEBUG else mock_data.AI_TOOLS


def _layout(path: str) -> str:
    if path.startswith("/ai-tools"):
        return "ai_tools"
    if path.startswith("/hackathons"):
        return "hackathons"
    if path.startswith("/contests"):
        return "contests"
    return "default"


def home(request):
    projects = _projects_data()
    tools = _ai_tools_data()
    return render(
        request,
        "web/home.html",
        {
            "layout": _layout(request.path),
            "active_nav": None,
            "project_count": len(projects),
            "ai_tool_count": len(tools),
            "featured_projects": pick_featured_list(projects, 3),
            "featured_tools": pick_featured_list(tools, 10),
            "site_about": SITE_ABOUT,
        },
    )


def projects_list(request):
    all_p = _projects_data()
    q = (request.GET.get("q") or "").strip().lower()
    difficulty = (request.GET.get("difficulty") or "all").lower()

    def match(p: dict) -> bool:
        if difficulty != "all" and (p.get("difficulty") or "").lower() != difficulty:
            return False
        if not q:
            return True
        hay = " ".join(
            [p.get("title") or "", p.get("description") or "", *((p.get("tech") or []))],
        ).lower()
        return q in hay

    filtered = [p for p in all_p if match(p)]
    featured = pick_featured_list(list(filtered), 5)
    f_ids = {p.get("id") for p in featured}
    more_src = [p for p in filtered if p.get("id") not in f_ids]
    if difficulty == "all" and not q:
        more = order_projects_for_display(more_src)
    else:
        more = more_src

    source = "api" if not settings.DEBUG else "local"
    return render(
        request,
        "web/projects.html",
        {
            "layout": _layout(request.path),
            "active_nav": "projects",
            "projects": filtered,
            "featured": featured,
            "more": more,
            "q": request.GET.get("q") or "",
            "difficulty": difficulty,
            "data_source": source,
        },
    )


def project_detail(request, slug: str):
    all_p = _projects_data()
    project = next((p for p in all_p if p.get("slug") == slug), None)
    if not project:
        return render(
            request,
            "web/project_not_found.html",
            {"layout": _layout(request.path), "active_nav": "projects", "slug": slug},
            status=404,
        )
    body = "default"
    if slug in PROJECT_BODY:
        body = slug
    return render(
        request,
        "web/project_detail.html",
        {
            "layout": _layout(request.path),
            "active_nav": "projects",
            "project": project,
            "body_template": f"web/project_bodies/{body}.html",
        },
    )


def ai_tools_list(request):
    items = _ai_tools_data()
    sections = group_ai_by_category(items)
    return render(
        request,
        "web/ai_tools.html",
        {
            "layout": _layout(request.path),
            "active_nav": "ai",
            "sections": sections,
            "data_source": "api" if not settings.DEBUG else "local",
        },
    )


def ai_tools_category(request, category_slug: str):
    items = _ai_tools_data()
    name = find_category_name_from_slug(category_slug, items)
    if not name:
        return HttpResponseRedirect(reverse("ai_tools"))
    tools = [
        e
        for e in items
        if ((e.get("category") or "").strip() or "Other") == name
    ]
    return render(
        request,
        "web/ai_tools_category.html",
        {
            "layout": _layout(request.path),
            "active_nav": "ai",
            "category_name": name,
            "tools": tools,
            "data_source": "api" if not settings.DEBUG else "local",
        },
    )


def pomelli(request):
    return render(
        request,
        "web/pomelli.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def midjourney(request):
    return render(
        request,
        "web/midjourney.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def dalle(request):
    return render(
        request,
        "web/dalle.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def runwayml(request):
    return render(
        request,
        "web/runwayml.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def cursor_ai(request):
    return render(
        request,
        "web/cursor.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def github_copilot(request):
    return render(
        request,
        "web/github_copilot.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def autogpt(request):
    return render(
        request,
        "web/autogpt.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def hackathons(request):
    type_filter = (request.GET.get("type") or "all").lower()
    q = (request.GET.get("q") or "").strip().lower()
    rows = []
    for h in HACKATHONS:
        if type_filter != "all" and h.get("type") != type_filter:
            continue
        if q and q not in (h.get("platform") or "").lower():
            continue
        rows.append(h)
    return render(
        request,
        "web/hackathons.html",
        {
            "layout": _layout(request.path),
            "active_nav": None,
            "rows": rows,
            "type_filter": type_filter,
            "q": request.GET.get("q") or "",
            "data_source": "api",
        },
    )


def contests(request):
    sort = (request.GET.get("sort") or "soon").lower()
    platform_q = (request.GET.get("platform") or "").strip().lower()
    min_d = (request.GET.get("min_dur") or "").strip()
    min_n: int | None
    try:
        min_n = int(min_d) if min_d else None
    except ValueError:
        min_n = None

    rows = [dict(c) for c in CONTESTS]
    if platform_q:
        rows = [c for c in rows if platform_q in (c.get("platform") or "").lower()]
    if min_n and min_n > 0:
        rows = [c for c in rows if int(c.get("duration_minutes") or 0) >= min_n]

    if sort == "platform":
        rows.sort(key=lambda c: (c.get("platform") or "").lower())
    elif sort == "duration":
        rows.sort(key=lambda c: -int(c.get("duration_minutes") or 0))
    else:
        rows.sort(key=lambda c: c.get("starts_at") or "")

    for c in rows:
        c["starts_fmt"] = format_utc_local(c["starts_at"])
        c["duration_fmt"] = format_duration_minutes(int(c.get("duration_minutes") or 0))

    return render(
        request,
        "web/contests.html",
        {
            "layout": _layout(request.path),
            "active_nav": None,
            "rows": rows,
            "sort": sort,
            "platform_q": request.GET.get("platform") or "",
            "min_dur": min_d,
            "data_source": "api",
        },
    )
