"""Deterministic topic, sensitivity, and scope classification for corpus files.

Classification is keyword-based and fully deterministic: the same title + text
sample always yields the same labels. It runs at the *document* level (title plus
a leading text sample) and the labels propagate to every chunk of that document,
which keeps a book's sensitivity stable across all its passages.

Sensitivity is the dual-use axis the governance layer gates on:

* ``offensive``  — oriented toward building malware / evasion (virus/rootkit/
  botnet construction, AV bypass, shellcode). Escalated by default.
* ``dual_use``   — offensive-security tradecraft with legitimate defensive and
  pentest use (Metasploit, Kali, exploitation, social engineering).
* ``educational`` — programming, defensive security, certifications, theory.
"""

from __future__ import annotations

# --- Sensitivity markers (checked most-severe first) --------------------------

_OFFENSIVE_MARKERS: tuple[str, ...] = (
    "black book of computer viruses",
    "computer viruses",
    "virus programming",
    "writing malware",
    "rootkit",
    "bootkit",
    "botnet",
    "keylogger",
    "creating security policies",  # false-positive guard handled by ordering below
    "malware",
    "trojan",
    "shellcode",
    "buffer overflow",
    "stack smashing",
    "bypassing-av",
    "bypassing av",
    "bypass antivirus",
    "defacing",
    "obfuscated malicious",
    "injected, dynamically generated",
    "stoned bootkit",
)

_DUAL_USE_MARKERS: tuple[str, ...] = (
    "hacking",
    "penetration test",
    "penetration testing",
    "pentest",
    "metasploit",
    "kali linux",
    "exploit",
    "reverse engineering",
    "reversing",
    "gray hat",
    "social engineering",
    "password crack",
    "cracking password",
    "sql injection",
    "footprinting",
    "phishing",
    "cache poisoning",
    "unauthorised access",
    "unauthorized access",
    "underground",
    "backtrack",
    "wireshark",
    "nessus",
    "snort",
    "ninja hacking",
    "violent python",
    "shellcoder",
)

# Clearly non-technical material — kept on disk by the user but out of the
# stated knowledge scope (computers / ethical hacking / technology).
_OUT_OF_SCOPE_MARKERS: tuple[str, ...] = (
    "graham",
    "dodd",
    "value investing",
    "franchise value",
    "security analysis - 1934",
    "doesn't want you to know",
    "13 things the government",
)

# --- Topic markers ------------------------------------------------------------

_TOPIC_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("cryptography", ("cryptograph", "encryption", "cipher", "the code book", "ssl", "tls")),
    (
        "web",
        ("php", "html", "web application", "web development", "website", "apache", "javascript"),
    ),
    ("mobile", ("android", "ios", "mobile")),
    ("database", ("sql", "mysql", "oracle", "database", "db2")),
    ("networking", ("network", "ccna", "tcp", "dns", "firewall", "wireless", "vpn", "router")),
    ("systems", ("linux", "windows", "kernel", "assembly", "operating system", "unix")),
    (
        "security",
        (
            "security",
            "cissp",
            "comptia",
            "penetration",
            "hacking",
            "forensic",
            "malware",
            "exploit",
        ),
    ),
    (
        "programming",
        ("python", "c++", "java", "perl", "programming", "algorithm", "software", "game"),
    ),
)


def _haystack(title: str, sample: str) -> str:
    return f"{title}\n{sample}".lower()


def classify_sensitivity(title: str, sample: str) -> str:
    """Return ``"offensive"``, ``"dual_use"``, or ``"educational"``."""
    text = _haystack(title, sample)
    # "creating security policies" is defensive despite matching an offensive
    # substring list; guard it explicitly.
    if "creating security policies" in text or "security convergence" in text:
        return "educational"
    for marker in _OFFENSIVE_MARKERS:
        if marker in text:
            return "offensive"
    for marker in _DUAL_USE_MARKERS:
        if marker in text:
            return "dual_use"
    return "educational"


def classify_topic(title: str, sample: str) -> str:
    """Return a coarse topic label for the document."""
    text = _haystack(title, sample)
    for topic, markers in _TOPIC_MARKERS:
        if any(marker in text for marker in markers):
            return topic
    return "general"


def is_in_scope(title: str, sample: str) -> bool:
    """True if the document is within the computers/ethical-hacking/tech scope."""
    text = _haystack(title, sample)
    return not any(marker in text for marker in _OUT_OF_SCOPE_MARKERS)
