"""Local FastAPI endpoints for the NLU pipeline."""
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from src.nlu import understand
from src.dialogue import ConversationState, DialogueManager

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


# The client carries state between turns, so conversations do not share memory.


class ChatState(BaseModel):
    """A booking draft supplied by the client, never a saved reservation."""
    active: bool = False
    date: Optional[str] = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: Optional[str] = Field(default=None, pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    party_size: Optional[int] = Field(default=None, gt=0)
    awaiting_confirmation: bool = False

    @field_validator("date")
    @classmethod
    def valid_date(cls, value):
        if value is not None:
            from datetime import date
            date.fromisoformat(value)
        return value


class ChatRequest(UnderstandRequest):
    """Send the previous response's state to continue the same conversation."""
    state: ChatState = Field(default_factory=ChatState)


@app.post("/chat")
def chat(request: ChatRequest) -> Dict[str, Any]:
    state = ConversationState(**request.state.model_dump())
    if state.awaiting_confirmation and (
        not state.active or state.missing_slot() is not None
    ):
        raise HTTPException(status_code=422, detail="Confirmation requires an active, complete draft.")
    if not state.active:
        state = ConversationState()
    try:
        return DialogueManager(state).respond(request.text)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
