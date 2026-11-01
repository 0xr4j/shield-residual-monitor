"""Deterministic policy gate for fictional, local DPI-style actions."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import hmac
import json
import secrets
from typing import Any


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True)
class Grant:
    grant_id: str
    subject_id: str
    session_id: str
    issued_at: str
    expires_at: str
    allowed_rails: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    recipients: dict[str, tuple[str, ...]]
    max_single_inr: str
    daily_limit_inr: str
    approval_threshold_inr: str
    max_actions_per_minute: int
    signature: str = ""

    def payload(self) -> dict[str, Any]:
        value = asdict(self)
        value.pop("signature")
        return value


def sign_grant(grant: Grant, key: bytes) -> Grant:
    signature = hmac.new(key, _canonical(grant.payload()), hashlib.sha256).hexdigest()
    return Grant(**grant.payload(), signature=signature)


def demo_grant(key: bytes) -> Grant:
    now = datetime.now(timezone.utc)
    grant = Grant(
        grant_id="demo-grant-01",
        subject_id="user-demo-01",
        session_id="session-demo-01",
        issued_at=now.isoformat(),
        expires_at=(now + timedelta(hours=2)).isoformat(),
        allowed_rails=("UPI_SIM", "ONDC_SIM"),
        allowed_actions=("payment", "place_order"),
        recipients={
            "upi:chai-stand": ("tea",),
            "ondc:stationery-store": ("stationery",),
        },
        max_single_inr="500.00",
        daily_limit_inr="750.00",
        approval_threshold_inr="250.00",
        max_actions_per_minute=3,
    )
    return sign_grant(grant, key)


class PolicyGate:
    """Fail-closed evaluator. ALLOW records a simulation, never sends money."""

    def __init__(self, grant: Grant, key: bytes):
        self.grant = grant
        self.key = key
        self.spent = Decimal("0")
        self.idempotency_keys: set[str] = set()
        self.nonces: set[str] = set()
        self.accepted_at: list[datetime] = []
        self.audit: list[dict[str, Any]] = []

    def _record(self, request_id: str, decision: str, rule: str, detail: str) -> dict[str, Any]:
        previous = self.audit[-1]["hash"] if self.audit else "0" * 64
        entry: dict[str, Any] = {
            "request_id": request_id,
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "decision": decision,
            "rule": rule,
            "detail": detail,
            "previous_hash": previous,
        }
        entry["hash"] = hashlib.sha256(bytes.fromhex(previous) + _canonical(entry)).hexdigest()
        self.audit.append(entry)
        return entry

    def evaluate(self, raw: dict[str, Any]) -> dict[str, Any]:
        request_id = str(raw.get("request_id", "unknown"))[:80]
        expected_sig = hmac.new(self.key, _canonical(self.grant.payload()), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, self.grant.signature):
            result = self._record(request_id, "DENY", "POLICY_INTEGRITY", "Authorization policy signature is invalid.")
            return result

        required = ("principal_id", "session_id", "rail", "action", "recipient", "purpose", "amount_inr", "idempotency_key", "nonce")
        if not isinstance(raw, dict) or any(not isinstance(raw.get(k), str) or not raw[k] for k in required):
            result = self._record(request_id, "DENY", "MALFORMED_REQUEST", "Required action fields are missing or invalid.")
            return result
        try:
            amount = Decimal(raw["amount_inr"]).quantize(Decimal("0.01"))
            if not amount.is_finite():
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            return self._record(request_id, "DENY", "INVALID_AMOUNT", "Amount must be a finite INR value.")

        now = datetime.now(timezone.utc)
        try:
            expired = now >= datetime.fromisoformat(self.grant.expires_at)
        except ValueError:
            expired = True
        checks = [
            (expired, "GRANT_EXPIRED", "The user grant has expired."),
            (raw["principal_id"] != self.grant.subject_id or raw["session_id"] != self.grant.session_id,
             "CONTEXT_MISMATCH", "The request is outside the granted user session."),
            (raw["rail"] not in self.grant.allowed_rails or raw["action"] not in self.grant.allowed_actions,
             "ACTION_OUT_OF_SCOPE", "This rail or action is not in the grant."),
            (raw["purpose"] not in self.grant.recipients.get(raw["recipient"], ()),
             "RECIPIENT_OUT_OF_SCOPE", "Recipient and purpose do not match the user grant."),
            (amount <= 0, "INVALID_AMOUNT", "Amount must be greater than zero."),
            (amount > Decimal(self.grant.max_single_inr), "SINGLE_LIMIT", "Amount exceeds the per-action cap."),
            (raw["idempotency_key"] in self.idempotency_keys or raw["nonce"] in self.nonces,
             "REPLAY_DETECTED", "This request or nonce has already been authorized."),
            (self.spent + amount > Decimal(self.grant.daily_limit_inr),
             "DAILY_LIMIT", "The action would exceed the session's daily budget."),
        ]
        for failed, rule, detail in checks:
            if failed:
                return self._record(request_id, "DENY", rule, detail)

        self.accepted_at = [t for t in self.accepted_at if (now - t) < timedelta(minutes=1)]
        if len(self.accepted_at) >= self.grant.max_actions_per_minute:
            return self._record(request_id, "DENY", "VELOCITY_LIMIT", "Too many actions were authorized in one minute.")

        if amount > Decimal(self.grant.approval_threshold_inr):
            return self._record(request_id, "REQUIRE_APPROVAL", "HUMAN_APPROVAL", "A person must approve this exact action before execution.")

        self.idempotency_keys.add(raw["idempotency_key"])
        self.nonces.add(raw["nonce"])
        self.spent += amount
        self.accepted_at.append(now)
        return self._record(request_id, "ALLOW", "GRANT_MATCH", "Action fits the scoped grant; simulation only, no external action performed.")


SCENARIOS: dict[str, dict[str, Any]] = {
    "in_scope": {"title": "Within the grant", "summary": "Known recipient, stated purpose and a small amount.", "requests": [
        {"request_id": "pay-001", "principal_id": "user-demo-01", "session_id": "session-demo-01", "rail": "UPI_SIM", "action": "payment", "recipient": "upi:chai-stand", "purpose": "tea", "amount_inr": "120.00", "idempotency_key": "idem-001", "nonce": "nonce-001"}]},
    "prompt_redirect": {"title": "Prompt-injection redirect", "summary": "The agent is redirected to an unapproved recipient.", "requests": [
        {"request_id": "pay-002", "principal_id": "user-demo-01", "session_id": "session-demo-01", "rail": "UPI_SIM", "action": "payment", "recipient": "upi:attacker", "purpose": "urgent_fee", "amount_inr": "120.00", "idempotency_key": "idem-002", "nonce": "nonce-002"}]},
    "approval": {"title": "Approval threshold", "summary": "Within the hard cap, but above the amount that can run unattended.", "requests": [
        {"request_id": "pay-003", "principal_id": "user-demo-01", "session_id": "session-demo-01", "rail": "UPI_SIM", "action": "payment", "recipient": "upi:chai-stand", "purpose": "tea", "amount_inr": "320.00", "idempotency_key": "idem-003", "nonce": "nonce-003"}]},
    "replay": {"title": "Replayed request", "summary": "The same idempotency key and nonce are sent twice.", "requests": [
        {"request_id": "pay-004a", "principal_id": "user-demo-01", "session_id": "session-demo-01", "rail": "UPI_SIM", "action": "payment", "recipient": "upi:chai-stand", "purpose": "tea", "amount_inr": "80.00", "idempotency_key": "idem-004", "nonce": "nonce-004"},
        {"request_id": "pay-004b", "principal_id": "user-demo-01", "session_id": "session-demo-01", "rail": "UPI_SIM", "action": "payment", "recipient": "upi:chai-stand", "purpose": "tea", "amount_inr": "80.00", "idempotency_key": "idem-004", "nonce": "nonce-004"}]},
    "daily_budget": {"title": "Daily budget", "summary": "Two allowed actions consume INR 400; the next would cross the INR 750 cap.", "requests": [
        {"request_id": "pay-005a", "principal_id": "user-demo-01", "session_id": "session-demo-01", "rail": "UPI_SIM", "action": "payment", "recipient": "upi:chai-stand", "purpose": "tea", "amount_inr": "200.00", "idempotency_key": "idem-005a", "nonce": "nonce-005a"},
        {"request_id": "pay-005b", "principal_id": "user-demo-01", "session_id": "session-demo-01", "rail": "UPI_SIM", "action": "payment", "recipient": "upi:chai-stand", "purpose": "tea", "amount_inr": "200.00", "idempotency_key": "idem-005b", "nonce": "nonce-005b"},
        {"request_id": "pay-005c", "principal_id": "user-demo-01", "session_id": "session-demo-01", "rail": "UPI_SIM", "action": "payment", "recipient": "upi:chai-stand", "purpose": "tea", "amount_inr": "400.00", "idempotency_key": "idem-005c", "nonce": "nonce-005c"}]},
    "wrong_session": {"title": "Wrong session", "summary": "An otherwise valid action comes from a different session.", "requests": [
        {"request_id": "pay-006", "principal_id": "user-demo-01", "session_id": "session-other", "rail": "UPI_SIM", "action": "payment", "recipient": "upi:chai-stand", "purpose": "tea", "amount_inr": "50.00", "idempotency_key": "idem-006", "nonce": "nonce-006"}]},
    "single_cap": {"title": "Per-action cap", "summary": "The amount is above the grant's INR 500 hard limit.", "requests": [
        {"request_id": "pay-007", "principal_id": "user-demo-01", "session_id": "session-demo-01", "rail": "UPI_SIM", "action": "payment", "recipient": "upi:chai-stand", "purpose": "tea", "amount_inr": "650.00", "idempotency_key": "idem-007", "nonce": "nonce-007"}]},
}


def run_scenario(name: str) -> dict[str, Any]:
    scenario = SCENARIOS.get(name)
    if scenario is None:
        raise KeyError(name)
    key = secrets.token_bytes(32)
    gate = PolicyGate(demo_grant(key), key)
    results = [gate.evaluate(request) for request in scenario["requests"]]
    return {"title": scenario["title"], "summary": scenario["summary"], "results": results,
            "spent_inr": str(gate.spent), "audit_head": gate.audit[-1]["hash"] if gate.audit else None}

