"""Validation and report-text fact checking."""
import re
from config import ALLOWED_ITEMS, ALLOWED_COLOURS, CAMPUS_PLACES

REQUIRED_KEYS = {"item", "colour", "brand", "place", "summary"}

def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()

def check_facts(data: dict, report_text: str) -> dict:
    """Null any colour, brand or place not supported by report text."""
    source = normalize_text(report_text)
    checked = dict(data)

    colour = checked.get("colour")
    if colour and colour.lower() not in source:
        checked["colour"] = None

    brand = checked.get("brand")
    if brand and normalize_text(str(brand)) not in source:
        checked["brand"] = None

    place = checked.get("place")
    if place and normalize_text(str(place)) not in source:
        checked["place"] = None

    return checked

def is_valid(data: dict) -> bool:
    """Check required keys and allowed field values."""
    if not isinstance(data, dict) or set(data.keys()) != REQUIRED_KEYS:
        return False
    if data["item"] not in ALLOWED_ITEMS:
        return False
    if data["colour"] is not None and str(data["colour"]).lower() not in ALLOWED_COLOURS:
        return False
    if data["brand"] is not None and not isinstance(data["brand"], str):
        return False
    if data["place"] is not None and not isinstance(data["place"], str):
        return False
    if not isinstance(data["summary"], str):
        return False
    if len(data["summary"].split()) > 8:
        return False
    return True

def validate_extraction(data: dict, report_text: str) -> dict:
    """Normalize, fact-check and validate an LLM result."""
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object.")
    # Keep exactly the expected keys; missing keys are rejected.
    if set(data.keys()) != REQUIRED_KEYS:
        raise ValueError(f"Expected keys: {sorted(REQUIRED_KEYS)}")
    data = dict(data)
    if data["item"] is not None:
        data["item"] = str(data["item"]).lower().strip()
    if data["colour"] is not None:
        data["colour"] = str(data["colour"]).lower().strip()
    if data["place"] is not None:
        data["place"] = str(data["place"]).lower().strip()
    if data["brand"] is not None:
        data["brand"] = str(data["brand"]).strip()
    data["summary"] = str(data["summary"]).strip()
    data = check_facts(data, report_text)

    # Place must be from the configured campus vocabulary and explicitly written.
    if data["place"] and data["place"] not in CAMPUS_PLACES:
        data["place"] = None

    if not is_valid(data):
        raise ValueError("Returned fields did not pass validation.")
    return data
