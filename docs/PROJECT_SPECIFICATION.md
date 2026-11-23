# L&F MATCH — One-page Project Specification

## Problem and purpose
Campus help desks receive lost-property reports and maintain a register of found items. Manually comparing every report is slow. L&F MATCH uses Gemini to extract structured facts from each report and Python to suggest candidate pairs. It does not decide ownership.

## Inputs and outputs
Inputs: `data/lost.csv` and `data/found.csv`, each with at least 10 rows and columns `id,date,report`. Dates use `YYYY-MM-DD`.
Outputs: `matches.csv` (all suggestions, highest score first), `no_match.csv` (lost reports without a suggestion), `unclaimed.csv` (found reports without a suggestion), and `summary.txt` (counts and double claims).

## Extraction JSON
Each report is sent to Gemini once. It returns `item`, `colour`, `brand`, `place`, and `summary`. Item is one of phone, wallet, id_card, bottle, bag, earphones, keys, umbrella, calculator, watch, spectacles, other. Colour is one of black, white, red, blue, green, yellow, pink, brown, grey, orange, or null. Brand and place are the exact written values or null. Summary is at most eight words and contains no names. The configured campus place vocabulary can be edited in `config.py`.

## Validation and matching rules
Python validates the JSON and checks that colour, brand and place appear in the original report; unsupported values become null. The item categories must be equal; `other` never matches automatically. Reports more than 30 days apart do not match. If both reports provide a colour or brand and the values differ, the pair is rejected. Same colour adds 2, same brand adds 2, and same place adds 1. Scores of 3+ are likely; 1–2 are possible; 0 is not listed. Every found item suggested for multiple lost reports is flagged as a double claim.

## Human checkpoint
The program only recommends candidates. Before handing over an item, the help desk asks the claimant for a detail that is not present in either report and verifies it. A likely score is not proof of ownership.

## Safety and failure handling
The API key is stored in `.env`, never in source code. Invalid or unavailable Gemini responses use a conservative fallback and do not stop the full run. Report text is treated as untrusted input; instructions inside a report are not followed.
