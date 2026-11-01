# Form copy — review before use

## Project title

NiyamGate: Intent-Bound Safety Gateway for Agentic DPI Actions

## Description for the website

NiyamGate is a local simulator for a policy gateway between an AI agent and DPI-facing tools. It checks each proposed payment or marketplace order against a separate, time-limited user grant for session, rail, recipient, purpose, amount, and aggregate budget. It detects replayed requests, limits action velocity, requests human approval above a threshold, and records hash-linked decision evidence. Scenarios demonstrate how the same controls respond to an in-scope action, a prompt-injection redirect, replay, and budget exhaustion. The prototype uses fictional data and does not connect to live UPI, Aadhaar, ONDC, banks, or external services.

## Problem addressed

Agents can act across several steps with limited human oversight, while India's DPI systems were designed around human-confirmed interactions. Prompt injection, compromised memory, or planning errors can redirect an action after the user has delegated a task. NiyamGate places deterministic, inspectable authorization at the tool boundary so the agent cannot expand the user's recipient, purpose, amount, or session scope.

## Technical report

Attach `docs/technical_report.md`.

## AI tools used, and what for

OpenAI ChatGPT (GPT-6) assisted with the initial project concept, Python and browser-demo implementation, technical report, and submission text. The runtime does not call an AI model.

## External code, models, or datasets used

None. The project uses Python's standard library only. Scenario data is fictional and created for this prototype.

## Submission note

Prepared on 1 November 2026 during the deadline extension reported for the form.

