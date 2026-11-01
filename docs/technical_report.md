# NiyamGate: Intent-Bound Safety Gateway for Agentic DPI Actions

**Track fit:** Technical build; Trust & Consent and System Resilience  
**Status:** Local simulation prototype  
**Prepared:** 1 November 2026

> **Timing note:** The submitting team reports that the deadline was extended and the form remains open. This prototype was prepared on 1 November 2026 during that extension. The public event page still displays the original 31 October date.

## Summary

NiyamGate is a small authorization gateway between an AI agent and tools that could initiate a payment or marketplace order. It treats the agent's proposal as untrusted, even when the model, prompt, or weights are public. A separate, short-lived user grant defines the allowed session, rail, action, recipient, purpose, amount, and aggregate budget. The gateway returns `ALLOW`, `REQUIRE_APPROVAL`, or `DENY`, explains the rule, and appends a hash-linked audit event. The current build is a local simulator with fictional data; it never calls a real DPI service.

## Problem

An agent can turn a broad request into a sequence of external actions. Prompt injection, compromised memory, or ordinary planning error can redirect a later step to an unintended recipient or purpose. A human-confirmed flow is difficult to preserve when the agent acts asynchronously across multiple tools. If authorization is encoded only in the agent prompt or hidden model behavior, an attacker who can inspect or alter that logic can target it.

The proposed control is to put a deterministic policy check at the action boundary. The agent may suggest an action, but it cannot expand the user's grant. This matches the hackathon's stated focus on safe agent behavior over India's public infrastructure and its emphasis on resilience when agent logic is public.

## Threat model

**Protected properties:** the user's delegated scope, recipient and purpose restrictions, transaction limits, replay resistance, and an explainable record of each decision.

**Adversary capabilities considered:** observe or manipulate the agent prompt; influence the agent to change a recipient, purpose, amount, tool, or session; repeat an earlier tool request; submit malformed fields; or trigger a fast sequence of individually small actions.

**Trust boundary:** the policy gate and the grant are separate from the agent. The demo signs a server-held grant with an ephemeral key and verifies its signature on every decision. The policy is not accepted from the action request.

**Out of scope:** a compromised gateway process or host, theft of the signing key, coercion of the user at the approval surface, compromise of a bank/DPI provider, production identity proofing, denial of service, and legal allocation of liability. The demo is not a security certification.

## Design

Each request carries a principal, session, rail, action, recipient, purpose, INR amount, idempotency key, nonce, and request identifier. The gate evaluates checks in fail-closed order:

1. Verify the grant signature and required request fields.
2. Reject an expired grant or a principal/session mismatch.
3. Require an allowed rail and action, then an exact recipient-purpose match.
4. Enforce positive amount, per-action cap, prior-use checks, and aggregate budget.
5. Apply a rolling per-minute action cap.
6. Require human approval above the unattended threshold; otherwise record an allow decision.

For a permitted simulated action, the gate consumes its idempotency key and nonce and adds the amount to its in-memory spend total. Approval-required and denied actions do not consume the grant. Every outcome produces a reason code and a SHA-256 hash linked to the previous audit event. The chain makes accidental edits detectable, but it is not immutable against an operator who can rewrite the entire local file or process state.

## Prototype and scenarios

`guard.py` implements the policy evaluator and seven deterministic scenarios. `app.py` serves a loopback-only JSON API using Python's standard library. `index.html` is a self-contained interface. Each scenario starts with a new synthetic grant and ledger.

| Scenario | Expected decision | Control illustrated |
|---|---|---|
| In-scope INR 120 payment | Allow | Exact session, recipient, purpose, and amount scope |
| Prompt-injection redirect to unknown recipient | Deny | Recipient/purpose allowlist is independent of agent intent |
| INR 320 payment | Require approval | Human approval above unattended threshold |
| Same request twice | Allow, then deny | Idempotency and nonce replay checks |
| Spend INR 200 + INR 200 + INR 400 | Allow, allow, then deny | Aggregate INR 750 budget |
| Valid action from another session | Deny | Session binding |
| INR 650 action | Deny | Per-action INR 500 cap |

These are designed scenarios, not benchmark results. No claim is made about false-positive rates, production throughput, or security against all prompt injection attacks. The key contribution is the explicit action-boundary pattern and its observable decision trace.

## Evaluation plan

Before any integration, run the fixtures in an isolated sandbox and add property-based and concurrency checks for: scope mismatch always denies; replay never authorizes twice; total accepted spend never exceeds the configured budget; expired grants fail closed; request mutations cannot alter the signed grant; and concurrent requests cannot both reserve the same budget. Measure decision latency, approval rates, rejected legitimate actions, and explanation clarity across representative languages and low-bandwidth conditions. A production design must reserve budget and idempotency state atomically in durable storage; this single-process simulator does not.

## DPI adoption path

Treat NiyamGate as a reference adapter, not a replacement for UPI, Aadhaar, ONDC, bank controls, or user authentication. A realistic next step is an observation-only adapter in an authorized sandbox: map each tool call to a canonical action, resolve a user-approved capability, evaluate a signed policy, and pass only permitted actions to a sandbox rail. Approval should use an institution-owned, accessible confirmation surface. Production deployment would need keys protected by a managed HSM, short-lived scoped credentials, durable atomic replay/budget storage, policy versioning and revocation, operational audit retention, and review by the relevant regulated entity and DPI operator.

Testing must remain in provided sandboxes or systems the team owns or has permission to test. This prototype includes no live endpoints and contains no Aadhaar, UPI, or ONDC credentials.

## Limitations and next steps

The key is ephemeral and process-local; all state resets on restart. The grant is a demo object rather than a user-facing consent ceremony. Approval is represented as a stop decision only; the demo does not implement an identity-verified approval channel. The rate and daily limits are in-memory and not atomic across instances. The examples cover a narrow payment/order model and English descriptions. The app has no authentication and should remain bound to localhost.

Next steps are a signed, revocable grant format; a one-time approval token bound to a canonical request hash; durable atomic reservations; sandbox adapter tests; multilingual and accessible explanations; and adversarial evaluation with independent reviewers.

## Provenance and disclosure

OpenAI ChatGPT (GPT-6) assisted with concept development, implementation drafting, and this report. The runtime uses Python's standard library and no external model, code package, or dataset. The demo data is fictional and authored for the scenarios. Any submission should disclose this AI use and the actual date and extent of team review.

## Reference

Secure AI Futures Lab, [India Agentic AI Security Hackathon](https://www.secureaifutureslab.com/events/india-ai-agentic-hackathon). The public event page describes the technical judging rubric, themes, deadline, AI-use disclosure, and responsible testing boundaries.

