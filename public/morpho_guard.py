"""Apply the structural pilot's prompt-level gate before model generation."""

from dataclasses import asdict

if __package__:
    from .graph_builder import extract
else:
    from graph_builder import extract

RULE_VERSION = "regex-gate-v1"


def evaluate_gate(text: str, *, verified_authorization: bool = False) -> dict:
    """Authorization must be supplied by the caller's trusted context."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("A non-empty prompt is required")
    if type(verified_authorization) is not bool:
        raise TypeError("verified_authorization must be a boolean")
    signals = extract(text)
    triggered = (
        signals.action == "Execute"
        and signals.target == "System_Critical"
        and not verified_authorization
    )
    return {
        **asdict(signals),
        "authorization": "Verified" if verified_authorization else "Unverified",
        "triggered": triggered,
    }
