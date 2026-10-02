"""Combine intent prediction and independent entity extraction; run the CLI."""
from datetime import datetime
from typing import Any, Dict, Optional

from src.entities import extract_entities
from src.predict import predict_intent


def understand(text: str, threshold: Optional[float] = None,
               reference_time: Optional[datetime] = None) -> Dict[str, Any]:
    """Convert a sentence into an intent, confidence, and recognized entities."""
    prediction = predict_intent(text, threshold=threshold)
    return {"text": text, **prediction,
            "entities": extract_entities(text, reference_time=reference_time)}


def main() -> None:
    """Read sentences until exit, EOF, or Ctrl+C."""
    # Import here to keep understand() usable independently of the dialogue layer.
    from src.dialogue import DialogueManager

    bot = DialogueManager()
    print('Simple NLU\nType "exit" to quit, or "reset" to clear the conversation.\n')
    while True:
        try:
            text = input("You: ")
            if text.strip().lower() == "exit":
                break
            result = bot.respond(text)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        except FileNotFoundError as error:
            print(error)
            break
        except ValueError as error:
            print(error)
            continue
        print(f"Bot: {result['reply']}\n")
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']:.0%}\n")
        print("Entities:")
        for name, value in result["entities"].items():
            print(f"{name.replace('_', ' ').capitalize()}: {value}")
        if not result["entities"]:
            print("None found")
        print()


if __name__ == "__main__":
    main()
