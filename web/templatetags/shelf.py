from django import template

from web.utils import category_slug_from_name

register = template.Library()


@register.filter
def category_slug(name: str) -> str:
    return category_slug_from_name(name or "")


@register.filter
def initials(name: str) -> str:
    if not name:
        return "?"
    parts = name.split()
    a = parts[0][0] if parts[0] else "?"
    if len(parts) > 1 and parts[1]:
        return (a + parts[1][0]).upper()
    if len(parts[0]) > 1:
        return (a + parts[0][1]).upper()
    return a.upper()
