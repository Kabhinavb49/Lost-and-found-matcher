"""Plain-Python comparison and scoring engine."""
from datetime import datetime
from collections import defaultdict
from config import LIKELY_THRESHOLD, MAX_DATE_GAP_DAYS

def _date_gap_days(lost_date: str, found_date: str):
    try:
        a = datetime.strptime(lost_date, "%Y-%m-%d").date()
        b = datetime.strptime(found_date, "%Y-%m-%d").date()
        return abs((a - b).days)
    except (TypeError, ValueError):
        return None

def score_pair(lost: dict, found: dict):
    """Return (score, reasons, level); None level means not suggested."""
    ld, fd = lost["details"], found["details"]

    if ld["item"] == "other" or fd["item"] == "other":
        return 0, ["Automatic matching is disabled for 'other' items."], None
    if ld["item"] != fd["item"]:
        return 0, ["Different item categories."], None

    gap = _date_gap_days(lost["date"], found["date"])
    if gap is None or gap > MAX_DATE_GAP_DAYS:
        return 0, ["Dates are invalid or more than 30 days apart."], None

    # A mismatch is a hard exclusion, not a score deduction.
    for field, label in (("colour", "colour"), ("brand", "brand")):
        a, b = ld.get(field), fd.get(field)
        if a and b and str(a).casefold() != str(b).casefold():
            return 0, [f"Different {label}: {a} vs {b}."], None

    score, reasons = 0, []
    for field, points, label in (
        ("colour", 2, "Same colour"),
        ("brand", 2, "Same brand"),
        ("place", 1, "Same place"),
    ):
        a, b = ld.get(field), fd.get(field)
        if a and b and str(a).casefold() == str(b).casefold():
            score += points
            reasons.append(f"{label} (+{points})")

    if score >= LIKELY_THRESHOLD:
        level = "likely"
    elif score >= 1:
        level = "possible"
    else:
        return 0, ["No matching colour, brand or place evidence."], None

    if not reasons:
        reasons = ["Same item category and within 30 days; no extra evidence."]
    return score, reasons, level

def find_matches(lost_reports: list, found_reports: list):
    """Compare every lost report with every found report."""
    suggestions = []
    matched_lost_ids, matched_found_ids = set(), set()
    found_claims = defaultdict(set)

    for lost in lost_reports:
        for found in found_reports:
            score, reasons, level = score_pair(lost, found)
            if level:
                suggestions.append({
                    "lost_id": lost["id"],
                    "found_id": found["id"],
                    "lost_date": lost["date"],
                    "found_date": found["date"],
                    "score": score,
                    "level": level,
                    "reasons": "; ".join(reasons),
                    "human_verification_required": "YES",
                })
                matched_lost_ids.add(lost["id"])
                matched_found_ids.add(found["id"])
                found_claims[found["id"]].add(lost["id"])

    suggestions.sort(key=lambda x: (-x["score"], x["lost_id"], x["found_id"]))
    double_claims = {
        found_id: sorted(lost_ids)
        for found_id, lost_ids in found_claims.items()
        if len(lost_ids) > 1
    }
    return suggestions, matched_lost_ids, matched_found_ids, double_claims
