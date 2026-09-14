from pydantic import BaseModel, Field
from fastapi import FastAPI

try:
    from .graph import run_support_graph
except ImportError:
    from graph import run_support_graph


app = FastAPI(
    title="Zepto SupportAI API",
    version="1.0"
)


class AskRequest(BaseModel):
    query: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float = Field(
        ge=0.0,
        le=1.0
    )


@app.post(
    "/ask",
    response_model=AskResponse
)
def ask_question(request: AskRequest):

    result = run_support_graph(
        request.query
    )

    return AskResponse(
        answer=result["answer"],
        sources=result.get(
            "sources",
            []
        ),
        confidence=result.get(
            "confidence",
            1.0
        )
    )