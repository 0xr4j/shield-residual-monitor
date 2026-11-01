# NiyamGate

**Intent-bound authorization for agent-proposed DPI actions.** NiyamGate is a local, dependency-free simulator that checks proposed UPI-style payments and ONDC-style orders against a separate user grant. The demo focuses on the SAFL hackathon's Trust & Consent and System Resilience themes.

> **Prototype boundary:** fictional scenarios only. It does not connect to live UPI, Aadhaar, ONDC, banks, or any other external service. It is not production security software.

## Run locally

Requires Python 3.10 or newer. From this folder:

```powershell
python app.py
```

Open <http://127.0.0.1:8765>. Stop the local server with `Ctrl+C`. The app binds only to loopback and uses no third-party packages or external network calls.

## What it demonstrates

- A short-lived grant signed inside the gateway, separate from the agent's prompt and output.
- Exact session, rail, action, recipient, purpose, single-action, and aggregate-spend checks.
- A human-approval threshold for actions that exceed the unattended limit.
- One-use nonce and idempotency checks, plus a per-minute action cap.
- A hash-linked audit trail with a reason code for every decision.

Select a scenario in the browser to see the decision and audit evidence. Each scenario starts from a fresh fictional grant and in-memory ledger.

## Source map

- `guard.py` — signed grant, fail-closed policy evaluation, scenarios, and audit chain.
- `app.py` — loopback-only HTTP server and small JSON API.
- `index.html` — self-contained simulator UI.
- `docs/technical_report.md` — threat model, design, evaluation plan, limitations, and adoption path.
- `docs/submission_copy.md` — draft project description and form-field text.

## Important limitations

The demo's signing key, grant, replay store, velocity state, and budget live only in process memory; restart resets them. The hash chain is not an immutable audit store. The server is single-process and has no user authentication or integration adapter. A real deployment needs institution-controlled consent, durable atomic reservations, secure key custody, policy versioning, independent authorization, DPI sandbox testing, and legal/operational review. Never use this prototype to authorize a real transaction.

## AI assistance and provenance

OpenAI ChatGPT (GPT-6) assisted with the initial concept, implementation, and documentation. The scenarios and code in this repository were drafted for this project; no external code, model, or dataset is included. The runtime does not call an AI model.

## Submission timing

Prepared on 1 November 2026 during the deadline extension reported for the submission form. The public event page still displays the original 31 October date; use the updated form deadline.

