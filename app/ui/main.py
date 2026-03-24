import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from app.services.generator import generate_multiple_responses
from app.services.evaluator import evaluate_multiple_responses
from app.services.comparator import rank_responses, get_best_response
from app.services.judge import compare_responses
from app.services.improver import improve_and_evaluate

# ---- CONFIG ----
st.set_page_config(
    page_title="EvalEngine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- LOAD CSS ----
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---- SESSION STATE ----
for key, val in [("page", "home"), ("run", False)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ============================================================
# LANDING PAGE
# ============================================================
if st.session_state.page == "home":

    st.markdown("""
    <div class='hero-container'>
        <div class='hero-badge'>v1.0 — now live</div>
        <h1 class='gradient-text'>EvalEngine</h1>
        <p class='hero-subtitle'>
            Structured evaluation, AI judging, and auto-improvement loops
            for LLM responses. Trust what your model outputs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_cta1, col_cta2, col_spacer = st.columns([1, 1, 4])
    with col_cta1:
        if st.button("⚡  Launch App", use_container_width=True):
            st.session_state.page = "app"
            st.rerun()
    with col_cta2:
        st.button("↗  View Docs", use_container_width=True)

    st.markdown("""
    <div class='stat-grid'>
        <div class='stat-cell'>
            <div class='stat-num'>3x</div>
            <div class='stat-label'>Response Variants</div>
        </div>
        <div class='stat-cell'>
            <div class='stat-num'>AI</div>
            <div class='stat-label'>Judge Scoring</div>
        </div>
        <div class='stat-cell'>
            <div class='stat-num'>∞</div>
            <div class='stat-label'>Improve Loop</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='feature-grid'>
        <div class='feature-card'>
            <span class='feature-icon'>◈</span>
            <div class='feature-title'>Multi-Response Generation</div>
            <div class='feature-desc'>
                Generates 3 response variants at different temperatures
                to explore the model output space.
            </div>
        </div>
        <div class='feature-card'>
            <span class='feature-icon'>◉</span>
            <div class='feature-title'>Structured Scoring</div>
            <div class='feature-desc'>
                Each response scored across accuracy, clarity,
                completeness, and relevance.
            </div>
        </div>
        <div class='feature-card'>
            <span class='feature-icon'>⊞</span>
            <div class='feature-title'>AI Comparative Judge</div>
            <div class='feature-desc'>
                An independent LLM judge ranks all responses
                and explains its reasoning.
            </div>
        </div>
        <div class='feature-card'>
            <span class='feature-icon'>↺</span>
            <div class='feature-title'>Auto Improvement</div>
            <div class='feature-desc'>
                Takes the best response and iteratively refines
                it using evaluation feedback as context.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='margin-top:2.5rem;padding:1.1rem 1.4rem;
         background:#111116;border:1px solid rgba(255,255,255,0.06);
         border-radius:10px;font-family:"JetBrains Mono",monospace;
         font-size:0.75rem;color:#4a4a5a;'>
        <span style='color:#f5a623'>$</span>
        <span style='color:#8a8a9a;margin-left:8px'>python -m streamlit run app/ui/main.py</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# MAIN APP
# ============================================================
elif st.session_state.page == "app":

    nav1, nav2, nav3 = st.columns([1, 6, 1])
    with nav1:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.run = False
            st.session_state.pop("result", None)
            st.rerun()
    with nav2:
        st.markdown("""
        <div style='display:flex;align-items:center;justify-content:center;
             gap:10px;padding:0.4rem 0;'>
            <span class='gradient-text-sm'>EvalEngine</span>
            <span style='font-family:"JetBrains Mono",monospace;font-size:0.7rem;
                   color:#4a4a5a;background:#16161d;
                   border:1px solid rgba(255,255,255,0.06);
                   border-radius:100px;padding:2px 10px;'>workspace</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        "<div style='height:1px;background:rgba(255,255,255,0.06);margin-bottom:1.5rem;'></div>",
        unsafe_allow_html=True
    )

    left, right = st.columns([1, 2], gap="large")

    # ---- LEFT PANEL ----
    with left:
        st.markdown("<div class='panel-title'>Configure</div>", unsafe_allow_html=True)

        prompt = st.text_area(
            "PROMPT",
            placeholder="Enter the prompt you want to evaluate...",
            height=140
        )

        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

        mode = st.radio("MODE", ["Generate Responses", "Enter Your Own"])

        responses = []

        if mode == "Enter Your Own":
            num = st.number_input("NUMBER OF RESPONSES", min_value=2, max_value=5, value=2)
            for i in range(int(num)):
                r = st.text_area(
                    f"RESPONSE {i+1}",
                    key=f"resp_{i}",
                    height=100,
                    placeholder=f"Paste response {i+1} here..."
                )
                if r.strip():
                    responses.append({"response": r})

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if st.button("⚡  Run Evaluation", use_container_width=True, type="primary"):
            if not prompt.strip():
                st.warning("Enter a prompt first.")
            elif mode == "Enter Your Own" and len(responses) < 2:
                st.warning("Enter at least 2 responses.")
            else:
                st.session_state.run = True
                st.session_state.pop("result", None)

        if st.session_state.get("result"):
            st.markdown("""
            <div style='margin-top:0.75rem;padding:0.6rem 0.9rem;
                 background:rgba(86,211,100,0.08);
                 border:1px solid rgba(86,211,100,0.2);
                 border-radius:8px;font-family:"JetBrains Mono",monospace;
                 font-size:0.72rem;color:#56d364;
                 display:flex;align-items:center;gap:6px;'>
                <span style='width:6px;height:6px;border-radius:50%;
                       background:#56d364;display:inline-block;'></span>
                Evaluation complete
            </div>
            """, unsafe_allow_html=True)

    # ---- PROCESS ----
    if st.session_state.get("run") and "result" not in st.session_state:
        with st.spinner("Running evaluation..."):
            try:
                if mode == "Generate Responses":
                    responses = generate_multiple_responses(prompt)

                evaluated = evaluate_multiple_responses(prompt, responses)
                ranked    = rank_responses(evaluated)
                best      = get_best_response(ranked)
                judge     = compare_responses(prompt, responses)
                improved  = improve_and_evaluate(prompt, ranked)

                st.session_state.result = {
                    "ranked":   ranked   or [],
                    "best":     best,
                    "judge":    judge    or {},
                    "improved": improved or {},   # <-- null guard: default to empty dict
                }
                st.session_state.run = False
                st.rerun()

            except Exception as e:
                st.error(f"Evaluation failed: {e}")
                st.session_state.run = False

    # ---- RIGHT PANEL ----
    with right:

        if "result" not in st.session_state:
            # Empty state
            st.markdown("""
            <div style='position:relative;min-height:380px;background:#111116;
                 border:1px solid rgba(255,255,255,0.06);border-radius:20px;
                 display:flex;flex-direction:column;align-items:center;
                 justify-content:center;gap:1rem;overflow:hidden;'>
                <div class='grid-bg'></div>
                <div style='font-family:"JetBrains Mono",monospace;
                     font-size:2.5rem;opacity:0.12;position:relative;'>⚡</div>
                <div style='font-family:"JetBrains Mono",monospace;
                     font-size:0.8rem;color:#4a4a5a;text-align:center;
                     line-height:1.8;position:relative;'>
                    Configure your prompt<br>and run an evaluation
                </div>
                <div style='font-family:"JetBrains Mono",monospace;
                     font-size:0.72rem;color:#4a4a5a;
                     display:flex;align-items:center;gap:6px;position:relative;'>
                    <span style='color:#f5a623'>▶</span> awaiting input
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            result  = st.session_state.result
            ranked  = result.get("ranked", [])
            judge   = result.get("judge", {})
            improved= result.get("improved") or {}   # safe even if None

            # ==================================================
            # SECTION 1 — ALL RESPONSES in one box
            # ==================================================
            st.markdown("""
            <div class='section-header'>
                <span class='section-title'>Generated Responses</span>
                <div class='section-header-line'></div>
            </div>
            """, unsafe_allow_html=True)

            # One big container card
            st.markdown("<div class='responses-container'>", unsafe_allow_html=True)

            for i, r in enumerate(ranked):
                resp_text  = r.get("response", "")
                evaluation = r.get("evaluation", {})
                score_val  = r.get("score", "—")
                is_best    = (i == 0)

                # Divider between items (not before first)
                if i > 0:
                    st.markdown(
                        "<div style='height:1px;background:rgba(255,255,255,0.05);margin:0.75rem 0;'></div>",
                        unsafe_allow_html=True
                    )

                # Row: rank + score pill
                best_label = " &nbsp;<span style='background:rgba(245,166,35,0.12);border:1px solid rgba(245,166,35,0.25);border-radius:100px;padding:1px 9px;font-size:0.6rem;color:#f5a623;'>best</span>" if is_best else ""
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:0.4rem;'>
                    <span style='font-family:"JetBrains Mono",monospace;font-size:0.65rem;
                           color:#4a4a5a;letter-spacing:.08em;'>RESPONSE {i+1}</span>
                    {best_label}
                    <span style='margin-left:auto;font-family:"JetBrains Mono",monospace;
                           font-size:0.65rem;background:rgba(45,224,193,0.08);
                           border:1px solid rgba(45,224,193,0.18);border-radius:100px;
                           padding:2px 10px;color:#2de0c1;'>score&nbsp;{score_val}</span>
                </div>
                """, unsafe_allow_html=True)

                # Response text
                st.markdown(f"""
                <div style='font-family:"JetBrains Mono",monospace;font-size:0.82rem;
                     color:#d0d0d8;line-height:1.8;padding:0.75rem 0;
                     white-space:pre-wrap;word-break:break-word;'>
                    {resp_text}
                </div>
                """, unsafe_allow_html=True)

                # Collapsible eval breakdown
                with st.expander(f"Evaluation breakdown — Response {i+1}"):
                    st.json(evaluation)

            st.markdown("</div>", unsafe_allow_html=True)

            # ==================================================
            # SECTION 2 — SCORES side by side
            # ==================================================
            st.markdown("""
            <div class='section-header' style='margin-top:2rem;'>
                <span class='section-title'>Score Summary</span>
                <div class='section-header-line'></div>
            </div>
            """, unsafe_allow_html=True)

            score_cols = st.columns(len(ranked))
            for i, (col, r) in enumerate(zip(score_cols, ranked)):
                score_val = r.get("score", "—")
                is_best   = (i == 0)
                border_col = "rgba(245,166,35,0.35)" if is_best else "rgba(255,255,255,0.07)"
                num_col    = "#f5a623" if is_best else "#2de0c1"
                lbl_extra  = "<br><span style='font-size:0.58rem;color:#f5a623;letter-spacing:.06em;'>★ BEST</span>" if is_best else ""
                with col:
                    st.markdown(f"""
                    <div style='background:#16161d;border:1px solid {border_col};
                         border-radius:12px;padding:1.1rem;text-align:center;'>
                        <div style='font-family:"Syne",sans-serif;font-size:2rem;
                             font-weight:800;color:{num_col};line-height:1;
                             margin-bottom:0.3rem;'>{score_val}</div>
                        <div style='font-family:"JetBrains Mono",monospace;
                             font-size:0.65rem;color:#4a4a5a;letter-spacing:.08em;
                             text-transform:uppercase;'>Response {i+1}{lbl_extra}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # ==================================================
            # SECTION 3 — JUDGE OUTPUT
            # ==================================================
            st.markdown("""
            <div class='section-header' style='margin-top:2rem;'>
                <span class='section-title'>AI Judge</span>
                <div class='section-header-line'></div>
            </div>
            """, unsafe_allow_html=True)

            ranking_txt     = judge.get("ranking", "")
            explanation_txt = judge.get("explanation", "")

            if ranking_txt or explanation_txt:
                st.markdown(f"""
                <div class='judge-box fade-in'>
                    <div style='font-family:"JetBrains Mono",monospace;
                         font-size:0.85rem;color:#2de0c1;font-weight:500;
                         margin-bottom:0.6rem;letter-spacing:.02em;'>{ranking_txt}</div>
                    <div style='font-family:"JetBrains Mono",monospace;
                         font-size:0.8rem;color:#8a8a9a;line-height:1.8;'>
                         {explanation_txt}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='judge-box fade-in'>
                    <div style='font-family:"JetBrains Mono",monospace;
                         font-size:0.8rem;color:#4a4a5a;'>No judge output available.</div>
                </div>
                """, unsafe_allow_html=True)

            # ==================================================
            # SECTION 4 — IMPROVED RESPONSE
            # ==================================================
            if improved:
                st.markdown("""
                <div class='section-header' style='margin-top:2rem;'>
                    <span class='section-title'>Improved Response</span>
                    <div class='section-header-line'></div>
                </div>
                """, unsafe_allow_html=True)

                improved_score = improved.get("score", "—")
                improved_resp  = improved.get("response", "")

                if improved_resp:
                    st.markdown(f"""
                    <div class='improved-box fade-in'>
                        <div style='display:flex;align-items:center;gap:8px;margin-bottom:0.75rem;'>
                            <span style='font-family:"JetBrains Mono",monospace;font-size:0.68rem;
                                   color:#56d364;background:rgba(86,211,100,0.08);
                                   border:1px solid rgba(86,211,100,0.2);border-radius:100px;
                                   padding:2px 10px;'>score {improved_score}</span>
                            <span style='font-family:"JetBrains Mono",monospace;
                                   font-size:0.68rem;color:#3a3a4a;'>auto-refined</span>
                        </div>
                        <div style='font-family:"JetBrains Mono",monospace;
                             font-size:0.82rem;color:#d0d0d8;line-height:1.8;
                             white-space:pre-wrap;word-break:break-word;'>
                            {improved_resp}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)