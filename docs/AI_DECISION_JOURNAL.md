# AI Decision Journal

| Decision | Reason | Risk considered | Control |
|---|---|---|---|
| Use Gemini only for extraction | LLM is useful for interpreting natural-language reports | Model can guess missing details | Explicit null rules and Python fact-check |
| One request per report | Avoids repeated calls for every possible pair | API latency or quota | L+F call estimate and fallback |
| Python performs matching | Rules must be predictable and explainable | Coding mistakes | Separate functions and evaluation harness |
| Hard reject colour/brand clashes | Contradictory facts should not be outweighed by points | Extraction error can cause false rejection | Original report remains available for staff review |
| Never auto-assign ownership | Similar descriptions do not prove ownership | Incorrect handover | Human asks for an independent detail |
| Keep API key in environment | Prevent accidental credential exposure | Key committed to Git | `.env` ignored by Git; `.env.example` has placeholder only |
