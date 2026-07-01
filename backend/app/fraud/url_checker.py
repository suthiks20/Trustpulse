"""Site risk checks: SSL certificate validity + lookalike-domain scoring.

No external APIs are used — SSL is checked directly via Python's ssl/socket
modules, and lookalike scoring is a local Levenshtein-distance comparison
against a small hardcoded brand list.
"""

import socket
import ssl
from urllib.parse import urlparse

import Levenshtein

KNOWN_BRANDS = [
    "sbi",
    "hdfcbank",
    "icicibank",
    "axisbank",
    "kotak",
    "paypal",
    "amazon",
    "google",
    "microsoft",
]


def extract_domain(url: str) -> str:
    if "://" not in url:
        url = "https://" + url
    parsed = urlparse(url)
    return parsed.hostname or ""


def check_ssl_valid(domain: str, timeout: float = 5.0) -> bool:
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                ssock.getpeercert()
        return True
    except Exception:
        return False


def lookalike_score(domain: str) -> float:
    """0-100 score: how close the domain is to a known brand without being identical.

    A domain that IS a known brand's real domain (e.g. "sbi.co.in") scores 0 risk here
    (it's the real thing). A domain that's suspiciously close but not exact
    (e.g. "hdfc-bank-secure-login.com") scores high.
    """
    core = domain.split(".")[0].lower() if domain else ""
    if not core:
        return 0.0

    normalized_core = "".join(ch for ch in core if ch.isalnum())

    best_score = 0.0
    for brand in KNOWN_BRANDS:
        if core == brand:
            continue  # exact match to the real brand name is not a lookalike
        distance = Levenshtein.distance(core, brand)
        max_len = max(len(core), len(brand))
        similarity = 1.0 - (distance / max_len)
        if brand in normalized_core and core != brand:
            similarity = max(similarity, 0.85)
        best_score = max(best_score, similarity)

    return round(best_score * 100, 2)


def compute_risk_score(ssl_valid: bool, lookalike: float) -> float:
    ssl_penalty = 0.0 if ssl_valid else 50.0
    risk = min(100.0, lookalike * 0.6 + ssl_penalty)
    return round(risk, 2)


def check_url(url: str) -> dict:
    domain = extract_domain(url)
    ssl_valid = check_ssl_valid(domain)
    lookalike = lookalike_score(domain)
    risk_score = compute_risk_score(ssl_valid, lookalike)
    return {
        "domain": domain,
        "ssl_valid": ssl_valid,
        "lookalike_score": lookalike,
        "risk_score": risk_score,
    }
