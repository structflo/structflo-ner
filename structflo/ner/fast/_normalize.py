"""Text normalization and variant expansion for gazetteer matching."""

from __future__ import annotations

import re

# Greek letter mappings (symbol ↔ name)
_GREEK: list[tuple[str, str]] = [
    ("α", "alpha"),
    ("β", "beta"),
    ("γ", "gamma"),
    ("δ", "delta"),
    ("ε", "epsilon"),
    ("ζ", "zeta"),
    ("η", "eta"),
    ("θ", "theta"),
    ("κ", "kappa"),
    ("λ", "lambda"),
    ("μ", "mu"),
    ("ν", "nu"),
    ("ξ", "xi"),
    ("π", "pi"),
    ("ρ", "rho"),
    ("σ", "sigma"),
    ("τ", "tau"),
    ("φ", "phi"),
    ("χ", "chi"),
    ("ψ", "psi"),
    ("ω", "omega"),
]

_DASH_RE = re.compile(r"[\u2010\u2011\u2012\u2013\u2014\u2015\uFE58\uFE63\uFF0D]")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Normalize text for matching: lowercase, collapse whitespace, unify dashes."""
    text = text.lower()
    text = _DASH_RE.sub("-", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def expand_variants(term: str) -> set[str]:
    """Generate matching variants from a canonical term.

    Returns a set of normalized forms that should all resolve to this term.
    """
    variants: set[str] = set()

    # Original and lowercased
    variants.add(term)
    variants.add(term.lower())

    # Greek letter expansion (both directions)
    for symbol, name in _GREEK:
        if symbol in term.lower():
            variants.add(term.lower().replace(symbol, name))
        if name in term.lower():
            variants.add(term.lower().replace(name, symbol))

    # Hyphen-optional: "DprE-1" ↔ "DprE1"
    if "-" in term:
        variants.add(term.replace("-", ""))
        variants.add(term.lower().replace("-", ""))
    # Also generate hyphenated form for alphanumeric boundaries: "DprE1" → "DprE-1"
    dehyphen = re.sub(r"([a-zA-Z])(\d)", r"\1-\2", term)
    if dehyphen != term:
        variants.add(dehyphen)
        variants.add(dehyphen.lower())

    # Period-optional: "M. tuberculosis" ↔ "M tuberculosis"
    if ". " in term:
        variants.add(term.replace(". ", " "))
        variants.add(term.lower().replace(". ", " "))

    # Normalize all variants (collapse whitespace, unify dashes)
    normalized = set()
    for v in variants:
        normalized.add(normalize(v))
    # Also keep case-sensitive originals for exact matching
    normalized.update(variants)

    return normalized
