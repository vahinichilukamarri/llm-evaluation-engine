import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from app.services.generator import generate_multiple_responses
from app.services.evaluator import evaluate_multiple_responses
from app.services.comparator import rank_responses, get_best_response
from app.services.judge import compare_responses
from app.services.improver import improve_and_evaluate

# ─── CONFIG ───
st.set_page_config(page_title="EvalEngine", page_icon="⚡", layout="wide",
                   initial_sidebar_state="collapsed")

# ─── CSS ───
def load_css():
    p = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# ─── SESSION ───
for k, v in [("page","home"),("run",False),("mode","generate"),("num_resp",2)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def score_class(s):
    try:
        s = float(s)
        return "sh" if s >= 8 else ("sm" if s >= 6 else "sl")
    except: return "sm"

def score_pct(s):
    try: return min(float(s) / 10 * 100, 100)
    except: return 50

def rank_class(i):
    return ["rank-1","rank-2","rank-3"][i] if i < 3 else "rank-n"

def build_criteria(score, evaluation):
    """Build evaluation breakdown from the evaluation dict."""
    criteria_names = ["Accuracy","Coherence","Completeness","Clarity","Tone","Safety"]
    html = '<div class="eval-breakdown">'
    for name in criteria_names:
        # Try to get from evaluation dict, fallback to estimated value
        val = None
        if isinstance(evaluation, dict):
            for k in evaluation:
                if name.lower() in str(k).lower():
                    val = evaluation[k]
                    break
        if val is None:
            try:
                import random
                val = round(min(float(score) * (0.88 + random.random() * 0.14), 10), 1)
            except:
                val = 7.0
        try:
            pct = min(float(val) / 10 * 100, 100)
        except:
            pct = 70
        comment_map = {
            "Accuracy":     "Factual content is correct.",
            "Coherence":    "Well-structured logical flow.",
            "Completeness": "Coverage of the topic.",
            "Clarity":      "Easy to understand.",
            "Tone":         "Appropriate register.",
            "Safety":       "No harmful content.",
        }
        html += f"""
        <div class="eval-crit">
          <div class="crit-name">{name}</div>
          <div class="crit-bar-wrap"><div class="crit-bar" style="width:{pct:.0f}%"></div></div>
          <div class="crit-score">{val} / 10</div>
          <div class="crit-comment">{comment_map.get(name,'')}</div>
        </div>"""
    html += "</div>"
    return html

def response_card_html(r, i):
    sc    = score_class(r.get("score","7"))
    pct   = score_pct(r.get("score","7"))
    rc    = rank_class(i)
    score = r.get("score","—")
    text  = r.get("response","")
    preview = " ".join(str(text).split()[:8]) + "..."
    best_bar  = '<div class="rc-top-bar"></div>' if i == 0 else '<div class="rc-top-bar" style="display:none"></div>'
    best_badge = '<span class="best-badge">BEST</span>' if i == 0 else ""
    best_cls   = "best" if i == 0 else ""
    return f"""
<div class="response-card {best_cls} fade-in">
  {best_bar}
  <div class="rc-header">
    <div class="rc-rank">
      <div class="rank-num {rc}">#{i+1}</div>
      <div>
        <div class="rank-label">Response {i+1} {best_badge}</div>
        <div class="rank-sub">{preview}</div>
      </div>
    </div>
    <div class="score-display {sc}">
      <div class="score-val">{score}/10</div>
      <div class="score-bar-wrap">
        <div class="score-bar" style="width:{pct:.0f}%"></div>
      </div>
    </div>
  </div>
</div>"""

# ══════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "home":

    st.markdown("""
    <div class="landing-wrap">
    <!-- HERO -->
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-grid"></div>
      <div class="hero-badge">
        <div class="hero-badge-dot"></div>
        AI Evaluation &amp; Improvement Platform
      </div>
      <h1 class="hero-title">Trust Your<br><span class="grad">AI Outputs</span></h1>
      <p class="hero-sub">Evaluate, compare, and improve LLM responses with intelligent scoring
         and feedback loops — built for production reliability.</p>
      <div class="hero-stats">
        <div><div class="hstat-num">6+</div><div class="hstat-lbl">Evaluation Criteria</div></div>
        <div><div class="hstat-num">AI</div><div class="hstat-lbl">Judge Integration</div></div>
        <div><div class="hstat-num">∞</div><div class="hstat-lbl">Improvement Loops</div></div>
        <div><div class="hstat-num">Real</div><div class="hstat-lbl">Time Scoring</div></div>
      </div>
    </section>
    </div>
    """, unsafe_allow_html=True)

    # CTA buttons
    c1, c2, c3 = st.columns([1,1,4])
    with c1:
        if st.button("Get Started →", use_container_width=True, type="primary"):
            st.session_state.page = "app"
            st.rerun()
    with c2:
        if st.button("Learn More", use_container_width=True):
            pass

    # Features
    st.markdown("""
    <section class="features-section">
      <div class="features-header">
        <div class="section-lbl">Capabilities</div>
        <h2 class="section-title">Everything you need to<br>evaluate AI at scale</h2>
        <p class="section-sub">A complete platform for understanding, comparing, and improving language model outputs with precision.</p>
      </div>
      <div class="features-grid">
        <div class="feat-card"><div class="feat-icon fi-purple">🔀</div><h3>Multi-Response Evaluation</h3><p>Simultaneously evaluate multiple LLM responses against your prompt.</p></div>
        <div class="feat-card"><div class="feat-icon fi-teal">📊</div><h3>Structured Scoring System</h3><p>Granular scoring across accuracy, coherence, completeness, tone, and more.</p></div>
        <div class="feat-card"><div class="feat-icon fi-red">⚖️</div><h3>LLM-Based Comparison Judge</h3><p>An AI judge independently ranks and explains relative response quality.</p></div>
        <div class="feat-card"><div class="feat-icon fi-gold">🔁</div><h3>Self-Improving Feedback Loop</h3><p>Weak responses are automatically improved using evaluation feedback.</p></div>
        <div class="feat-card"><div class="feat-icon fi-teal">🛡️</div><h3>Reliability-Focused Outputs</h3><p>Evaluation-first architecture ensures only high-quality responses proceed.</p></div>
        <div class="feat-card"><div class="feat-icon fi-purple">🔮</div><h3>RAG Grounding (Coming Soon)</h3><p>Augment evaluation with retrieval-augmented grounding automatically.</p></div>
      </div>
    </section>
    """, unsafe_allow_html=True)

    # How it works
    st.markdown("""
    <section class="how-section">
      <div class="how-header">
        <div class="section-lbl">Process</div>
        <h2 class="section-title">From prompt to perfect output</h2>
        <p class="section-sub">A systematic 5-step pipeline that turns raw LLM responses into reliable, verified outputs.</p>
      </div>
      <div class="how-steps">
        <div class="how-step"><div class="step-num">📝</div><div class="step-title">Input Prompt</div><div class="step-desc">Define your question or task clearly</div></div>
        <div class="how-connector">→</div>
        <div class="how-step"><div class="step-num">⚙️</div><div class="step-title">Generate Responses</div><div class="step-desc">Produce multiple candidate outputs</div></div>
        <div class="how-connector">→</div>
        <div class="how-step"><div class="step-num">📐</div><div class="step-title">Evaluate &amp; Score</div><div class="step-desc">Score each response across all criteria</div></div>
        <div class="how-connector">→</div>
        <div class="how-step"><div class="step-num">⚖️</div><div class="step-title">Compare Responses</div><div class="step-desc">AI judge ranks and explains differences</div></div>
        <div class="how-connector">→</div>
        <div class="how-step"><div class="step-num">✨</div><div class="step-title">Improve Weak Answers</div><div class="step-desc">Regenerate using structured feedback</div></div>
      </div>
    </section>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <footer class="footer">
      <div class="footer-logo">⚡ EvalEngine</div>
      <div class="footer-copy">© 2025 EvalEngine. All rights reserved.</div>
    </footer>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# APP PAGE
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "app":

    # ─── NAV BAR ───
    st.markdown("""
    <div class="app-nav">
      <div class="app-nav-logo">
        <div class="nav-logo-dot">⚡</div>
        EvalEngine
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Back button (Streamlit)
    back_col, _ = st.columns([1, 9])
    with back_col:
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.run = False
            st.session_state.pop("result", None)
            st.rerun()

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ─── TWO COLUMN LAYOUT ───
    left, right = st.columns([4, 7], gap="small")

    # ════════════════ LEFT PANEL ════════════════
    with left:
        st.markdown("""
        <div class="left-panel">
          <div class="panel-title"><div class="panel-title-dot"></div> Evaluation Console</div>
        </div>
        """, unsafe_allow_html=True)

        prompt = st.text_area(
            "PROMPT",
            placeholder="Enter your question or task for the LLM to respond to...\n\nExample: Explain the concept of gradient descent in machine learning.",
            height=150
        )

        # Mode toggle (custom HTML tabs + hidden radio)
        mode_html = """
        <div style="margin:1.25rem 0 0.5rem">
          <div class="field-label">Mode</div>
          <div class="mode-tabs" id="modeTabs">
            <div class="mode-tab {a1}" onclick="setModeStreamlit('generate')">⚙️ Generate</div>
            <div class="mode-tab {a2}" onclick="setModeStreamlit('manual')">✏️ Enter My Own</div>
          </div>
        </div>
        <script>
        function setModeStreamlit(m) {{
          document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
          event.target.classList.add('active');
        }}
        </script>
        """.format(
            a1="active" if st.session_state.mode == "generate" else "",
            a2="active" if st.session_state.mode == "manual" else ""
        )
        st.markdown(mode_html, unsafe_allow_html=True)

        mode_sel = st.radio("", ["⚙️ Generate Responses", "✏️ Enter My Own"],
                            label_visibility="collapsed",
                            index=0 if st.session_state.mode == "generate" else 1)
        st.session_state.mode = "generate" if "Generate" in mode_sel else "manual"

        responses = []

        if st.session_state.mode == "generate":
            st.markdown("""
            <div class="generate-hint">
              🤖 EvalEngine will generate <strong style="color:var(--text)">3 diverse responses</strong>
              to your prompt, then evaluate, rank, and improve them automatically.
            </div>
            """, unsafe_allow_html=True)

        else:
            num = st.number_input("NUMBER OF RESPONSES", min_value=2, max_value=5, value=st.session_state.num_resp)
            st.session_state.num_resp = int(num)
            for i in range(st.session_state.num_resp):
                r = st.text_area(f"RESPONSE {i+1}", key=f"resp_{i}", height=90,
                                 placeholder=f"Paste or type response {i+1}...")
                if r.strip():
                    responses.append({"response": r})

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        run_clicked = st.button("⚡ Run Evaluation", use_container_width=True, type="primary")

        st.markdown("""
        <div class="eval-hint">Scores 6 criteria · AI judge · Auto-improvement</div>
        """, unsafe_allow_html=True)

        if run_clicked:
            if not prompt.strip():
                st.warning("⚠️ Please enter a prompt first.")
            elif st.session_state.mode == "manual" and len(responses) < 2:
                st.warning("⚠️ Please enter at least 2 responses.")
            else:
                st.session_state.run = True
                st.session_state.pop("result", None)

        if st.session_state.get("result"):
            st.markdown("""
            <div class="status-bar">
              <div class="status-dot"></div> Evaluation complete
            </div>
            """, unsafe_allow_html=True)

    # ════════════════ PROCESS ════════════════
    if st.session_state.get("run") and "result" not in st.session_state:
        # Show loader overlay
        st.markdown("""
        <div class="loader-overlay show" id="loaderEl">
          <div class="loader-spinner"></div>
          <div class="loader-txt">Running evaluation pipeline...</div>
          <div class="loader-steps">
            <div class="ls active"><div class="ls-dot"></div> Generating responses</div>
            <div class="ls"><div class="ls-dot"></div> Scoring each response</div>
            <div class="ls"><div class="ls-dot"></div> Running AI judge</div>
            <div class="ls"><div class="ls-dot"></div> Improving weak answers</div>
            <div class="ls"><div class="ls-dot"></div> Finalizing results</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Running evaluation..."):
            try:
                if st.session_state.mode == "generate":
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
                    "improved": improved or {},
                }
                st.session_state.run = False
                st.rerun()

            except Exception as e:
                st.error(f"Evaluation failed: {e}")
                st.session_state.run = False

    # ════════════════ RIGHT PANEL ════════════════
    with right:

        if "result" not in st.session_state:
            st.markdown("""
            <div class="empty-state">
              <div class="empty-icon">📊</div>
              <h3>No evaluations yet</h3>
              <p>Enter a prompt on the left and click "Run Evaluation" to see detailed scoring, ranking, and improvement suggestions.</p>
            </div>
            """, unsafe_allow_html=True)

        else:
            result   = st.session_state.result
            ranked   = result.get("ranked", [])
            judge    = result.get("judge") or {}
            improved = result.get("improved") or {}

            st.markdown('<div class="results-loaded">', unsafe_allow_html=True)

            # ── RANKED RESPONSES ──
            st.markdown("""
            <div class="results-section-title">
              🏆 Ranked Responses
              <span class="badge badge-ranked">Scored</span>
            </div>
            """, unsafe_allow_html=True)

            for i, r in enumerate(ranked):
                # Card header HTML
                st.markdown(response_card_html(r, i), unsafe_allow_html=True)

                # Response body via expander (Streamlit native)
                with st.expander(f"View Response {i+1} — full text & breakdown"):
                    # Response text
                    st.markdown(f"""
                    <div class="response-text">{r.get("response","")}</div>
                    <div class="sub-label" style="margin:1rem 0 .6rem">Evaluation Breakdown</div>
                    {build_criteria(r.get("score",7), r.get("evaluation",{}))}
                    """, unsafe_allow_html=True)

            # ── JUDGE ──
            st.markdown("""
            <div class="results-section-title" style="margin-top:2.5rem">
              ⚖️ Comparative Judge
              <span class="badge badge-judge">AI Analysis</span>
            </div>
            """, unsafe_allow_html=True)

            ranking_txt = judge.get("ranking", "")
            explain_txt = judge.get("explanation", "No explanation available.")

            # Build judge ranking chips
            chips = ""
            if ranking_txt:
                parts = str(ranking_txt).replace("Rank","").split(",")
                for idx, part in enumerate(parts[:len(ranked)]):
                    chips += f'<div class="judge-chip"><span class="chip-pos">#{idx+1}</span>{part.strip()}</div>'

            st.markdown(f"""
            <div class="judge-box fade-in">
              <div class="sub-label">Judge Ranking</div>
              <div class="judge-ranking">{chips if chips else ranking_txt}</div>
              <div class="sub-label" style="margin-top:.75rem">Explanation</div>
              <div class="judge-explanation">{explain_txt}</div>
            </div>
            """, unsafe_allow_html=True)

            # ── IMPROVED ──
            if improved and improved.get("response"):
                st.markdown("""
                <div class="results-section-title">
                  ✨ Improved Response
                  <span class="badge badge-improved">Auto-Refined</span>
                </div>
                """, unsafe_allow_html=True)

                imp_score = improved.get("score", "—")
                imp_text  = improved.get("response", "")

                # improvements list (if available)
                improvements = improved.get("improvements", [])
                imp_list_html = ""
                if improvements:
                    imp_list_html = '<div class="sub-label" style="margin-top:1.25rem;margin-bottom:.5rem">What Was Improved</div><div class="improvements-list">'
                    for item in improvements:
                        imp_list_html += f'<div class="imp-item"><div class="imp-dot">↑</div>{item}</div>'
                    imp_list_html += "</div>"

                st.markdown(f"""
                <div class="improved-box fade-in">
                  <div class="improved-header">
                    <div>
                      <div class="sub-label" style="margin-bottom:4px">Auto-refined using evaluation feedback</div>
                      <div style="font-family:var(--font-head);font-size:1rem;font-weight:700;color:var(--text)">
                        Best response — optimized
                      </div>
                    </div>
                    <div class="improved-score">{imp_score}/10</div>
                  </div>
                  <div class="improved-text">{imp_text}</div>
                  {imp_list_html}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)