import os
from datetime import datetime

import feedparser
import requests
import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


DEFAULT_RSS_URL = "https://techcrunch.com/tag/artificial-intelligence/feed/"
DEFAULT_MODEL = "openai/gpt-oss-120b:free"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
)


st.set_page_config(
    page_title="Intelligent AI News Scraper & Generator | Neon Intelligence Pipeline",
    page_icon="📝",
    layout="wide",
)


def init_state() -> None:
    defaults = {
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "model": DEFAULT_MODEL,
        "temperature": 0.7,
        "rss_url": DEFAULT_RSS_URL,
        "max_articles": 5,
        "articles": [],
        "research": "",
        "trends": "",
        "selected_topic": "",
        "post": "",
        "optimized_post": "",
        "history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_llm() -> ChatOpenAI:
    api_key = st.session_state.api_key.strip()
    if not api_key:
        st.error("Enter your OpenRouter API key in the sidebar first.")
        st.stop()

    return ChatOpenAI(
        model=st.session_state.model,
        temperature=st.session_state.temperature,
        api_key=api_key,
        base_url=DEFAULT_BASE_URL,
    )


def fetch_headlines(rss_url: str, max_articles: int) -> list[str]:
    response = requests.get(
        rss_url,
        headers={"User-Agent": USER_AGENT},
        timeout=20,
    )
    response.raise_for_status()
    feed = feedparser.parse(response.content)
    headlines = [
        entry.get("title", "").strip()
        for entry in feed.entries
        if entry.get("title")
    ]
    return headlines[:max_articles]


def run_prompt(llm: ChatOpenAI, template: str, values: dict) -> str:
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke(values)
    return result.content.strip()


def render_pipeline_steps(active_step: int = -1) -> None:
    steps = [
        ("Fetching", "🛰️"),
        ("Research", "🔍"),
        ("Trends", "📈"),
        ("Writing", "✍️"),
        ("Optimize", "✨"),
    ]

    chips = []
    for index, (label, icon) in enumerate(steps):
        if index < active_step:
            chips.append(f'<div class="step-chip done">{icon} {label}</div>')
        elif index == active_step:
            chips.append(f'<div class="step-chip active">{icon} {label}</div>')
        else:
            chips.append(f'<div class="step-chip">{icon} {label}</div>')

    progress_value = max(0, min(100, int(((active_step + 1) / 5) * 100))) if active_step >= 0 else 0

    st.markdown(
        f"""
        <div class="pipeline-wrap">
            <div class="pipeline-title">AI Pipeline Status</div>
            <div class="step-grid">{''.join(chips)}</div>
            <div class="pipeline-meter">
                <div class="pipeline-meter-fill" style="width:{progress_value}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


init_state()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #0E1117;
        --card: rgba(17, 24, 39, 0.58);
        --card-strong: rgba(17, 24, 39, 0.8);
        --text: #E6F6FF;
        --muted: #8BA6B9;
        --line: rgba(34,211,238,0.45);
        --grad-start: #22D3EE;
        --grad-end: #A855F7;
        --shadow: 0 22px 45px rgba(0, 0, 0, 0.45);
        --glow: 0 0 0 1px rgba(34,211,238,0.45), 0 0 32px rgba(168,85,247,0.25);
        --radius-xl: 20px;
        --radius-lg: 16px;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: var(--text);
    }

    p, li, label, .stMarkdown, .stCaption {
        line-height: 1.55;
        letter-spacing: 0.01em;
    }

    .stApp {
        background:
            radial-gradient(1200px 500px at 10% -20%, rgba(168,85,247,0.26), transparent 50%),
            radial-gradient(900px 500px at 90% -25%, rgba(34,211,238,0.22), transparent 50%),
            linear-gradient(180deg, rgba(8, 13, 23, 0.98), rgba(14, 17, 23, 0.98)),
            var(--bg);
        color: var(--text);
    }

    .ambient-layer {
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
    }

    .ambient-orb {
        position: absolute;
        border-radius: 999px;
        filter: blur(70px);
        opacity: 0.34;
    }

    .ambient-orb.a {
        width: 280px;
        height: 280px;
        top: 12%;
        left: -60px;
        background: #A855F7;
        animation: drift 10s ease-in-out infinite;
    }

    .ambient-orb.b {
        width: 360px;
        height: 360px;
        top: 58%;
        right: -80px;
        background: #22D3EE;
        animation: drift 14s ease-in-out infinite reverse;
    }

    .main .block-container {
        max-width: 1240px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10,15,28,0.96) 0%, rgba(12,19,35,0.98) 100%);
        border-right: 1px solid rgba(34,211,238,0.2);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.4rem;
        padding-bottom: 1.4rem;
    }

    .sidebar-panel {
        background: var(--card);
        border: 1px solid rgba(34,211,238,0.22);
        border-radius: var(--radius-xl);
        padding: 1rem 1rem 0.7rem 1rem;
        backdrop-filter: blur(12px);
        box-shadow: var(--shadow);
    }

    .hero {
        position: relative;
        overflow: hidden;
        border-radius: 24px;
        border: 1px solid rgba(34,211,238,0.24);
        background:
            radial-gradient(500px 220px at 100% -50%, rgba(168,85,247,0.3), transparent 50%),
            linear-gradient(140deg, rgba(34,211,238,0.12), rgba(168,85,247,0.14));
        padding: 1.55rem 1.55rem 1.45rem 1.55rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.25rem;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 1rem;
        align-items: end;
    }

    .hero-side {
        text-align: right;
        font-size: 0.82rem;
        color: var(--muted);
    }

    .hero-kpi {
        font-size: 1.3rem;
        color: #67E8F9;
        font-weight: 700;
        line-height: 1;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(34,211,238,0.12);
        color: var(--text);
        border: 1px solid rgba(34,211,238,0.34);
        border-radius: 999px;
        padding: 0.25rem 0.65rem;
        font-size: 0.78rem;
        margin-bottom: 0.85rem;
    }

    .hero-title {
        margin: 0;
        font-size: clamp(1.75rem, 4vw, 2.7rem);
        font-weight: 800;
        line-height: 1.08;
        background: linear-gradient(90deg, #22D3EE, #A855F7);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        margin-top: 0.6rem;
        color: var(--muted);
        font-size: 1rem;
        max-width: 65ch;
    }

    .gradient-sep {
        height: 1px;
        background: linear-gradient(90deg, rgba(168,85,247,0), rgba(34,211,238,0.95), rgba(168,85,247,0));
        margin: 1rem 0 1.2rem 0;
    }

    .glass-card {
        background: var(--card);
        border: 1px solid rgba(34,211,238,0.18);
        border-radius: var(--radius-xl);
        padding: 1.2rem;
        backdrop-filter: blur(14px);
        box-shadow: var(--shadow);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }

    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(34,211,238,0.48);
        box-shadow: 0 24px 55px rgba(0,0,0,0.52), 0 0 0 1px rgba(168,85,247,0.28);
    }

    .section-title {
        font-size: 1.04rem;
        font-weight: 700;
        margin-bottom: 0.95rem;
        color: var(--text);
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.7rem;
        margin-bottom: 1rem;
    }

    .stat-card {
        background: rgba(17, 24, 39, 0.65);
        border: 1px solid rgba(34,211,238,0.2);
        border-radius: 14px;
        padding: 0.75rem 0.78rem;
    }

    .stat-label {
        color: var(--muted);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.28rem;
    }

    .stat-value {
        font-size: 1rem;
        font-weight: 700;
        color: #CFFAFE;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .stTextInput > div > div,
    .stTextArea > div > div,
    .stSelectbox > div > div,
    .stNumberInput > div > div,
    .stSlider {
        border-radius: 14px !important;
    }

    .api-highlight [data-baseweb="input"] {
        box-shadow: var(--glow);
        border-radius: 14px;
    }

    .stButton > button {
        border-radius: 14px;
        border: 1px solid rgba(34,211,238,0.28);
        transition: all 0.22s ease;
        min-height: 48px;
        font-weight: 600;
        letter-spacing: 0.01em;
        font-size: 0.95rem;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        border-color: rgba(34,211,238,0.68);
        box-shadow: 0 14px 30px rgba(34,211,238,0.34);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #22D3EE, #A855F7);
        border: none;
        color: #04070F;
        box-shadow: 0 16px 30px rgba(34,211,238,0.36);
    }

    .stButton > button:focus-visible {
        outline: none;
        box-shadow: 0 0 0 2px rgba(8,13,23,0.9), 0 0 0 4px rgba(34,211,238,0.55);
    }

    .result-badge {
        display: inline-flex;
        gap: 0.35rem;
        align-items: center;
        font-size: 0.78rem;
        padding: 0.24rem 0.58rem;
        border: 1px solid rgba(34,211,238,0.28);
        border-radius: 999px;
        background: rgba(34,211,238,0.1);
        margin-bottom: 0.8rem;
    }

    .result-ready {
        border: 1px solid rgba(34,211,238,0.48);
        box-shadow: 0 0 0 1px rgba(34,211,238,0.28), 0 0 26px rgba(168,85,247,0.24);
        animation: fadeUp 0.5s ease;
    }

    .skeleton {
        height: 220px;
        border-radius: 16px;
        background: linear-gradient(90deg, rgba(255,255,255,0.03), rgba(255,255,255,0.10), rgba(255,255,255,0.03));
        background-size: 200% 100%;
        animation: shimmer 1.8s infinite linear;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .pipeline-wrap {
        background: var(--card);
        border: 1px solid rgba(34,211,238,0.2);
        border-radius: var(--radius-lg);
        padding: 0.9rem;
        margin-bottom: 0.8rem;
    }

    .pipeline-meter {
        height: 7px;
        margin-top: 0.58rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.07);
        overflow: hidden;
    }

    .pipeline-meter-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #22D3EE, #A855F7);
        box-shadow: 0 0 18px rgba(34,211,238,0.45);
        transition: width 0.45s ease;
    }

    .pipeline-title {
        font-weight: 650;
        margin-bottom: 0.65rem;
        color: var(--muted);
        font-size: 0.86rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .step-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 0.42rem;
    }

    .step-chip {
        background: rgba(15,23,42,0.6);
        border: 1px solid rgba(34,211,238,0.18);
        border-radius: 11px;
        font-size: 0.78rem;
        padding: 0.42rem 0.45rem;
        text-align: center;
        color: var(--muted);
    }

    .step-chip.done {
        color: #BAE6FD;
        border-color: rgba(34,211,238,0.36);
    }

    .step-chip.active {
        color: #fff;
        border-color: rgba(34,211,238,0.75);
        background: linear-gradient(90deg, rgba(34,211,238,0.26), rgba(168,85,247,0.24));
        box-shadow: 0 0 0 1px rgba(168,85,247,0.34);
    }

    .timeline-item {
        background: rgba(17, 24, 39, 0.62);
        border: 1px solid rgba(34,211,238,0.18);
        border-left: 3px solid rgba(34,211,238,0.9);
        border-radius: 12px;
        padding: 0.7rem 0.8rem;
        margin-bottom: 0.55rem;
    }

    .timeline-item:hover {
        border-left-color: #A855F7;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.24);
    }

    .timeline-time {
        font-size: 0.75rem;
        color: var(--muted);
        margin-bottom: 0.2rem;
    }

    .timeline-topic {
        font-size: 0.9rem;
        color: var(--text);
    }

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0.4rem;
        background: rgba(17, 24, 39, 0.72);
        border: 1px solid rgba(34,211,238,0.2);
        border-radius: 12px;
        padding: 0.3rem;
    }

    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 9px;
        color: var(--muted);
        transition: all 0.2s ease;
        padding: 0.5rem 0.8rem;
    }

    [data-testid="stTabs"] [aria-selected="true"] {
        background: linear-gradient(90deg, rgba(34,211,238,0.24), rgba(168,85,247,0.24));
        color: var(--text) !important;
    }

    .tab-card {
        background: var(--card);
        border: 1px solid rgba(34,211,238,0.16);
        border-radius: 14px;
        padding: 0.9rem;
        margin-top: 0.75rem;
    }

    .tiny-note {
        color: var(--muted);
        font-size: 0.8rem;
        margin-top: 0.45rem;
    }

    @keyframes shimmer {
        from { background-position: 100% 0; }
        to { background-position: -100% 0; }
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes drift {
        0% { transform: translateY(0px) translateX(0px); }
        50% { transform: translateY(-10px) translateX(8px); }
        100% { transform: translateY(0px) translateX(0px); }
    }

    @media (max-width: 1100px) {
        .hero-grid {
            grid-template-columns: 1fr;
        }
        .hero-side {
            text-align: left;
        }
        .step-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .stats-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    @media (max-width: 760px) {
        .main .block-container {
            padding-top: 1rem;
            padding-left: 0.85rem;
            padding-right: 0.85rem;
            padding-bottom: 1.8rem;
        }
        .hero {
            padding: 1rem 0.95rem;
        }
        .hero-title {
            font-size: clamp(1.45rem, 7vw, 2rem);
        }
        .hero-subtitle {
            font-size: 0.92rem;
        }
        .glass-card {
            padding: 0.9rem;
        }
        .section-title {
            font-size: 0.98rem;
        }
        .stButton > button {
            min-height: 44px;
            font-size: 0.92rem;
        }
        .step-grid {
            grid-template-columns: repeat(1, minmax(0, 1fr));
        }
        .stats-grid {
            grid-template-columns: repeat(1, minmax(0, 1fr));
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="ambient-layer">
        <div class="ambient-orb a"></div>
        <div class="ambient-orb b"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <div class="hero-grid">
            <div>
                <h1 class="hero-title">Intelligent AI News Scraper &amp; Generator</h1>
                <div class="hero-subtitle">
                    Transform live AI news into high-impact, audience-specific content through a neon intelligence pipeline.
                </div>
            </div>
            <div class="hero-side">
                <div>Neural Throughput</div>
                <div class="hero-kpi">99.2%</div>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">Recent Runs</div>
            <div class="stat-value">{len(st.session_state.history)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Headlines Cached</div>
            <div class="stat-value">{len(st.session_state.articles)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Active Model</div>
            <div class="stat-value">{st.session_state.model}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="sidebar-panel">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Control Panel")
    st.caption("Configure model, feed source, and generation behavior.")
    st.markdown('<div class="gradient-sep"></div>', unsafe_allow_html=True)

    st.markdown('<div class="api-highlight">', unsafe_allow_html=True)
    st.session_state.api_key = st.text_input(
        "🔑 OpenRouter API Key",
        type="password",
        value=st.session_state.api_key,
        placeholder="sk-or-v1-...",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.model = st.selectbox(
        "🧠 Model",
        [
            "openai/gpt-oss-120b:free",
            "openai/gpt-4o-mini",
            "meta-llama/llama-3.3-70b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
        ],
        index=0,
    )

    st.session_state.temperature = st.slider("🌡️ Temperature", 0.0, 1.0, 0.7, 0.05)

    st.markdown('<div class="gradient-sep"></div>', unsafe_allow_html=True)

    st.session_state.rss_url = st.text_input("📰 RSS URL", value=st.session_state.rss_url)
    st.session_state.max_articles = st.slider("📌 Number of headlines", 3, 10, st.session_state.max_articles)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="glass-card" style="margin-bottom: 1rem;">
        <div class="section-title">How It Works</div>
        <div style="color:#9CA3AF; line-height:1.7; font-size:0.94rem;">
            1) Fetch AI news headlines from RSS<br>
            2) Research what those headlines are about<br>
            3) Detect trends<br>
            4) Pick the best topic<br>
            5) Write the content<br>
            6) Improve the hook
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧩 Content Inputs</div>', unsafe_allow_html=True)

    content_type_col, audience_col = st.columns(2, gap="medium")
    with content_type_col:
        content_type = st.selectbox(
            "Content format",
            ["LinkedIn Post", "Twitter / X Thread", "Newsletter Blurb", "Blog Intro"],
        )
    with audience_col:
        audience = st.selectbox(
            "Audience",
            ["Tech Enthusiasts", "Developers", "Startup Founders", "General Public"],
        )

    tone_col, _ = st.columns([1, 1], gap="medium")
    with tone_col:
        tone = st.selectbox(
            "Tone",
            ["Professional", "Balanced", "Conversational", "Casual", "Bold"],
            index=1,
        )

    extra_instructions = st.text_area(
        "Extra instructions (optional)",
        placeholder="Example: Keep it short and practical.",
        height=100,
    )

    st.markdown('<div class="gradient-sep"></div>', unsafe_allow_html=True)

    generate = st.button("Generate Content", type="primary", width="stretch")
    clear = st.button("Clear Results", width="stretch")

    st.markdown('</div>', unsafe_allow_html=True)

    if clear:
        for key in ["articles", "research", "trends", "selected_topic", "post", "optimized_post"]:
            st.session_state[key] = [] if key == "articles" else ""
        st.rerun()

with right_col:
    card_class = "glass-card result-ready" if st.session_state.optimized_post else "glass-card"
    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✨ AI Output</div>', unsafe_allow_html=True)

    if st.session_state.optimized_post:
        st.markdown('<div class="result-badge">✅ Crafted for your voice</div>', unsafe_allow_html=True)
        st.success("Content generated successfully.")
        st.text_area("Final content", st.session_state.optimized_post, height=260)
        st.code(st.session_state.optimized_post, language="markdown")
        st.markdown('<div class="tiny-note">Tip: Use the copy icon in the code block to quickly copy the generated result.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="result-badge">⏳ Awaiting generation</div>', unsafe_allow_html=True)
        st.markdown('<div class="skeleton"></div>', unsafe_allow_html=True)
        st.info("Your generated post will appear here.")

    st.markdown('</div>', unsafe_allow_html=True)

if generate:
    llm = get_llm()

    stepper_placeholder = st.empty()

    with st.status("Running content pipeline...", expanded=True) as status:
        try:
            stepper_placeholder.container()
            with stepper_placeholder:
                render_pipeline_steps(active_step=0)

            status.write("Fetching headlines from RSS...")
            articles = fetch_headlines(st.session_state.rss_url, st.session_state.max_articles)
            if not articles:
                raise ValueError("No headlines were found. Try a different RSS URL.")
            st.session_state.articles = articles

            formatted_articles = "\n".join(f"- {article}" for article in articles)

            with stepper_placeholder:
                render_pipeline_steps(active_step=1)
            status.write("Researching headlines...")
            st.session_state.research = run_prompt(
                llm,
                """You are a research agent.
Analyze these AI news headlines:
{articles}

Return:
- Key topics
- Short summaries
- Important keywords

Keep the output clean and easy to read.
""",
                {"articles": formatted_articles},
            )

            with stepper_placeholder:
                render_pipeline_steps(active_step=2)
            status.write("Finding trends...")
            st.session_state.trends = run_prompt(
                llm,
                """You are a trend detection agent.
Based on this research:
{research}

Identify the top 3 trends, why they matter, and which one has the strongest content potential.
""",
                {"research": st.session_state.research},
            )

            with stepper_placeholder:
                render_pipeline_steps(active_step=3)
            status.write("Selecting the best topic...")
            st.session_state.selected_topic = run_prompt(
                llm,
                """You are a content strategist.
Audience: {audience}
Format: {content_type}
Tone: {tone}

From these trends:
{trends}

Pick one best topic and explain why it fits this audience.
""",
                {
                    "audience": audience,
                    "content_type": content_type,
                    "tone": tone,
                    "trends": st.session_state.trends,
                },
            )

            status.write("Writing the post...")
            st.session_state.post = run_prompt(
                llm,
                """You are an expert content writer.
Write a {content_type} for {audience} with a {tone} tone.

Topic:
{topic}

Extra instructions:
{extra}

Requirements:
- Strong opening hook
- Clear explanation
- One practical takeaway
- Short closing CTA
""",
                {
                    "content_type": content_type,
                    "audience": audience,
                    "tone": tone,
                    "topic": st.session_state.selected_topic,
                    "extra": extra_instructions.strip() or "No extra instructions.",
                },
            )

            with stepper_placeholder:
                render_pipeline_steps(active_step=4)
            status.write("Optimizing the hook...")
            st.session_state.optimized_post = run_prompt(
                llm,
                """Improve only the opening 1 to 2 lines of this post so it is more attention-grabbing.

Return the full revised post only.

Post:
{post}
""",
                {"post": st.session_state.post},
            )

            st.session_state.history.append(
                {
                    "time": datetime.now().strftime("%H:%M"),
                    "topic": st.session_state.selected_topic[:80],
                }
            )
            status.update(label="Pipeline complete", state="complete")
            st.rerun()
        except Exception as exc:
            status.update(label=f"Pipeline failed: {exc}", state="error")
            st.error(str(exc))

st.markdown('<div class="gradient-sep"></div>', unsafe_allow_html=True)

tab_final, tab_headlines, tab_research, tab_trends, tab_topic = st.tabs(
    ["✨ Final Post", "🗞️ Headlines", "🔬 Research", "📊 Trends", "🎯 Selected Topic"]
)

with tab_final:
    st.markdown('<div class="tab-card">', unsafe_allow_html=True)
    if st.session_state.optimized_post:
        st.markdown(st.session_state.optimized_post)
    else:
        st.write("No final content yet.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_headlines:
    st.markdown('<div class="tab-card">', unsafe_allow_html=True)
    if st.session_state.articles:
        for index, article in enumerate(st.session_state.articles, start=1):
            st.write(f"{index}. {article}")
    else:
        st.write("No headlines yet.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_research:
    st.markdown('<div class="tab-card">', unsafe_allow_html=True)
    st.write(st.session_state.research or "No research yet.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_trends:
    st.markdown('<div class="tab-card">', unsafe_allow_html=True)
    st.write(st.session_state.trends or "No trends yet.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_topic:
    st.markdown('<div class="tab-card">', unsafe_allow_html=True)
    st.write(st.session_state.selected_topic or "No topic selected yet.")
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.history:
    st.markdown('<div class="gradient-sep"></div>', unsafe_allow_html=True)
    st.markdown("### 🕒 Recent Runs")
    for item in reversed(st.session_state.history[-5:]):
        st.markdown(
            f"""
            <div class="timeline-item">
                <div class="timeline-time">{item['time']}</div>
                <div class="timeline-topic">{item['topic']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
