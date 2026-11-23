# L&F MATCH

**AI-powered Lost and Found Matching System** — Python + Google Gemini.

L&F MATCH reads campus lost/found CSV reports, uses Gemini to extract structured details once per report, validates the extraction against the original text, compares every lost report with every found report using Python, and writes four output files.

> The system suggests candidates. It never decides ownership. The help desk must verify a claimant using a detail absent from both reports.

## 1. Requirements
- Python 3.10 or newer (Python 3.12 recommended)
- Google Gemini API key
- Internet connection for Gemini extraction

## 2. Setup (Windows PowerShell)
```powershell
cd path\to\LF_MATCH
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Open `.env` and replace the placeholder with your own Gemini API key. Never paste the key into Python files or commit `.env` to Git.

## 3. Configure
- Put at least 10 lost reports in `data/lost.csv`.
- Put at least 10 found reports in `data/found.csv`.
- Keep the columns exactly `id,date,report`.
- Use dates in `YYYY-MM-DD` format.
- Adjust `CAMPUS_PLACES` in `config.py` to the campus's approved place vocabulary.
- Optional: change `GEMINI_MODEL` in `.env` to a model available to your API key.

## 4. Run
```powershell
python main.py
```
The program creates:
- `outputs/matches.csv`
- `outputs/no_match.csv`
- `outputs/unclaimed.csv`
- `outputs/summary.txt`

Each unchanged report is sent to Gemini once. Successful extractions are saved in an ignored local cache at `outputs/extraction_cache.json`, so rerunning the project does not repeat those API calls. If Gemini returns a temporary 429/503 error, the client retries with a delay and spaces requests to stay below the 15-requests-per-minute limit observed in the supplied run. If Gemini remains unavailable or returns invalid data, the program uses a conservative fallback and continues. Check the console for retry/fallback warnings.

## 5. Run the evaluation and red-team tests
```powershell
python tests/eval_harness.py
```
The harness checks five expected match levels and three red-team scenarios. Run it from the project root.

## 6. Project structure
```text
LF_MATCH/
├── config.py
├── gemini_client.py
├── main.py
├── matching.py
├── system_prompt.py
├── validator.py
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   ├── lost.csv
│   └── found.csv
├── outputs/
├── tests/
│   └── eval_harness.py
└── docs/
    ├── PROJECT_SPECIFICATION.md
    ├── JUDGMENT_FRAMEWORK.md
    ├── COST_AND_LATENCY.md
    ├── AI_DECISION_JOURNAL.md
    └── REFLECTION.md
```

## 7. Matching rules
- Same item category is required; `other` never matches automatically.
- Reports more than 30 days apart are excluded.
- If both reports provide different colours or different brands, the pair is excluded.
- Same colour: +2; same brand: +2; same place: +1.
- 3 or more: likely; 1–2: possible; 0: not listed.
- A found item suggested for multiple lost reports is flagged as a double claim.

## 8. GitHub checklist
```powershell
git init
git add .
git status
git commit -m "Create L&F MATCH project structure and specification"
git add main.py matching.py validator.py
git commit -m "Build Gemini extraction and Python matching engine"
git add tests docs README.md data
git commit -m "Add evaluation, red-team tests and project documentation"
```
Before pushing, check `git status` and confirm `.env` is not tracked.

## 9. Important limitations
- The campus-place vocabulary in `config.py` is a starter list; update it for your campus.
- The sample CSVs are demonstration data, not real campus records.
- The fallback is intentionally conservative and may not extract colour, brand or place.
- Gemini model availability, quotas, latency and pricing can change. Check Google's current documentation.
- A suggested match is not proof of ownership. A staff member must verify an independent detail before handover.
