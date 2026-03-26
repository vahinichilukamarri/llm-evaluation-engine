from fastapi import APIRouter
from app.services.evaluator import evaluate_response, evaluate_multiple_responses

router = APIRouter()

# 🔹 Single response evaluation
@router.post("/evaluate")
def evaluate(data: dict):
    prompt = data.get("prompt")
    response = data.get("response")

    if not prompt or not response:
        return {"error": "Missing prompt or response"}

    result = evaluate_response(prompt, response)

    return result


# 🔹 Multiple responses evaluation
@router.post("/compare")
def compare(data: dict):
    prompt = data.get("prompt")
    responses = data.get("responses")

    if not prompt or not responses:
        return {"error": "Missing prompt or responses"}

    result = evaluate_multiple_responses(prompt, responses)

    return {"results": result}