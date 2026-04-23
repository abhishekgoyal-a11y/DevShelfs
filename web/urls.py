from django.urls import path

from web import views

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/", views.projects_list, name="projects"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("ai-tools/pomelli-ai", views.pomelli, name="pomelli_ai"),
    path("ai-tools/pomeli-ai", views.pomelli),
    path("ai-tools/midjourney", views.midjourney, name="midjourney"),
    path("ai-tools/dall-e", views.dalle, name="dalle"),
    path("ai-tools/runwayml", views.runwayml, name="runwayml"),
    path("ai-tools/cursor", views.cursor_ai, name="cursor_ai"),
    path("ai-tools/category/<slug:category_slug>/", views.ai_tools_category, name="ai_tools_category"),
    path("ai-tools/", views.ai_tools_list, name="ai_tools"),
    path("hackathons/", views.hackathons, name="hackathons"),
    path("contests/", views.contests, name="contests"),
]
