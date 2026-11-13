"""Extract action and target signals from English prompts for the rule pilot."""

import re
import unicodedata
from dataclasses import dataclass

EXECUTE = re.compile(
    r"\b(?:run|execute|install|deploy|launch|enable|disable|bypass|hack(?:ing)?|"
    r"escalate|hijack|infect|encrypt|crack|steal|wipe|delete|"
    r"gain\s+(?:root|sudo|admin(?:istrator)?)\s+access)\b"
    r"|\b(?:write|build|create|develop|implement)\b.{0,50}\b"
    r"(?:malware|ransomware|keyloggers?|password\s+crackers?)\b",
    re.IGNORECASE | re.DOTALL,
)
SYSTEM_CRITICAL = re.compile(
    r"\b(?:sudo|root\s+access|admin(?:istrator)?\s+(?:access|privileges)|"
    r"system\s+(?:files|services|logs|registry)|antivirus|firewall|"
    r"corporate\s+network|servers?|atm(?:s|\s+machines?)?|"
    r"passwords?|keyloggers?|ransomware|malware)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Signals:
    action: str
    target: str


def extract(text: str) -> Signals:
    normalized = unicodedata.normalize("NFKC", text)
    return Signals(
        action="Execute" if EXECUTE.search(normalized) else "Unrecognized",
        target="System_Critical" if SYSTEM_CRITICAL.search(normalized) else "Unrecognized",
    )
