"""Extract a small, explicit set of restaurant entities without an AI service."""
import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

import dateparser

NUMBER_WORDS = dict(zip(
    "one two three four five six seven eight nine ten eleven twelve".split(), range(1, 13)
))
NUMBER = r"(?:\d+|" + "|".join(NUMBER_WORDS) + r")"
PARTY_PATTERN = re.compile(
    rf"\b(?:party\s+of\s+(?P<party>{NUMBER})\b|"
    rf"table\s+for\s+(?P<table>{NUMBER})\b|"
    rf"for\s+(?P<people>{NUMBER})\s+(?:people|persons|guests|diners)\b)", re.I
)
TIME_PATTERN = re.compile(
    r"\b(?:(?:1[0-2]|0?[1-9])(?::[0-5]\d)?\s*[ap]m\b|"
    r"(?:[01]?\d|2[0-3]):[0-5]\d\b|noon\b|midnight\b)", re.I
)
WEEKDAY = r"monday|tuesday|wednesday|thursday|friday|saturday|sunday"
MONTH = (r"january|february|march|april|may|june|july|august|september|"
         r"october|november|december")
DATE_PATTERN = re.compile(
    rf"\b(?:day after tomorrow|tomorrow|tonight|today|"
    rf"(?:next\s+)?(?:{WEEKDAY})|\d{{4}}-\d{{2}}-\d{{2}}|"
    rf"(?:{MONTH})\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?|"
    rf"\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{MONTH})(?:\s+\d{{4}})?)\b", re.I
)


def extract_entities(text: str, reference_time: Optional[datetime] = None,
                     timezone: str = "Asia/Singapore") -> Dict[str, Any]:
    """Return recognized entities; use an injectable local clock for testing.

    'next Friday' means Friday in the next calendar week (Monday–Sunday).
    An unqualified weekday means its next occurrence, including today.
    """
    if not isinstance(text, str):
        raise ValueError("Text must be a string.")
    zone = ZoneInfo(timezone)
    base = reference_time or datetime.now(zone)
    if base.tzinfo is not None:
        base = base.astimezone(zone)
    base = base.replace(tzinfo=None)
    settings = {"RELATIVE_BASE": base, "PREFER_DATES_FROM": "future"}
    entities: Dict[str, Any] = {}
    match = DATE_PATTERN.search(text)
    if match:
        phrase = match.group().lower()
        if phrase == "tonight":
            phrase = "today"
        # dateparser does not reliably support 'next Friday'; anchor the weekday.
        if re.fullmatch(rf"next\s+(?:{WEEKDAY})", phrase):
            next_monday = base + timedelta(days=7 - base.weekday())
            weekday_index = WEEKDAY.split("|").index(phrase.split()[-1])
            candidate = next_monday + timedelta(days=weekday_index)
            parsed = dateparser.parse(candidate.date().isoformat(), languages=["en"], settings=settings)
        elif re.fullmatch(WEEKDAY, phrase):
            # Parsing weekdays as future can skip today; make our policy explicit.
            weekdays = WEEKDAY.split("|")
            candidate = base + timedelta(days=(weekdays.index(phrase) - base.weekday()) % 7)
            parsed = dateparser.parse(candidate.date().isoformat(), languages=["en"], settings=settings)
        else:
            parsed = dateparser.parse(phrase, languages=["en"], settings=settings)
        if parsed is not None:
            entities["date"] = parsed.date().isoformat()
    match = TIME_PATTERN.search(text)
    if match:
        phrase = match.group().lower()
        phrase = {"noon": "12:00", "midnight": "00:00"}.get(phrase, phrase)
        parsed = dateparser.parse(phrase, languages=["en"], settings=settings)
        if parsed is not None:
            entities["time"] = parsed.strftime("%H:%M")
    match = PARTY_PATTERN.search(text)
    if match:
        raw = next(value for value in match.groupdict().values() if value).lower()
        size = int(raw) if raw.isdigit() else NUMBER_WORDS[raw]
        if size > 0:
            entities["party_size"] = size
    return entities
