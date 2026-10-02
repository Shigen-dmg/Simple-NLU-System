"""Small dialogue manager: learned intents, remembered slots, and local replies."""
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.entities import NUMBER_WORDS
from src.nlu import understand

INFO_PATH = Path(__file__).resolve().parents[1] / "data" / "restaurant_info.json"
QUESTIONS = {
    "date": "What date would you like? For example, tomorrow or next Friday.",
    "time": "What time would you like? For example, 7pm or 19:30.",
    "party_size": "How many people? You can say four or for 4 people.",
}


@dataclass
class ConversationState:
    """Only the current booking draft is remembered; no real reservation exists."""
    active: bool = False
    date: Optional[str] = None
    time: Optional[str] = None
    party_size: Optional[int] = None
    awaiting_confirmation: bool = False

    def missing_slot(self) -> Optional[str]:
        return next((name for name in QUESTIONS if getattr(self, name) is None), None)


def load_restaurant_info() -> Dict[str, Any]:
    """Read editable local information without inventing restaurant facts."""
    with INFO_PATH.open() as handle:
        return json.load(handle)


class DialogueManager:
    """Keep one conversation's state; independent instances never share memory."""

    def __init__(self, state: Optional[ConversationState] = None,
                 restaurant_info: Optional[Dict[str, Any]] = None):
        self.state = ConversationState(**asdict(state)) if state else ConversationState()
        self.restaurant_info = load_restaurant_info() if restaurant_info is None else restaurant_info

    def respond(self, text: str, reference_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze a turn and return a reply, updated state, and original NLU output.

        Control phrases (yes/no/reset) and bare counts are dialogue rules, not
        replacements for the trained classifier. Raw NLU confidence is preserved.
        """
        result = understand(text, reference_time=reference_time)
        normalized = re.sub(r"[.!?]+$", "", text.strip().lower()).strip()
        handled_as = "intent"

        if normalized in {"reset", "start over", "cancel", "never mind", "nevermind"}:
            self.state = ConversationState()
            reply = "Okay, I cleared the conversation draft. How can I help?"
            handled_as = "control"
        elif self.state.awaiting_confirmation and normalized in {"yes", "y", "confirm", "yes please", "okay", "ok"}:
            draft = self._slots()
            self.state = ConversationState()
            reply = (f"Demo booking draft confirmed: {draft['party_size']} people on "
                     f"{draft['date']} at {draft['time']}. No real reservation has been saved; "
                     "please contact the restaurant to book.")
            return {**result, "reply": reply, "handled_as": "confirmation",
                    "state": asdict(self.state), "booking_draft": draft}
        elif self.state.awaiting_confirmation and normalized in {"no", "n", "no thanks"}:
            self.state = ConversationState()
            reply = "Okay, I discarded the draft. You can start a new booking anytime."
            handled_as = "confirmation"
        elif result["intent"] in {"opening_hours", "view_menu", "restaurant_location", "greeting"}:
            reply = self._information_reply(result["intent"])
            if self.state.active:
                reply += " " + self._booking_prompt()
        elif result["intent"] == "goodbye":
            self.state = ConversationState()
            reply = "Goodbye! Thanks for chatting."
        elif result["intent"] == "cancel_booking":
            was_active = self.state.active
            self.state = ConversationState()
            reply = ("I cleared your current draft. " if was_active else "") + (
                "I can't cancel an existing reservation here. Please contact the restaurant to cancel it."
            )
        elif result["intent"] == "modify_booking" and not self.state.active:
            reply = ("I can't change a saved reservation here. Please contact the restaurant. "
                     "If you'd like to prepare a new draft, say 'book a table'.")
        elif result["intent"] == "restaurant_booking" or self.state.active:
            if not self.state.active:
                self.state = ConversationState(active=True)
            entities = dict(result["entities"])
            # A standalone number answers only a pending party-size question.
            if self.state.missing_slot() == "party_size":
                count = self._bare_count(normalized)
                if count is not None:
                    entities["party_size"] = count
            if entities:
                for key, value in entities.items():
                    setattr(self.state, key, value)
                self.state.awaiting_confirmation = False
                reply = self._booking_prompt()
                handled_as = "booking_details"
            elif result["intent"] in {"restaurant_booking", "modify_booking"}:
                reply = self._booking_prompt()
            else:
                reply = "I didn't understand that booking detail. " + self._booking_prompt()
                handled_as = "clarification"
        else:
            reply = ("I'm not sure what you mean. I can help prepare a table-booking draft "
                     "or answer questions about the menu, hours, and location. Could you rephrase?")
            handled_as = "clarification"
        return {**result, "reply": reply, "handled_as": handled_as, "state": asdict(self.state)}

    @staticmethod
    def _bare_count(text: str) -> Optional[int]:
        match = re.fullmatch(r"(\d{1,3}|" + "|".join(NUMBER_WORDS) + r")(?:\s+(?:people|guests))?", text)
        if not match:
            return None
        raw = match.group(1)
        count = int(raw) if raw.isdigit() else NUMBER_WORDS[raw]
        return count if count > 0 else None

    def _slots(self) -> Dict[str, Any]:
        return {key: getattr(self.state, key) for key in QUESTIONS}

    def _booking_prompt(self) -> str:
        missing = self.state.missing_slot()
        if missing:
            return QUESTIONS[missing]
        self.state.awaiting_confirmation = True
        return (f"A table for {self.state.party_size} on {self.state.date} at {self.state.time}. "
                "Confirm this demo draft? Say yes or no, or give corrected details. "
                "This does not reserve a real table.")

    def _information_reply(self, intent: str) -> str:
        info = self.restaurant_info
        if intent == "greeting":
            return "Hello! I can help with a table-booking draft, menu, opening hours, or location."
        if intent == "opening_hours":
            hours = info.get("opening_hours")
            return f"Our opening hours: {hours}" if hours else "Opening hours haven't been configured yet."
        if intent == "restaurant_location":
            address = info.get("address")
            return f"You can find us at {address}." if address else "The restaurant address hasn't been configured yet."
        menu = info.get("menu")
        return "On the menu: " + "; ".join(menu) + "." if menu else "The menu hasn't been configured yet."
