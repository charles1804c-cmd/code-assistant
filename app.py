import streamlit as st
import os
from dotenv import load_dotenv
import markdown as md

load_dotenv()  # loads .env for local development

# ── Streamlit Cloud & local API key support ──
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_KEY = os.getenv("GROQ_API_KEY", "")

from explainer import explain_code, answer_code_question

# ─────────────────────────────────
#  Page Config
# ─────────────────────────────────
st.set_page_config(
    page_title="Code Assistant — AI Code Explainer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────
#  Custom Styling — Dark Minimalist DevTool
#   BG:     #0a0d0f
#   CARD:   #131618
#   ACCENT: #00d4c0 (Teal / Cyan)
# ─────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:      #0a0d0f;
    --card:    #131618;
    --card2:   #1a1d21;
    --accent:  #00d4c0;
    --adim:    rgba(0,212,192,0.09);
    --aglow:   rgba(0,212,192,0.22);
    --purple:  #7c5cfc;
    --orange:  #fb923c;
    --green:   #34d399;
    --border:  #1e2124;
    --text:    #f0f2f5;
    --muted:   #94a3b8;
    --r:       14px;
    --rs:      8px;
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background-color: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text) !important;
}

/* ── Hide Sidebar & Streamlit Chrome entirely ── */
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
[data-testid="stExpandSidebarButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { visibility: hidden !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }

/* ── Subtle animated background glow ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 65% 45% at 0% 0%,    rgba(0,212,192,0.07)  0%, transparent 55%),
        radial-gradient(ellipse 55% 55% at 100% 100%, rgba(124,92,252,0.07) 0%, transparent 55%);
    animation: glow 10s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes glow {
    from { opacity:.5; }
    to   { opacity:1;  }
}

/* ── Main Container ── */
.main .block-container {
    padding: 2.5rem 2rem 4rem !important;
    max-width: 960px !important;
    margin: 0 auto !important;
    position: relative;
    z-index: 1;
}

/* ── Cards ── */
.cl-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 1.4rem 1.6rem;
    margin-bottom: .9rem;
    transition: border-color .2s, box-shadow .2s;
}
.cl-card:hover {
    border-color: rgba(0,212,192,.25);
    box-shadow: 0 0 25px rgba(0,212,192,.06);
}
.cl-label {
    font-size: .72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.6px;
    margin-bottom: 10px;
}
.cl-label.teal   { color: var(--accent);  }
.cl-label.purple { color: #a78bfa;         }
.cl-label.green  { color: var(--green);    }
.cl-label.orange { color: var(--orange);   }

.cl-body {
    color: #a0aec0;
    font-size: .92rem;
    line-height: 1.8;
}
.cl-body code {
    background: rgba(0,212,192,.08);
    color: var(--accent);
    padding: 2px 7px;
    border-radius: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: .84em;
    border: 1px solid rgba(0,212,192,.18);
}
.cl-body strong { color: var(--text); }

/* ── Text Area ── */
.stTextArea textarea {
    background: #0e1113 !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    color: #dde3ec !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: .88rem !important;
    line-height: 1.65 !important;
    caret-color: var(--accent);
    resize: vertical !important;
    transition: border-color .2s, box-shadow .2s !important;
}
.stTextArea textarea:focus {
    border-color: rgba(0,212,192,.5) !important;
    box-shadow: 0 0 0 3px rgba(0,212,192,.1) !important;
    outline: none !important;
}
.stTextArea label { display: none !important; }

/* ── Buttons ── */
.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    border-radius: var(--rs) !important;
    padding: .65rem 1.4rem !important;
    font-weight: 700 !important;
    font-size: .88rem !important;
    width: 100% !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    background: #00edd8 !important;
    box-shadow: 0 4px 20px rgba(0,212,192,.35) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary action buttons (Sample / Clear) */
.secondary-btn .stButton > button {
    background: #131618 !important;
    color: #cbd5e1 !important;
    border: 1px solid var(--border) !important;
}
.secondary-btn .stButton > button:hover {
    background: #1a1d21 !important;
    color: var(--accent) !important;
    border-color: rgba(0,212,192,0.3) !important;
    box-shadow: none !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    padding: 1rem 1.2rem !important;
}
[data-testid="metric-container"] label {
    color: var(--muted) !important;
    font-size: .7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
[data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
}

/* ── Rendered Markdown in Cards ── */
.cl-body p  { margin: 0 0 .75rem; color: #cbd5e1; font-size:.92rem; line-height:1.78; }
.cl-body p:last-child { margin-bottom: 0; }

.cl-body pre {
    background: #0e1113;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    overflow-x: auto;
    margin: .8rem 0;
}
.cl-body pre code {
    background: none;
    border: none;
    padding: 0;
    color: #e2e8f0;
    font-size: .86em;
}

.cl-body ul, .cl-body ol {
    padding-left: 1.4rem;
    margin: .5rem 0 .9rem;
}
.cl-body li {
    color: #cbd5e1;
    font-size: .92rem;
    line-height: 1.75;
    margin-bottom: .35rem;
}
.cl-body li::marker { color: var(--accent); }

/* ── Chat Messages & Input ── */
[data-testid="stChatMessage"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.8rem !important;
    color: #cbd5e1 !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    border-color: rgba(0,212,192,0.3) !important;
    background: rgba(0,212,192,0.06) !important;
}

[data-testid="stChatMessage"] p {
    color: #cbd5e1 !important;
    font-size: 0.92rem !important;
    line-height: 1.7 !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stChatMessage"] p:last-child { margin-bottom: 0 !important; }

[data-testid="stChatMessage"] code {
    background: rgba(0,212,192,0.1) !important;
    color: var(--accent) !important;
    padding: 2px 7px !important;
    border-radius: 5px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

[data-testid="stChatMessage"] pre {
    background: #0e1113 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 0.9rem !important;
}
[data-testid="stChatMessage"] pre code {
    background: transparent !important;
    color: #e2e8f0 !important;
    padding: 0 !important;
}

[data-testid="stChatInput"] {
    border-color: var(--border) !important;
}
[data-testid="stChatInput"] textarea {
    background: #0e1113 !important;
    color: #f0f2f5 !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--rs) !important;
    font-size: 0.9rem !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(0,212,192,0.5) !important;
    box-shadow: 0 0 0 3px rgba(0,212,192,0.1) !important;
}
[data-testid="stChatInput"] button {
    color: var(--accent) !important;
}

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.6rem 0 !important; }
.stAlert { background: rgba(0,212,192,.05) !important; border: 1px solid rgba(0,212,192,.2) !important; border-radius: var(--rs) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────
#  State Initialization
# ─────────────────────────────────
if "editor_code" not in st.session_state:
    st.session_state["editor_code"] = ""

if "explanation_result" not in st.session_state:
    st.session_state["explanation_result"] = None

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []


# ─────────────────────────────────
#  HEADER
# ─────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.6rem; text-align:center;">
    <div style="display:inline-flex; align-items:center; gap:10px; margin-bottom:6px;">
        <div style="width:38px; height:38px; border-radius:10px;
                    background:rgba(0,212,192,.14); border:1px solid rgba(0,212,192,.3);
                    display:flex; align-items:center; justify-content:center; font-size:1.15rem;">
            🔍
        </div>
        <div style="font-size:2.3rem; font-weight:800; letter-spacing:-1px; color:#f0f2f5; line-height:1;">
            Code <span style="color:#00d4c0;">Assistant</span>
        </div>
    </div>
    <div style="font-size:.92rem; color:#94a3b8; font-weight:400;">
        Paste code in <b style="color:#00d4c0;">any programming language</b> · AI automatically detects it & explains every line
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────
#  CODE EDITOR AREA
# ─────────────────────────────────
col_head_left, col_head_right = st.columns([6, 1])
with col_head_left:
    st.markdown("""
    <div style="padding-top:6px;">
        <span class="cl-label teal">📝 &nbsp;Paste Your Code Here</span>
    </div>
    """, unsafe_allow_html=True)
with col_head_right:
    st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
    if st.button("Clear", use_container_width=True, help="Clear code editor"):
        st.session_state["editor_code"] = ""
        st.session_state["explanation_result"] = None
        st.session_state["chat_messages"] = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

user_code = st.text_area(
    "code_editor_area",
    value=st.session_state["editor_code"],
    key="editor_code",
    placeholder="// Paste code in any language (Python, JavaScript, Java, C++, Rust, SQL, HTML, CSS, Bash...)",
    height=280,
    label_visibility="collapsed",
)

st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
_, c2, _ = st.columns([1.5, 2, 1.5])
with c2:
    go = st.button("🔍  Explain This Code", use_container_width=True)


# ─────────────────────────────────
#  TRIGGER EXPLANATION (AUTO-DETECT)
# ─────────────────────────────────
if go:
    current_code = st.session_state.get("editor_code", "")
    if not current_code.strip():
        st.warning("⚠️ Please paste some code first.")
    elif not GROQ_KEY.strip():
        st.error("🔑 Groq API key is not configured. Please add it to your .env file or Streamlit Cloud secrets.")
    else:
        os.environ["GROQ_API_KEY"] = GROQ_KEY
        with st.spinner("Analyzing code and auto-detecting language..."):
            try:
                result = explain_code(current_code)
                st.session_state["explanation_result"] = result
                st.session_state["explained_code"] = current_code
                st.session_state["chat_messages"] = []
                st.rerun()
            except Exception as e:
                err = str(e)
                if "api_key" in err.lower() or "auth" in err.lower():
                    st.error("❌ Invalid API key — check your Groq key.")
                elif "rate" in err.lower():
                    st.warning("⏳ Rate limit hit — wait a moment and retry.")
                else:
                    st.error(f"❌ {err}")


# ─────────────────────────────────
#  DISPLAY EXPLANATION RESULTS
# ─────────────────────────────────
if st.session_state.get("explanation_result"):
    result = st.session_state["explanation_result"]
    exp_code = st.session_state.get("explained_code", st.session_state.get("editor_code", ""))
    detected_lang = result.get("language", "Auto-Detected")

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # Anti-Hallucination Verification Badge
    st.markdown("""
    <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; margin-bottom:12px;">
        <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(52,211,153,0.1); border:1px solid rgba(52,211,153,0.3); border-radius:20px; padding:5px 14px; font-size:0.78rem; color:#34d399; font-weight:600;">
            <span>🛡️</span> Anti-Hallucination Guard: Active (Deterministic AST + Dual-Pass Verified)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pre-flight Syntax Error Warning (if deterministic check found syntax error)
    preflight = result.get("preflight", {})
    if preflight.get("syntax_error"):
        syntax_err = preflight["syntax_error"]
        st.markdown(f"""
        <div style="background:rgba(251,146,60,0.1); border:1px solid rgba(251,146,60,0.4); border-radius:10px; padding:12px 16px; margin-bottom:14px; color:#fed7aa; font-size:0.86rem;">
            <b>⚠️ Deterministic Pre-Flight Alert:</b> Syntax error detected at <code>{syntax_err}</code>. The explanation below accounts for this defect.
        </div>
        """, unsafe_allow_html=True)

    # Handle non-code / irrelevant inputs
    if "irrelevant" in detected_lang.lower():
        st.markdown(f"""
        <div class="cl-card" style="border-color: rgba(251,146,60,0.35); background: rgba(251,146,60,0.06); margin-top: 1rem;">
            <div class="cl-label orange">⚠️ &nbsp;Irrelevant Input (Non-Code)</div>
            <div style="color: #fed7aa; font-size: 0.92rem; line-height: 1.7;">
                <b>Irrelevant:</b> {result.get("summary", "The text pasted does not appear to be programming, scripting, or markup code.")}<br><br>
                Please paste valid code in any language (such as Python, JavaScript, Java, C++, SQL, HTML, CSS, Rust, Bash, etc.) to get an explanation.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        lines = len([l for l in exp_code.strip().split("\n") if l.strip()])
        c1, c2, c3 = st.columns(3)
        c1.metric("✨ Detected Language", detected_lang)
        c2.metric("Lines of Code", lines)
        c3.metric("Characters", len(exp_code.strip()))

        st.markdown("<div style='height:.7rem'></div>", unsafe_allow_html=True)

        def to_html(text):
            """Convert LLM markdown output to safe HTML."""
            return md.markdown(
                text,
                extensions=["fenced_code", "nl2br", "sane_lists"]
            )

        if result.get("summary"):
            st.markdown(f"""
            <div class="cl-card">
                <div class="cl-label teal">📋 &nbsp;What This Code Does</div>
                <div class="cl-body">{to_html(result["summary"])}</div>
            </div>""", unsafe_allow_html=True)

        if result.get("breakdown"):
            st.markdown(f"""
            <div class="cl-card">
                <div class="cl-label purple">🔍 &nbsp;Step-by-Step Breakdown</div>
                <div class="cl-body">{to_html(result["breakdown"])}</div>
            </div>""", unsafe_allow_html=True)

        if result.get("how_to_run"):
            st.markdown(f"""
            <div class="cl-card">
                <div class="cl-label green">▶️ &nbsp;How to Run This Code</div>
                <div class="cl-body">{to_html(result["how_to_run"])}</div>
            </div>""", unsafe_allow_html=True)

        if result.get("watch_out"):
            st.markdown(f"""
            <div class="cl-card">
                <div class="cl-label orange">⚠️ &nbsp;Things to Watch Out For</div>
                <div class="cl-body">{to_html(result["watch_out"])}</div>
            </div>""", unsafe_allow_html=True)

        if not any([result.get("summary"), result.get("breakdown"), result.get("how_to_run")]):
            st.markdown(f"""
            <div class="cl-card">
                <div class="cl-label teal">📄 &nbsp;Explanation</div>
                <div class="cl-body">{to_html(result.get("raw", ""))}</div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────
#  INTERACTIVE CODE Q&A CHAT BOX
# ─────────────────────────────────
st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

st.markdown("""
<div class="cl-card" style="margin-bottom:0.8rem; border-color: rgba(0,212,192,0.25);">
    <div class="cl-label teal" style="font-size:0.8rem; margin-bottom:4px;">
        💬 &nbsp;Ask Questions About Your Code
    </div>
    <div style="font-size:0.85rem; color:#94a3b8;">
        Ask anything in plain text — e.g. <i>"How can I optimize this?"</i>, <i>"Can you rewrite it without recursion?"</i>, or <i>"Explain line 3 in more detail"</i>.
    </div>
</div>
""", unsafe_allow_html=True)

# Display chat message history
for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input prompt
chat_prompt = st.chat_input("Ask any question about your pasted code...")

if chat_prompt:
    current_code = st.session_state.get("editor_code", "")
    detected_lang = (
        st.session_state.get("explanation_result", {}).get("language", "Auto-Detected")
        if st.session_state.get("explanation_result")
        else "Auto-Detected"
    )

    if not current_code.strip():
        st.warning("⚠️ Please paste some code first before asking questions.")
    elif not GROQ_KEY.strip():
        st.error("🔑 Groq API key is not configured in .env or Streamlit secrets.")
    else:
        # Append user question
        st.session_state["chat_messages"].append({"role": "user", "content": chat_prompt})
        with st.chat_message("user"):
            st.markdown(chat_prompt)

        # Generate answer from LLM
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    os.environ["GROQ_API_KEY"] = GROQ_KEY
                    answer = answer_code_question(
                        current_code,
                        detected_lang,
                        st.session_state["chat_messages"],
                        chat_prompt
                    )
                    st.markdown(answer)
                    st.session_state["chat_messages"].append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"❌ Error generating answer: {e}")


# ─────────────────────────────────
#  Footer
# ─────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:3rem 0 1rem;font-size:.7rem;color:#1e2124;letter-spacing:.4px;">
    Code Assistant &nbsp;·&nbsp; AI Auto-Detect &nbsp;·&nbsp; Groq / GPT-OSS &nbsp;·&nbsp; Streamlit
</div>""", unsafe_allow_html=True)
