# Cost and Latency Note

## API-call estimate
The program sends one Gemini request per report, not one request per lost/found pair. For L lost reports and F found reports, one full run requires approximately **L + F API calls**. With the sample data (10 lost + 10 found), that is **20 calls**. Python then compares L × F pairs locally (100 comparisons for the sample), with no additional Gemini calls.

## Latency
A text extraction request commonly takes a few seconds, but response time varies with model load, network conditions, report length and service limits. For the observed free-tier limit of 15 requests per minute, the application spaces requests by about 4.5 seconds. A first run with 20 distinct reports therefore takes at least about 86 seconds of pacing time, plus model response time and any retries. Successful extractions are cached, so an unchanged subsequent run can avoid those API calls. These are planning estimates, not service guarantees.

## Cost
The exact cost depends on the selected Gemini model, input/output token counts, current pricing and free-tier availability. Estimate it as:
`(input tokens × input-token price) + (output tokens × output-token price)`.
Check the current Google AI pricing page before submitting a numeric estimate. The project does not hard-code a price because provider pricing and free quotas can change.

## Cost controls
- Keep each report short and send it only once.
- Do not ask Gemini to compare every pair.
- Use Python for all pair comparisons.
- Store the model name in `.env` through `GEMINI_MODEL`.
