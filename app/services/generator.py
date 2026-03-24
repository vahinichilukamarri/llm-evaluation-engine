from groq import Groq
from app.config.settings import settings

# Initialize Groq client
client = Groq(api_key=settings.GROQ_API_KEY)


def generate_response(prompt, temperature):
    """
    Generate a single response from LLM
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=settings.GEN_MODEL,
            temperature=temperature
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating response: {str(e)}"


def generate_multiple_responses(prompt):
    """
    Generate multiple responses with different temperatures
    """

    temperatures = [0.0, 0.7, 1.2]
    responses = []

    for temp in temperatures:
        print(f"Generating response with temperature {temp}...")

        res = generate_response(prompt, temp)

        responses.append({
            "response": res,
            "temperature": temp
        })

    return responses