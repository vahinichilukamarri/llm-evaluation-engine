from groq import Groq
from app.config.settings import settings
import json

client = Groq(api_key=settings.GROQ_API_KEY)


def evaluate_response(prompt, response):
    """
    Evaluate a single response using LLM-as-a-judge
    """

    evaluation_prompt = f"""
You are a STRICT AI evaluator.

Your job is to critically evaluate the response.

IMPORTANT RULES:
- Do NOT give similar scores to all responses
- Be highly critical and differentiate quality
- Penalize generic, repetitive, or less insightful answers
- Reward clarity, depth, structure, and usefulness

Score based on:

1. Relevance (0-10): Does it directly answer the question?
2. Factuality (0-10): Is it accurate and correct?
3. Completeness (0-10): Does it fully cover the topic?
4. Bias/Safety (0-10): Is it neutral and balanced?

SCORING GUIDELINES:
- 9-10 → Excellent, high quality
- 7-8 → Good but missing depth
- 5-6 → Average, generic
- <5 → Poor or incorrect

Return ONLY valid JSON:

{{
  "relevance": number,
  "factuality": number,
  "completeness": number,
  "bias": number,
  "explanation": "why this score"
}}

Prompt:
{prompt}

Response:
{response}
"""

    try:
        result = client.chat.completions.create(
            messages=[{"role": "user", "content": evaluation_prompt}],
            model=settings.EVAL_MODEL,
            temperature=0.0
        )

        content = result.choices[0].message.content.strip()

        try:
            return json.loads(content)
        except:
            return {
                "error": "Invalid JSON",
                "raw_output": content
            }

    except Exception as e:
        return {"error": str(e)}


def evaluate_multiple_responses(prompt, responses):
    """
    Evaluate a list of responses
    """

    evaluated = []

    for res in responses:
        print("Evaluating response...")

        evaluation = evaluate_response(prompt, res["response"])

        evaluated.append({
            "response": res["response"],
            "temperature": res.get("temperature", "user"),
            "evaluation": evaluation
        })

    return evaluated