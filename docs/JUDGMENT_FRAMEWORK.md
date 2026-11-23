# Judgment Framework

| Stage | What the system does | What can go wrong? | Human checkpoint / decision |
|---|---|---|---|
| Report intake | Reads report ID, date and text from CSV | Missing or malformed rows | Help desk corrects source records |
| AI extraction | Gemini extracts item, colour, brand, place and summary | Hallucinated or malformed fields | Python validator checks format and source text |
| Fact checking | Removes unsupported colour, brand and place | A real detail may be phrased differently | Staff can inspect original report; do not manually invent a value |
| Matching | Python compares every lost report with every found report | Similar items may belong to different people | Treat results only as candidate suggestions |
| Scoring | Adds points for matching colour, brand and place | Missing details can reduce confidence | Staff reviews reasons and original descriptions |
| Double claims | Flags a found item suggested for multiple lost reports | Multiple people may plausibly claim the same item | Help desk investigates every claimant |
| Item handover | System does not authorize handover | Wrong person may claim an item | **Required checkpoint:** ask the claimant for a detail not present in either report, verify it, then decide whether to hand over |

## Three judgment questions
1. **What does the AI decide?** It only structures text into fields. It does not determine identity or ownership.
2. **What does Python decide?** It applies explicit validation, date, mismatch and scoring rules to generate suggestions.
3. **What must a person decide?** Whether a claimant is the rightful owner. The help desk must verify an additional detail absent from both reports before handover.
