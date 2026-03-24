from groq import Groq
from app.config.settings import settings
import json

client = Groq(api_key=settings.GROQ_API_KEY)


def evaluate_response(prompt, response):
    """
    Evaluate a single response using LLM-as-a-judge
    """

    evaluation_prompt = f"""
You are an expert AI evaluator.

Evaluate the response based on:

1. Relevance (0-10)
2. Factuality (0-10)
3. Completeness (0-10)
4. Bias/Safety (0-10)

Return ONLY valid JSON in this format:

{{
  "relevance": number,
  "factuality": number,
  "completeness": number,
  "bias": number,
  "explanation": "short explanation"
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