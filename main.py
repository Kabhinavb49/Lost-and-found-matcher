"""Command-line entry point for L&F MATCH."""
import csv
import json
import hashlib
from pathlib import Path
from config import LOST_FILE, FOUND_FILE, OUTPUT_DIR
from matching import find_matches

def read_report(file_path: Path) -> list:
    """Read CSV rows and return report dictionaries."""
    reports = []
    with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        required = {"id", "date", "report"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"{file_path.name} must contain id,date,report columns.")
        for row in reader:
            if row.get("id") and row.get("date") and row.get("report"):
                reports.append({
                    "id": row["id"].strip(),
                    "date": row["date"].strip(),
                    "report": row["report"].strip(),
                })
    return reports

def conservative_fallback(report_text: str) -> dict:
    """Safe offline fallback: only identify obvious item words; never guess details."""
    text = report_text.lower()
    item_terms = {
        "phone": ["phone", "mobile"],
        "wallet": ["wallet", "purse"],
        "id_card": ["id card", "identity card"],
        "bottle": ["bottle"],
        "bag": ["bag", "backpack"],
        "earphones": ["earphones", "headphones", "earbuds"],
        "keys": ["keys", "key"],
        "umbrella": ["umbrella"],
        "calculator": ["calculator"],
        "watch": ["watch"],
        "spectacles": ["spectacles", "glasses"],
    }
    found_item = "other"
    for item, terms in item_terms.items():
        if any(term in text for term in terms):
            found_item = item
            break
    return {
        "item": found_item, "colour": None, "brand": None,
        "place": None, "summary": "Needs manual report review"
    }

CACHE_FILE = OUTPUT_DIR / "extraction_cache.json"


def _cache_key(report: dict) -> str:
    """Create a stable key so unchanged reports do not consume API calls again."""
    raw = f"{report['id']}|{report['date']}|{report['report']}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_extraction_cache() -> dict:
    """Read previously successful Gemini extractions."""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError):
        print("[Warning] Extraction cache could not be read; starting a new cache.")
        return {}


def save_extraction_cache(cache: dict) -> None:
    """Persist successful extractions after each report."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = CACHE_FILE.with_suffix(".tmp")
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(cache, file, indent=2, ensure_ascii=False)
    temp_file.replace(CACHE_FILE)


def enrich_reports(reports: list, label: str) -> list:
    """Reuse cached extractions; call Gemini for new reports and retry failures."""
    from gemini_client import extract_report
    enriched = []
    cache = load_extraction_cache()
    for index, report in enumerate(reports, start=1):
        key = _cache_key(report)
        print(f"[{label}] Processing {report['id']} ({index}/{len(reports)})...")
        if key in cache:
            details = cache[key]
            status = "Cache"
            print("  [Cache] Reusing saved Gemini extraction.")
        else:
            try:
                details = extract_report(report["report"])
                status = "Gemini"
                cache[key] = details
                save_extraction_cache(cache)
            except Exception as exc:
                print(f"  [Fallback] {exc}")
                details = conservative_fallback(report["report"])
                status = "Fallback"
        enriched.append({**report, "details": details, "extraction_source": status})
    return enriched

def write_reports(lost_reports, found_reports, suggestions,
                  matched_lost_ids, matched_found_ids, double_claims):
    """Write the four required output files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_DIR / "matches.csv", "w", newline="", encoding="utf-8") as f:
        fields = ["lost_id", "found_id", "lost_date", "found_date", "score",
                  "level", "reasons", "human_verification_required"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(suggestions)

    with open(OUTPUT_DIR / "no_match.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "report"])
        writer.writeheader()
        writer.writerows([
            {"id": r["id"], "date": r["date"], "report": r["report"]}
            for r in lost_reports if r["id"] not in matched_lost_ids
        ])

    with open(OUTPUT_DIR / "unclaimed.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "report"])
        writer.writeheader()
        writer.writerows([
            {"id": r["id"], "date": r["date"], "report": r["report"]}
            for r in found_reports if r["id"] not in matched_found_ids
        ])

    with open(OUTPUT_DIR / "summary.txt", "w", encoding="utf-8") as f:
        f.write("L&F MATCH — RUN SUMMARY\n")
        f.write("=======================\n")
        f.write(f"Lost reports: {len(lost_reports)}\n")
        f.write(f"Found reports: {len(found_reports)}\n")
        f.write(f"Suggested pairs: {len(suggestions)}\n")
        f.write(f"Lost reports with no suggestion: {len(lost_reports) - len(matched_lost_ids)}\n")
        f.write(f"Unclaimed found items: {len(found_reports) - len(matched_found_ids)}\n")
        f.write(f"Double-claim items: {len(double_claims)}\n\n")
        f.write("DOUBLE-CLAIM REVIEW\n")
        f.write("-------------------\n")
        if double_claims:
            for found_id, lost_ids in sorted(double_claims.items()):
                f.write(f"{found_id} is suggested for: {', '.join(lost_ids)}\n")
        else:
            f.write("No double claims detected.\n")
        f.write("\nHUMAN CHECKPOINT: The help desk must ask each claimant for a\n")
        f.write("detail that is not present in either report before handing over an item.\n")

def main():
    try:
        lost_raw = read_report(LOST_FILE)
        found_raw = read_report(FOUND_FILE)
        if len(lost_raw) < 10 or len(found_raw) < 10:
            raise ValueError("The project requires at least 10 lost and 10 found reports.")
        print(f"Loaded {len(lost_raw)} lost and {len(found_raw)} found reports.")
        print("Extracting each report once...")
        lost = enrich_reports(lost_raw, "LOST")
        found = enrich_reports(found_raw, "FOUND")
        suggestions, lost_ids, found_ids, double_claims = find_matches(lost, found)
        write_reports(lost, found, suggestions, lost_ids, found_ids, double_claims)
        print("\nMatching complete.")
        print(f"Suggested pairs: {len(suggestions)}")
        print(f"Double-claim items: {len(double_claims)}")
        print(f"Output folder: {OUTPUT_DIR}")
        print("Review matches.csv; suggestions are not proof of ownership.")
    except (OSError, ValueError, csv.Error) as exc:
        print(f"[ERROR] {exc}")

if __name__ == "__main__":
    main()
