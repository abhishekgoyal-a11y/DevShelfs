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
    "resume-cover-letter-improver",
    "website-rag-chatbot",
    "ai-product-description-generator",
    "personal-study-tutor",
    "resume-job-match-optimizer",
    "ai-coding-pair-programmer",
    "meeting-lecture-summarizer",
    "personalized-news-digest",
    "customer-support-agent",
    "ai-debate-partner",
    "travel-planner-agent",
    "mental-model-coach",
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
    if path.startswith("/tutorials"):
        return "tutorials"
    return "default"


_TUTORIAL_CATEGORIES = [
    {"name": "All", "slug": "all"},
    {"name": "Getting Started", "slug": "getting-started"},
    {"name": "AI Agents", "slug": "ai-agents"},
    {"name": "RAG & Vector DBs", "slug": "rag-vector-dbs"},
    {"name": "LLMs & Models", "slug": "llms-models"},
    {"name": "Developer Tools", "slug": "developer-tools"},
    {"name": "Video & Audio", "slug": "video-audio"},
]


_HOME_AI_TOOL_ORDER = (
    "pomelli-ai",
    "midjourney",
    "runwayml",
    "cursor",
)


def _home_featured_tools(tools: list[dict]) -> list[dict]:
    by_id = {t.get("id"): t for t in tools if t.get("id")}
    return [by_id[i] for i in _HOME_AI_TOOL_ORDER if i in by_id]


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
            "featured_tools": _home_featured_tools(tools),
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


def agentgpt(request):
    return render(
        request,
        "web/agentgpt.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def google_gemini(request):
    return render(
        request,
        "web/google_gemini.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def perplexity(request):
    return render(
        request,
        "web/perplexity.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def chatgpt(request):
    return render(
        request,
        "web/chatgpt.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def jasper_ai(request):
    return render(
        request,
        "web/jasper_ai.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def copy_ai(request):
    return render(
        request,
        "web/copy_ai.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def elevenlabs(request):
    return render(
        request,
        "web/elevenlabs.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def murf_ai(request):
    return render(
        request,
        "web/murf_ai.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def otter_ai(request):
    return render(
        request,
        "web/otter_ai.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def replit_ai(request):
    return render(
        request,
        "web/replit_ai.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def adcreative_ai(request):
    return render(
        request,
        "web/adcreative_ai.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def claude_ai(request):
    return render(
        request,
        "web/claude_ai.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def codeium(request):
    return render(
        request,
        "web/codeium.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def tabnine(request):
    return render(
        request,
        "web/tabnine.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def langchain(request):
    return render(
        request,
        "web/langchain.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def crewai(request):
    return render(
        request,
        "web/crewai.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def langgraph(request):
    return render(
        request,
        "web/langgraph.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def autogen(request):
    return render(
        request,
        "web/autogen.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def smolagents(request):
    return render(
        request,
        "web/smolagents.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


def openclaw(request):
    return render(
        request,
        "web/openclaw.html",
        {"layout": _layout(request.path), "active_nav": "ai"},
    )


_AI_AGENTS_SERIES = [
    {"number": 2, "title": "What is an AI Agent?", "summary": "Plain-English definition, chatbot vs agent comparison, and real-world analogies.", "url": "tutorial_ai_agents_what_is"},
    {"number": 3, "title": "How AI Agents Work", "summary": "The agent loop — Perceive → Think → Act → Observe → Repeat — broken down step by step.", "url": "tutorial_ai_agents_how_work"},
    {"number": 4, "title": "Core Components", "summary": "The four building blocks: LLM, Tools, Memory, and Planning.", "url": "tutorial_ai_agents_components"},
    {"number": 5, "title": "Types of AI Agents", "summary": "Reflex, ReAct, multi-agent, and autonomous agents — when to use each.", "url": "tutorial_ai_agents_types"},
    {"number": 6, "title": "Agent Frameworks Overview", "summary": "LangChain, CrewAI, AutoGen, Phidata, Swarm — compared in one place.", "url": "tutorial_ai_agents_frameworks"},
    {"number": 7, "title": "Build Your First Agent", "summary": "Write and run a simple research agent in Python from scratch.", "url": "tutorial_ai_agents_build"},
    {"number": 8, "title": "Real-World Use Cases", "summary": "Research, coding, customer support, and data analysis agents with examples.", "url": "tutorial_ai_agents_usecases"},
    {"number": 9, "title": "Limitations & Best Practices", "summary": "What agents get wrong, token costs, security risks, and production checklist.", "url": "tutorial_ai_agents_limitations"},
    {"number": 10, "title": "What to Learn Next", "summary": "Series recap and recommended next tutorials to keep building.", "url": "tutorial_ai_agents_next"},
]


_TUTORIALS = [
    {
        "title": "AI Agents Tutorial",
        "description": "Learn what AI agents are, how they plan and act, and build your first agent from scratch.",
        "category": "AI Agents",
        "difficulty": "Beginner",
        "read_time": 12,
        "icon": "🤖",
        "icon_gradient": "from-emerald-500/40 via-teal-400/20 to-cyan-400/25",
        "url": "/tutorials/ai-agents/introduction/",
    },
    {
        "title": "LangChain Tutorial",
        "description": "Build LLM-powered apps with chains, agents, and RAG pipelines using LangChain.",
        "category": "AI Agents",
        "difficulty": "Intermediate",
        "read_time": 18,
        "icon": "🔗",
        "icon_gradient": "from-violet-500/40 via-purple-400/20 to-fuchsia-400/25",
        "url": "/tutorials/langchain/introduction/",
    },
    {
        "title": "RAG Pipeline Tutorial",
        "description": "Connect an LLM to your own documents using retrieval-augmented generation.",
        "category": "RAG & Vector DBs",
        "difficulty": "Intermediate",
        "read_time": 15,
        "icon": "📚",
        "icon_gradient": "from-amber-500/40 via-orange-400/20 to-yellow-400/25",
        "url": "#",
    },
    {
        "title": "Prompt Engineering",
        "description": "Master the techniques that get better, more reliable outputs from any LLM.",
        "category": "Getting Started",
        "difficulty": "Beginner",
        "read_time": 10,
        "icon": "✍️",
        "icon_gradient": "from-sky-500/40 via-blue-400/20 to-indigo-400/25",
        "url": "/tutorials/prompt-engineering/introduction/",
    },
    {
        "title": "Run LLMs Locally",
        "description": "Use Ollama to run Llama, Mistral, and other models on your own machine for free.",
        "category": "LLMs & Models",
        "difficulty": "Beginner",
        "read_time": 8,
        "icon": "💻",
        "icon_gradient": "from-lime-500/40 via-green-400/20 to-emerald-400/25",
        "url": "/tutorials/run-llms-locally/introduction/",
    },
    {
        "title": "Build with CrewAI",
        "description": "Create multi-agent crews where AI roles collaborate to complete complex tasks.",
        "category": "AI Agents",
        "difficulty": "Intermediate",
        "read_time": 20,
        "icon": "👥",
        "icon_gradient": "from-rose-500/40 via-pink-400/20 to-fuchsia-400/25",
        "url": "#",
    },
    {
        "title": "Flowise Crash Course",
        "description": "Build and deploy a RAG chatbot visually using Flowise — no code required.",
        "category": "Developer Tools",
        "difficulty": "Beginner",
        "read_time": 14,
        "icon": "🌊",
        "icon_gradient": "from-cyan-500/40 via-teal-400/20 to-sky-400/25",
        "url": "#",
    },
    {
        "title": "Fine-tune a Llama Model",
        "description": "Fine-tune Meta Llama on your own dataset using LoRA and the Hugging Face ecosystem.",
        "category": "LLMs & Models",
        "difficulty": "Advanced",
        "read_time": 25,
        "icon": "🦙",
        "icon_gradient": "from-orange-500/40 via-amber-400/20 to-yellow-400/25",
        "url": "#",
    },
]


def tutorial_ai_agents_intro(request):
    return render(
        request,
        "web/tutorials/ai_agents/introduction.html",
        {
            "layout": _layout(request.path),
            "active_nav": "tutorials",
            "series_pages": _AI_AGENTS_SERIES,
        },
    )


def tutorial_ai_agents_what_is(request):
    return render(
        request,
        "web/tutorials/ai_agents/what_is_an_ai_agent.html",
        {"layout": _layout(request.path), "active_nav": "tutorials"},
    )


def tutorial_ai_agents_how_work(request):
    return render(
        request,
        "web/tutorials/ai_agents/how_agents_work.html",
        {"layout": _layout(request.path), "active_nav": "tutorials"},
    )


def tutorial_ai_agents_components(request):
    return render(
        request,
        "web/tutorials/ai_agents/core_components.html",
        {"layout": _layout(request.path), "active_nav": "tutorials"},
    )


def tutorial_ai_agents_types(request):
    return render(
        request,
        "web/tutorials/ai_agents/types_of_agents.html",
        {"layout": _layout(request.path), "active_nav": "tutorials"},
    )


def tutorial_ai_agents_frameworks(request):
    return render(
        request,
        "web/tutorials/ai_agents/frameworks.html",
        {"layout": _layout(request.path), "active_nav": "tutorials"},
    )


def tutorial_ai_agents_build(request):
    return render(
        request,
        "web/tutorials/ai_agents/build_your_first_agent.html",
        {"layout": _layout(request.path), "active_nav": "tutorials"},
    )


def tutorial_ai_agents_usecases(request):
    return render(
        request,
        "web/tutorials/ai_agents/use_cases.html",
        {"layout": _layout(request.path), "active_nav": "tutorials"},
    )


def tutorial_ai_agents_limitations(request):
    return render(
        request,
        "web/tutorials/ai_agents/limitations.html",
        {"layout": _layout(request.path), "active_nav": "tutorials"},
    )


def tutorial_ai_agents_next(request):
    return render(
        request,
        "web/tutorials/ai_agents/whats_next.html",
        {"layout": _layout(request.path), "active_nav": "tutorials"},
    )


_LANGCHAIN_SERIES = [
    {"number": 2, "title": "Core Concepts", "summary": "LLM vs Chat Models, Chains vs Agents, LCEL & Runnable interface, LangGraph intro.", "url": "tutorial_langchain_concepts"},
    {"number": 3, "title": "Prompt Templates", "summary": "PromptTemplate, ChatPromptTemplate, few-shot prompts, structured outputs, guardrails.", "url": "tutorial_langchain_prompts"},
    {"number": 4, "title": "Chains & LCEL", "summary": "LLMChain, SequentialChain, and the modern LCEL pipe syntax in depth.", "url": "tutorial_langchain_chains"},
    {"number": 5, "title": "Memory", "summary": "Conversation memory, summary memory, token limits, and when NOT to use memory.", "url": "tutorial_langchain_memory"},
    {"number": 6, "title": "Tools & Agents", "summary": "Tool vs Agent distinction, ReAct flow, web search and calculator tool examples.", "url": "tutorial_langchain_agents"},
    {"number": 7, "title": "RAG Pipeline", "summary": "Chunking, embeddings, FAISS, similarity search, retrieval strategies, common mistakes.", "url": "tutorial_langchain_rag"},
    {"number": 8, "title": "Build a RAG Chatbot", "summary": "Hands-on: full document Q&A chatbot — load, chunk, embed, store, retrieve, answer.", "url": "tutorial_langchain_build"},
]


def tutorial_langchain_intro(request):
    return render(
        request,
        "web/tutorials/langchain/introduction.html",
        {
            "layout": _layout(request.path),
            "active_nav": "tutorials",
            "series_pages": _LANGCHAIN_SERIES,
        },
    )


def tutorial_langchain_concepts(request):
    return render(request, "web/tutorials/langchain/core_concepts.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_langchain_prompts(request):
    return render(request, "web/tutorials/langchain/prompt_templates.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_langchain_chains(request):
    return render(request, "web/tutorials/langchain/chains_lcel.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_langchain_memory(request):
    return render(request, "web/tutorials/langchain/memory.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_langchain_agents(request):
    return render(request, "web/tutorials/langchain/tools_agents.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_langchain_rag(request):
    return render(request, "web/tutorials/langchain/rag_pipeline.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_langchain_build(request):
    return render(request, "web/tutorials/langchain/build_rag_chatbot.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


_PROMPT_ENG_SERIES = [
    {"number": 2, "title": "Prompt Anatomy", "summary": "System/user/assistant roles, tokens, temperature, top-p, and context window limits.", "url": "tutorial_pe_anatomy"},
    {"number": 3, "title": "Zero-shot & Few-shot", "summary": "Zero-shot prompting, few-shot examples, how many to include, and formatting them well.", "url": "tutorial_pe_zeroshot"},
    {"number": 4, "title": "Chain-of-Thought", "summary": "When CoT helps vs hurts, hidden vs explicit reasoning, and programmatic alternatives.", "url": "tutorial_pe_cot"},
    {"number": 5, "title": "Role & Persona Prompting", "summary": "Personas, expert framing, tone control, and audience targeting.", "url": "tutorial_pe_role"},
    {"number": 6, "title": "Structured Output Prompting", "summary": "JSON/markdown/tables, schema-in-prompt, and combining with Pydantic validation.", "url": "tutorial_pe_structured"},
    {"number": 7, "title": "Prompt Patterns Library", "summary": "Reusable patterns: Instruction+Context+Format, ReAct, Critic-Refine, Planner→Executor.", "url": "tutorial_pe_patterns"},
    {"number": 8, "title": "Tool Use & Function Calling", "summary": "Function calling concepts, JSON schema → tool calls, tools vs pure prompting.", "url": "tutorial_pe_tools"},
    {"number": 9, "title": "Prompt Security & Guardrails", "summary": "Injection attacks, jailbreaks, data leakage, input sanitization, output validation.", "url": "tutorial_pe_security"},
    {"number": 10, "title": "Prompt Testing & Engineering", "summary": "Test cases, golden datasets, regression testing, accuracy/latency/cost metrics.", "url": "tutorial_pe_testing"},
]


def tutorial_pe_intro(request):
    return render(
        request,
        "web/tutorials/prompt_engineering/introduction.html",
        {
            "layout": _layout(request.path),
            "active_nav": "tutorials",
            "series_pages": _PROMPT_ENG_SERIES,
        },
    )


def tutorial_pe_anatomy(request):
    return render(request, "web/tutorials/prompt_engineering/prompt_anatomy.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_pe_zeroshot(request):
    return render(request, "web/tutorials/prompt_engineering/zero_shot_few_shot.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_pe_cot(request):
    return render(request, "web/tutorials/prompt_engineering/chain_of_thought.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_pe_role(request):
    return render(request, "web/tutorials/prompt_engineering/role_persona.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_pe_structured(request):
    return render(request, "web/tutorials/prompt_engineering/structured_output.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_pe_patterns(request):
    return render(request, "web/tutorials/prompt_engineering/prompt_patterns.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_pe_tools(request):
    return render(request, "web/tutorials/prompt_engineering/tool_use.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_pe_security(request):
    return render(request, "web/tutorials/prompt_engineering/security_guardrails.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_pe_testing(request):
    return render(request, "web/tutorials/prompt_engineering/testing_engineering.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


_RUN_LLM_SERIES = [
    {"number": 2, "title": "Ollama", "summary": "Install, pull models, ollama run, REST API, and the model library.", "url": "tutorial_rll_ollama"},
    {"number": 3, "title": "Open-source Model Landscape", "summary": "Llama 3, Mistral, Gemma, Phi-3, Qwen — size vs quality tradeoffs and use-case guide.", "url": "tutorial_rll_models"},
    {"number": 4, "title": "Model Selection Strategy", "summary": "Chat vs embedding vs coding models, small vs large tradeoffs, when local is NOT enough.", "url": "tutorial_rll_selection"},
    {"number": 5, "title": "LM Studio", "summary": "GUI setup, model download, local OpenAI-compatible server — ideal for non-technical users.", "url": "tutorial_rll_lmstudio"},
    {"number": 6, "title": "Quantization & Performance", "summary": "GGUF vs GPTQ, Q4 vs Q8, GPU offloading, and CPU-only performance tips.", "url": "tutorial_rll_quantization"},
    {"number": 7, "title": "Limitations of Local Models", "summary": "Hallucination rates, weak reasoning in small models, context limits, maintenance overhead.", "url": "tutorial_rll_limitations"},
    {"number": 8, "title": "Local Models with LangChain", "summary": "ChatOllama, OpenAI-compatible endpoint, drop-in replacement for GPT in your chains.", "url": "tutorial_rll_langchain"},
    {"number": 9, "title": "Local RAG Pipeline", "summary": "End-to-end RAG with local embeddings, hybrid search, reranking, and Docker deployment.", "url": "tutorial_rll_rag"},
]


def tutorial_rll_intro(request):
    return render(
        request,
        "web/tutorials/run_llms_locally/introduction.html",
        {
            "layout": _layout(request.path),
            "active_nav": "tutorials",
            "series_pages": _RUN_LLM_SERIES,
        },
    )


def tutorial_rll_ollama(request):
    return render(request, "web/tutorials/run_llms_locally/ollama.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_rll_models(request):
    return render(request, "web/tutorials/run_llms_locally/model_landscape.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_rll_selection(request):
    return render(request, "web/tutorials/run_llms_locally/model_selection.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_rll_lmstudio(request):
    return render(request, "web/tutorials/run_llms_locally/lm_studio.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_rll_quantization(request):
    return render(request, "web/tutorials/run_llms_locally/quantization.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_rll_limitations(request):
    return render(request, "web/tutorials/run_llms_locally/limitations.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_rll_langchain(request):
    return render(request, "web/tutorials/run_llms_locally/langchain_local.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorial_rll_rag(request):
    return render(request, "web/tutorials/run_llms_locally/local_rag.html", {"layout": _layout(request.path), "active_nav": "tutorials"})


def tutorials(request):
    active_category = (request.GET.get("category") or "all").lower()
    if active_category == "all":
        filtered = _TUTORIALS
    else:
        cat_map = {c["slug"]: c["name"] for c in _TUTORIAL_CATEGORIES}
        cat_name = cat_map.get(active_category, "")
        filtered = [t for t in _TUTORIALS if t["category"] == cat_name]
    return render(
        request,
        "web/tutorials.html",
        {
            "layout": _layout(request.path),
            "active_nav": "tutorials",
            "categories": _TUTORIAL_CATEGORIES,
            "active_category": active_category,
            "tutorials": filtered,
        },
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
