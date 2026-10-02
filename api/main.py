"""Local FastAPI endpoints for the NLU pipeline."""
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from src.nlu import understand

app = FastAPI(title="Simple NLU API")


class UnderstandRequest(BaseModel):
    """A nonempty sentence, limited to 2000 characters."""
    text: str = Field(min_length=1, max_length=2000)

    @field_validator("text")
    @classmethod
    def reject_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text must not be blank.")
        return value


@app.get("/")
def root() -> Dict[str, str]:
    return {"name": "Simple NLU API", "status": "running"}


@app.post("/understand")
def understand_sentence(request: UnderstandRequest) -> Dict[str, Any]:
    try:
        result = understand(request.text)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {key: result[key] for key in ("intent", "confidence", "entities")}
