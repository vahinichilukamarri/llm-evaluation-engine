import streamlit as st
import time
import json
import plotly.graph_objects as go

# ---------------------------------------------------------
# IMPORT BACKEND SERVICES
# ---------------------------------------------------------
from app.services.generator import generate_multiple_responses
from app.services.evaluator import evaluate_multiple_responses
from app.services.comparator import rank_responses, get_best_response
from app.services.judge import compare_responses
from app.services.improver import improve_and_evaluate

# Configure page
st.set_page_config(
    page_title="EvalEngine | Precision AI Evaluation",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CUSTOM INJECTED CSS FOR PREMIUM SAAS LOOK & ANIMATIONS
# ---------------------------------------------------------
custom_css = """
<style>
/* Base Fonts & Typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #f8fafc;
}

code {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Hide default streamlit UI */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Animated Gradient Background */
.stApp {
    background: linear-gradient(-45deg, #09090b, #18181b, #0f172a, #111827);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Glassmorphism Classes */
.glass-panel {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 24px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-panel:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.15);
}

.glass-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 16px;
    padding: 24px;
    height: 100%;
    transition: all 0.3s ease;
}

.glass-card:hover {
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.2);
    border-color: rgba(99, 102, 241, 0.4);
}

/* Hero Section */
.hero-wrapper {
    text-align: center;
    padding: 6rem 0 4rem 0;
    position: relative;
    z-index: 10;
}

.hero-title {
    font-size: 5.5rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 50%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.5rem;
}

.hero-subtitle {
    font-size: 1.5rem;
    color: #94a3b8;
    max-width: 800px;
    margin: 0 auto;
    font-weight: 400;
    line-height: 1.6;
}

/* Typography styles */
.section-heading {
    font-size: 2.25rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 2rem;
    text-align: center;
    letter-spacing: -0.01em;
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: inline-block;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.05);
}

.card-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 0.75rem;
}

.card-text {
    color: #94a3b8;
    font-size: 1rem;
    line-height: 1.6;
}

/* Custom Metric Display */
[data-testid="stMetricValue"] {
    font-size: 3rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #34d399, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
[data-testid="stMetricLabel"] {
    font-size: 1.1rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94a3b8;
}

/* Premium Button Styling */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    border: none;
    padding: 0.875rem 2.5rem;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 1.125rem;
    letter-spacing: 0.025em;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3), inset 0 1px 0 rgba(255,255,255,0.2);
    width: 100%;
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5), inset 0 1px 0 rgba(255,255,255,0.3);
    background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
}

.stButton > button:active {
    transform: translateY(1px);
}

/* CTA Button Specific (Secondary) */
[key="btn_secondary"] > button {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    box-shadow: none !important;
}
[key="btn_secondary"] > button:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}

/* Badges */
.rank-badge {
    background: linear-gradient(135deg, #fbbf24, #ea580c);
    color: #fff;
    padding: 6px 16px;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 15px;
    box-shadow: 0 4px 15px rgba(234, 88, 12, 0.3);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.tier-badge {
    background: rgba(148, 163, 184, 0.2);
    color: #cbd5e1;
    padding: 6px 16px;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 15px;
}

/* Floating particles CSS */
.particles-bg {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    background-image: 
        radial-gradient(circle at 15% 30%, rgba(99, 102, 241, 0.1) 0%, transparent 40%),
        radial-gradient(circle at 85% 60%, rgba(168, 85, 247, 0.1) 0%, transparent 40%),
        radial-gradient(circle at 50% 10%, rgba(56, 189, 248, 0.05) 0%, transparent 50%);
    animation: pulseGlow 10s ease-in-out infinite alternate;
}

@keyframes pulseGlow {
    0% { opacity: 0.8; }
    100% { opacity: 1.2; }
}

/* Inputs styling overload */
.stTextArea textarea {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 16px !important;
    font-size: 1rem !important;
    transition: all 0.3s ease;
}
.stTextArea textarea:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2) !important;
}

/* Diff Highlight styling (for improvement section) */
.diff-added {
    background-color: rgba(52, 211, 153, 0.2);
    color: #6ee7b7;
    padding: 2px 4px;
    border-radius: 4px;
}
</style>

<!-- Background Element -->
<div class="particles-bg"></div>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# SESSION STATE MANAGEMENT
# ---------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'eval_data' not in st.session_state:
    st.session_state.eval_data = None
if 'improved_data' not in st.session_state:
    st.session_state.improved_data = None
if 'rag_enabled' not in st.session_state:
    st.session_state.rag_enabled = False

def navigate_to(page):
    st.session_state.page = page

# ---------------------------------------------------------
# VISUALIZATION HELPER (PLOTLY RADAR CHART)
# ---------------------------------------------------------
def create_radar_chart(eval_dict):
    """Parses evaluation dictionary to generate a modern radar chart."""
    categories = ['Accuracy', 'Relevance', 'Coherence', 'Logic', 'Safety']
    
    # We attempt to extract numeric values representing these categories
    # The actual keys depend on the evaluator's internal logic, so we do fuzzy matching
    vals = []
    
    mapping = {
        'Accuracy': ['accuracy', 'correctness', 'factual'],
        'Relevance': ['relevance', 'alignment', 'context'],
        'Coherence': ['coherence', 'readability', 'structure'],
        'Logic': ['logic', 'reasoning', 'analytical', 'hallucination_risk'], # hallucination normally bad, we invert if needed
        'Safety': ['safety', 'harmlessness', 'toxicity']
    }
    
    for cat, aliases in mapping.items():
        val = 7.5 # Default baseline if not explicitly found
        for k, v in eval_dict.items():
            if any(alias in k.lower() for alias in aliases) and isinstance(v, (int, float)):
                val = float(v)
                # Ensure 10-point scale
                if val <= 1.0: val *= 10
                # Invert risk metrics
                if 'risk' in k.lower() or 'toxic' in k.lower():
                    val = 10.0 - val
                break
        vals.append(val)
        
    vals.append(vals[0]) # close loop
    radar_categories = categories + [categories[0]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals,
        theta=radar_categories,
        fill='toself',
        fillcolor='rgba(129, 140, 248, 0.4)',
        line=dict(color='#818cf8', width=3),
        name='Metrics',
        marker=dict(size=8, color='#c084fc')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="rgba(255,255,255,0.08)", linecolor="rgba(255,255,255,0)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.08)", linecolor="rgba(255,255,255,0.2)"),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', size=12, family="Inter"),
        margin=dict(l=40, r=40, t=30, b=30),
        height=320
    )
    return fig

# ---------------------------------------------------------
# LANDING PAGE VIEW
# ---------------------------------------------------------
def view_landing():
    # HERO
    st.markdown('<div class="hero-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Can You Trust Your LLM?</div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="hero-subtitle">
    EvalEngine analyzes, compares, and scores AI-generated responses across reliability metrics like relevance and coherence — helping you make informed decisions before trusting LLM outputs.
    </div>
    ''', unsafe_allow_html=True)

    # STATUS BADGE
    st.markdown('''
    <div style="text-align:center; color:#94a3b8; margin-top:1rem;">
    ⚡ Actively Improving — Advanced reliability features under development
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div style="margin-top: 3rem;"></div>', unsafe_allow_html=True)
    
    col_l, col_btn, col_r = st.columns([1, 1, 1])
    with col_btn:
        if st.button("🚀 Let's Get Started"):
            navigate_to('app')
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)  # End Hero
    
    st.markdown('<div style="margin-top: 6rem;"></div>', unsafe_allow_html=True)
    
    # SECTION TITLE
    st.markdown('<div class="section-heading">Current Capabilities & Roadmap</div>', unsafe_allow_html=True)
    
    # ------------------ ROW 1 ------------------
    fcol1, fcol2, fcol3 = st.columns(3)
    
    with fcol1:
        st.markdown('''
        <div class="glass-card">
            <span class="feature-icon">⚖️</span>
            <div class="card-title">Multi-Response Evaluation</div>
            <div class="card-text">
            Compare multiple LLM responses side-by-side and identify the most reliable output using structured scoring.
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
    with fcol2:
        st.markdown('''
        <div class="glass-card">
            <span class="feature-icon">🧠</span>
            <div class="card-title">LLM-as-a-Judge Comparison</div>
            <div class="card-text">
            Use an AI evaluator to rank responses and explain which output is most trustworthy.
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
    with fcol3:
        st.markdown('''
        <div class="glass-card">
            <span class="feature-icon">📊</span>
            <div class="card-title">Multi-Metric Scoring</div>
            <div class="card-text">
            Evaluate responses across key dimensions like relevance, coherence, and overall quality.
            </div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)

    # ------------------ ROW 2 ------------------
    fcol4, fcol5, fcol6 = st.columns(3)

    with fcol4:
        st.markdown('''
        <div class="glass-card">
            <span class="feature-icon">🧬</span>
            <div class="card-title">Fallback Response Improvement</div>
            <div class="card-text">
            When all candidate responses score poorly, EvalEngine generates an improved version using feedback from evaluation and comparison.
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with fcol5:
        st.markdown('''
        <div class="glass-card">
            <span class="feature-icon">⚠️</span>
            <div class="card-title">Hallucination Detection (In Progress)</div>
            <div class="card-text">
            Detect factual inaccuracies and unreliable claims in LLM responses before trusting them.
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with fcol6:
        st.markdown('''
        <div class="glass-card">
            <span class="feature-icon">📚</span>
            <div class="card-title">RAG-Based Grounding (In Progress)</div>
            <div class="card-text">
            Validate responses against external knowledge sources to improve evaluation reliability.
            </div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 6rem;"></div>', unsafe_allow_html=True)

    # HOW IT WORKS
    st.markdown('<div class="section-heading">How It Works</div>', unsafe_allow_html=True)

    hw1, hw2 = st.columns([1, 1], gap="large")

    with hw1:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
            <h3 style="color:#a5b4fc; margin-bottom: 20px;">1. Enter Your Prompt</h3>
            <p style="color:#94a3b8; font-size:1.1rem; line-height: 1.6;">
            Provide the input or task you want to evaluate.
            </p>
            <br>
            <h3 style="color:#a5b4fc; margin-bottom: 20px;">2. Generate or Add Responses</h3>
            <p style="color:#94a3b8; font-size:1.1rem; line-height: 1.6;">
            Either generate responses from models or input your own responses for evaluation.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with hw2:
        st.markdown("""
        <div class="glass-panel" style="height: 100%;">
            <h3 style="color:#a5b4fc; margin-bottom: 20px;">3. Evaluate and Compare</h3>
            <p style="color:#94a3b8; font-size:1.1rem; line-height: 1.6;">
            Each response is scored across multiple metrics and ranked to identify the most reliable output.
            </p>
            <br>
            <h3 style="color:#a5b4fc; margin-bottom: 20px;">4. Select or Improve</h3>
            <p style="color:#94a3b8; font-size:1.1rem; line-height: 1.6;">
            The best response is selected. If all responses score poorly, the system generates an improved version using evaluation feedback.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# MAIN APP VIEW
# ---------------------------------------------------------
# ---------------------------------------------------------
# MAIN APP VIEW
# ---------------------------------------------------------
def view_main_app():
    # TOP NAVIGATION BAR
    nav_col1, nav_col2, nav_col3 = st.columns([6, 2, 2])
    
    with nav_col1:
        st.markdown(
            '<div style="font-size: 1.5rem; font-weight: 800; background: linear-gradient(to right, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">EvalEngine — LLM Evaluation Workspace</div>',
            unsafe_allow_html=True
        )
    
    with nav_col3:
        if st.button("Exit Workspace"):
            navigate_to('landing')
            st.rerun()

    st.markdown('<hr style="border-color: rgba(255,255,255,0.05); margin-top: 0.5rem; margin-bottom: 2rem;">', unsafe_allow_html=True)

    # WORKSPACE LAYOUT
    cfg_col, task_col = st.columns([1, 2], gap="large")

    # ---------------- LEFT PANEL ----------------
    with cfg_col:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)

        st.markdown('<div class="card-title">1. Select Response Source</div>', unsafe_allow_html=True)
        st.markdown('<p class="card-text" style="font-size: 0.9rem;">Choose whether to generate responses or provide your own.</p>', unsafe_allow_html=True)

        mode = st.radio(
            "Source Mode",
            ["Generate Responses", "Use My Responses"],
            label_visibility="collapsed"
        )

        user_responses = []

        if mode == "Use My Responses":
            n_res = st.number_input("Number of responses", min_value=1, max_value=5, value=2)
            st.caption("Enter responses to evaluate:")

            for i in range(n_res):
                rsp = st.text_area(f"Response {i+1}", key=f"user_req_{i}", height=80)
                if rsp:
                    user_responses.append({"response": rsp, "temperature": "user"})

        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- RIGHT PANEL ----------------
    with task_col:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)

        st.markdown('<div class="card-title">2. Enter Prompt</div>', unsafe_allow_html=True)
        st.markdown('<p class="card-text" style="font-size: 0.9rem;">Provide the input or task for evaluation.</p>', unsafe_allow_html=True)

        prompt = st.text_area(
            "Prompt",
            height=140,
            placeholder="Example: Explain the trade-offs between microservices and monolithic architectures.",
            label_visibility="collapsed"
        )

        st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)

        if st.button("Evaluate Responses"):
            execute_evaluation(prompt, mode, user_responses)

        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- RESULTS ----------------
    if st.session_state.eval_data:
        st.markdown('<div style="margin-top: 4rem;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Evaluation Results</div>', unsafe_allow_html=True)

        e_data = st.session_state.eval_data
        ranked = e_data['ranked']
        comparison = e_data['comparison']

        t1, t2, t3 = st.tabs([
            "Ranked Responses",
            "Evaluation Summary",
            "Response Improvement"
        ])

        # -------- TAB 1 --------
        with t1:
            for i, item in enumerate(ranked):
                if i == 0:
                    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)

                    mc1, mc2 = st.columns([2, 1])

                    with mc1:
                        st.markdown("**Best Response:**")
                        st.info(item.get("response", ""))

                    with mc2:
                        st.metric("Score", round(item.get("final_score", 0), 2))
                        st.plotly_chart(create_radar_chart(item.get("evaluation", {})), use_container_width=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                else:
                    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)

                    mc1, mc2 = st.columns([3, 1])

                    with mc1:
                        st.write(item.get("response", ""))

                    with mc2:
                        st.metric("Score", item.get("final_score", 0))
                        with st.expander("Evaluation Details"):
                            st.json(item.get("evaluation", {}))

                    st.markdown('</div>', unsafe_allow_html=True)

        # -------- TAB 2 --------
        with t2:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)

            if isinstance(comparison, dict):
                st.markdown("### Final Ranking")
                st.success(comparison.get("ranking", "No ranking available"))

                st.markdown("### Evaluation Reasoning")
                st.write(comparison.get("reason", "No reasoning available"))

            st.markdown('</div>', unsafe_allow_html=True)

        # -------- TAB 3 --------
        with t3:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)

            c1, c2 = st.columns(2)

            with c1:
                st.markdown("**Best Available Response**")
                if ranked:
                    st.info(ranked[0].get("response", ""))

            with c2:
                st.markdown("**Improved Response (if needed)**")

                if st.session_state.improved_data:
                    imp = st.session_state.improved_data
                    st.success(imp.get("response", ""))
                    st.plotly_chart(create_radar_chart(imp.get("evaluation", {})), use_container_width=True)

                else:
                    if st.button("Generate Improved Response"):
                        improved = improve_and_evaluate(e_data['prompt'], ranked)

                        if improved:
                            st.session_state.improved_data = improved
                            st.rerun()
                        else:
                            st.error("Improvement failed")

            st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# EXECUTION FUNCTION (FIXED)
# ---------------------------------------------------------
def execute_evaluation(prompt, mode, user_responses):

    if not prompt.strip():
        st.error("Please enter a prompt to evaluate.")
        return

    with st.status("Running evaluation...", expanded=True):

        # -------- GET RESPONSES --------
        if mode == "Generate Responses":
            st.write("Generating responses...")
            responses = generate_multiple_responses(prompt)

            if not responses:
                st.error("Failed to generate responses")
                return

        else:
            if not user_responses:
                st.error("Please provide at least one response")
                return
            responses = user_responses

        # -------- EVALUATION --------
        st.write("Evaluating responses...")
        evaluated = evaluate_multiple_responses(prompt, responses)

        # -------- RANKING --------
        st.write("Ranking responses...")
        ranked = rank_responses(evaluated)

        # -------- COMPARISON --------
        st.write("Comparing responses...")
        comparison = compare_responses(prompt, responses)

    st.session_state.eval_data = {
        "prompt": prompt,
        "ranked": ranked,
        "comparison": comparison
    }

    st.session_state.improved_data = None
    st.rerun()

# ---------------------------------------------------------
# ROUTING LOGIC
# ---------------------------------------------------------
if st.session_state.page == 'landing':
    view_landing()
else:
    view_main_app()