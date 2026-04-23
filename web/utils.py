import re
from datetime import datetime, UTC


def category_slug_from_name(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower())
    s = s.strip("-")
    return s or "other"


def find_category_name_from_slug(slug: str, items: list[dict]) -> str | None:
    wanted = (slug or "").lower()
    if not wanted:
        return None
    seen: set[str] = set()
    for item in items:
        raw = (item.get("category") or "").strip() or "Other"
        if raw in seen:
            continue
        seen.add(raw)
        if category_slug_from_name(raw) == wanted:
            return raw
    return None


def group_ai_by_category(
    items: list[dict],
    category_order: tuple[str, ...] = ("Marketing & ads", "Image & design", "Video & motion"),
) -> list[tuple[str, list[dict]]]:
    m: dict[str, list[dict]] = {}
    for item in items:
        cat = (item.get("category") or "").strip() or "Other"
        m.setdefault(cat, []).append(item)
    out: list[tuple[str, list[dict]]] = []
    for name in category_order:
        if name in m:
            out.append((name, m.pop(name)))
    for name, lst in sorted(m.items()):
        out.append((name, lst))
    return out


def pick_featured_list(
    rows: list[dict], max_n: int = 3, *, key: str = "featured", order_key: str = "featured_order"
) -> list[dict]:
    hit = [x for x in rows if x.get(key)]
    hit.sort(key=lambda x: (x.get(order_key) is None, x.get(order_key) or 999))
    return hit[:max_n]


def order_projects_for_display(more: list[dict]) -> list[dict]:
    import random

    order = ("beginner", "intermediate", "advanced")
    buckets: dict[str, list[dict]] = {k: [] for k in order}
    for p in more:
        d = (p.get("difficulty") or "").lower()
        if d in buckets:
            buckets[d].append(p)
    for k in order:
        random.shuffle(buckets[k])
    return [p for d in order for p in buckets[d]]


def parse_utc(s: str) -> datetime:
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def format_utc_local(iso: str) -> str:
    d = parse_utc(iso)
    if d.tzinfo is None:
        d = d.replace(tzinfo=UTC)
    return d.astimezone(UTC).strftime("%a %d %b, %H:%M UTC")


def format_duration_minutes(mins: int) -> str:
    h, m = divmod(int(mins), 60)
    if h <= 0:
        return f"{m} min"
    if m == 0:
        return f"{h}h"
    return f"{h}h {m}m"
