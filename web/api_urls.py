from django.urls import path

from web import api

urlpatterns = [
    path("projects/", api.projects_list),
    path("ai-tools/", api.ai_tools_list),
    path("hackathons/", api.hackathons_list),
    path("contests/", api.contests_list),
]
