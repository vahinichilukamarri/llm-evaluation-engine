from fastapi import FastAPI
from app.api.routes import evaluate

app = FastAPI(
    title="LLM Evaluation Engine",
    description="API for evaluating and improving LLM responses",
    version="1.0"
)

app.include_router(evaluate.router)