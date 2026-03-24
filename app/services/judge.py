from groq import Groq
from app.config.settings import settings
import json

client = Groq(api_key=settings.GROQ_API_KEY)


def compare_responses(prompt, responses):
    """
    Compare multiple responses using LLM and rank them
    """

    combined = ""

    for i, res in enumerate(responses):
        combined += f"\nResponse {i+1}:\n{res['response']}\n"

    prompt_text = f"""
You are an expert AI judge.

Compare the following responses.

IMPORTANT:
- You MUST differentiate between them
- Even small differences matter
- Focus on clarity, usefulness, and quality

Prompt:
{prompt}

Responses:
{combined}

Return ONLY JSON:

{{
  "ranking": [best, second, third],
  "reason": "explanation"
}}
"""

    try:
        result = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_text}],
            model=settings.EVAL_MODEL,
            temperature=0.0
        )

        content = result.choices[0].message.content.strip()

        try:
            return json.loads(content)
        except:
            return {"raw_output": content}

    except Exception as e:
        return {"error": str(e)}