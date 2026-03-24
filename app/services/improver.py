from groq import Groq
from app.config.settings import settings
from app.services.evaluator import evaluate_response

client = Groq(api_key=settings.GROQ_API_KEY)


def generate_improved_response(prompt, bad_responses):
    """
    Generate improved response using weak responses as context
    """

    combined = ""

    for i, res in enumerate(bad_responses):
        combined += f"\nBad Response {i+1}:\n{res['response']}\n"

    improvement_prompt = f"""
You are an expert AI assistant.

The following responses are poor quality.

Your job:
- Identify their weaknesses
- Generate a much better response

IMPORTANT:
- Be accurate
- Be clear and structured
- Fully answer the prompt
- Avoid hallucinations
- Improve completeness and correctness

Prompt:
{prompt}

Bad Responses:
{combined}

Now generate an improved response:
"""

    try:
        result = client.chat.completions.create(
            messages=[{"role": "user", "content": improvement_prompt}],
            model=settings.GEN_MODEL,
            temperature=0.3
        )

        return result.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"


def improve_and_evaluate(prompt, responses, threshold=3):
    """
    Full improvement loop
    """

    # Step 1: Check scores
    scores = [r["final_score"] for r in responses]

    if max(scores) >= threshold:
        return None  # No need to improve

    print("\n⚠️ All responses are low quality. Improving...\n")

    # Step 2: Generate improved response
    improved = generate_improved_response(prompt, responses)

    # Step 3: Evaluate improved response
    evaluation = evaluate_response(prompt, improved)

    return {
        "response": improved,
        "evaluation": evaluation
    }