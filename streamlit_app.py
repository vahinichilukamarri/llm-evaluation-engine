import streamlit as st

from app.services.generator import generate_multiple_responses
from app.services.evaluator import evaluate_multiple_responses
from app.services.comparator import rank_responses, get_best_response
from app.services.judge import compare_responses
from app.services.improver import improve_and_evaluate


st.set_page_config(page_title="LLM Evaluation Engine", layout="wide")

st.title("🧠 LLM Evaluation & Improvement Engine")

# 🔹 Input
prompt = st.text_area("Enter your prompt:")

mode = st.radio(
    "Choose mode:",
    ["Generate responses", "Enter your own responses"]
)

responses = []

# 🔹 User input responses
if mode == "Enter your own responses":
    n = st.number_input("How many responses?", min_value=1, max_value=5, value=2)

    for i in range(n):
        res = st.text_area(f"Response {i+1}", key=f"user_res_{i}")
        if res:
            responses.append({"response": res, "temperature": "user"})

# 🔹 Button
if st.button("🚀 Evaluate"):

    if not prompt.strip():
        st.error("Please enter a prompt")
        st.stop()

    # Generate responses
    if mode == "Generate responses":
        with st.spinner("Generating responses..."):
            responses = generate_multiple_responses(prompt)

    if not responses:
        st.warning("No responses to evaluate")
        st.stop()

    # 🔍 Evaluate
    with st.spinner("Evaluating responses..."):
        evaluated = evaluate_multiple_responses(prompt, responses)

    # 📊 Rank
    ranked = rank_responses(evaluated)
    best = get_best_response(ranked)

    st.subheader("🏆 Ranked Responses")

    for i, item in enumerate(ranked):
        with st.container():
            st.markdown(f"### Rank {i+1} — Score: {item['final_score']}")

            st.write("**Response:**")
            st.write(item["response"])

            st.write("**Evaluation:**")
            st.json(item["evaluation"])

            if i == 0:
                st.success("⭐ Best Response")

    # 🧠 Judge
    st.subheader("🧠 Comparative Judge")

    comparison = compare_responses(prompt, responses)

    if isinstance(comparison, dict):
        st.write("**Ranking:**", comparison.get("ranking"))
        st.write("**Reason:**", comparison.get("reason"))
    else:
        st.write(comparison)

    # 🚀 Improvement Loop
    improved = improve_and_evaluate(prompt, ranked)

    if improved:
        st.subheader("🚀 Improved Response")

        st.write(improved["response"])

        st.write("**Evaluation:**")
        st.json(improved["evaluation"])