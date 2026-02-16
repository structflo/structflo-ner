"""Core matching engine: exact dictionary scan, regex patterns, and fuzzy matching."""

from __future__ import annotations

import re
from dataclasses import dataclass

from rapidfuzz import fuzz

from structflo.ner.fast._normalize import expand_variants, normalize


@dataclass(frozen=True)
class Match:
    """A single entity match found in text."""

    text: str
    entity_type: str
    char_start: int
    char_end: int
    canonical: str
    match_method: str  # "exact", "regex", or "fuzzy"


# Characters that mark word boundaries in biomedical text
_BOUNDARY_RE = re.compile(r"[\s\(\)\[\]\{\},;:\"\'\.!?/\-]")
_TOKEN_RE = re.compile(r"[A-Za-z0-9][\w\-\.]*[A-Za-z0-9]|[A-Za-z0-9]")


class GazetteerMatcher:
    """Multi-phase matching engine for gazetteer-based NER.

    Phase 1: Exact dictionary matching via sliding window over normalized text.
    Phase 1b: Regex pattern matching for structured IDs (accession numbers).
    Phase 2: Fuzzy matching for remaining unmatched candidate tokens.
    """

    def __init__(
        self,
        gazetteers: dict[str, list[str]],
        accession_patterns: list[tuple[re.Pattern[str], str]] | None = None,
        fuzzy_threshold: int = 85,
    ) -> None:
        self._fuzzy_threshold = fuzzy_threshold
        self._accession_patterns = accession_patterns or []

        # Build lookup structures
        # _norm_to_canonical: normalized_variant → (canonical_term, entity_type)
        self._norm_to_canonical: dict[str, tuple[str, str]] = {}
        # _case_sensitive: original_term → (canonical_term, entity_type)
        self._case_sensitive: dict[str, tuple[str, str]] = {}
        # _max_term_len: length of longest normalized term (for sliding window)
        self._max_term_len = 0
        # _fuzzy_terms: list of (canonical_term, entity_type) for fuzzy matching
        self._fuzzy_terms: list[tuple[str, str]] = []

        for entity_type, terms in gazetteers.items():
            for term in terms:
                # Case-sensitive exact entry
                self._case_sensitive[term] = (term, entity_type)

                # Normalized variants for case-insensitive matching
                for variant in expand_variants(term):
                    norm = normalize(variant)
                    if norm and norm not in self._norm_to_canonical:
                        self._norm_to_canonical[norm] = (term, entity_type)
                    self._max_term_len = max(self._max_term_len, len(norm))

                # Fuzzy candidates
                self._fuzzy_terms.append((term, entity_type))

    def match(self, text: str) -> list[Match]:
        """Find all entity matches in the given text."""
        matches: list[Match] = []
        occupied: set[int] = set()  # character positions already claimed

        # Phase 1: Exact matching (case-sensitive first, then normalized)
        matches.extend(self._exact_match(text, occupied))

        # Phase 1b: Regex patterns for accession numbers
        matches.extend(self._regex_match(text, occupied))

        # Phase 2: Fuzzy matching on remaining tokens
        if self._fuzzy_threshold > 0:
            matches.extend(self._fuzzy_match(text, occupied))

        # Sort by position
        matches.sort(key=lambda m: (m.char_start, -m.char_end))
        return matches

    def _exact_match(self, text: str, occupied: set[int]) -> list[Match]:
        """Phase 1: Sliding window exact match against normalized dictionary."""
        matches: list[Match] = []
        text_norm = normalize(text)

        # Build a mapping from normalized positions back to original positions.
        # Since normalize() lowercases and collapses whitespace, we need to
        # track the correspondence. For simplicity and correctness, we do
        # case-sensitive matching first on original text, then normalized.

        # Pass 1: Case-sensitive exact matching on original text
        for term, (canonical, entity_type) in self._case_sensitive.items():
            start = 0
            while True:
                idx = text.find(term, start)
                if idx == -1:
                    break
                end = idx + len(term)
                if self._is_word_boundary(text, idx, end) and not self._overlaps(
                    occupied, idx, end
                ):
                    matches.append(
                        Match(
                            text=text[idx:end],
                            entity_type=entity_type,
                            char_start=idx,
                            char_end=end,
                            canonical=canonical,
                            match_method="exact",
                        )
                    )
                    occupied.update(range(idx, end))
                start = idx + 1

        # Pass 2: Normalized sliding window for case-insensitive matching
        # Build position map from normalized text back to original
        norm_to_orig = _build_position_map(text, text_norm)

        for window_len in range(self._max_term_len, 0, -1):
            for i in range(len(text_norm) - window_len + 1):
                fragment = text_norm[i : i + window_len]
                if fragment not in self._norm_to_canonical:
                    continue

                # Map back to original positions
                orig_start = norm_to_orig[i]
                orig_end = norm_to_orig[min(i + window_len, len(text_norm)) - 1] + 1

                if self._overlaps(occupied, orig_start, orig_end):
                    continue
                if not self._is_word_boundary(text, orig_start, orig_end):
                    continue

                canonical, entity_type = self._norm_to_canonical[fragment]
                matches.append(
                    Match(
                        text=text[orig_start:orig_end],
                        entity_type=entity_type,
                        char_start=orig_start,
                        char_end=orig_end,
                        canonical=canonical,
                        match_method="exact",
                    )
                )
                occupied.update(range(orig_start, orig_end))

        return matches

    def _regex_match(self, text: str, occupied: set[int]) -> list[Match]:
        """Phase 1b: Regex pattern matching for structured accession IDs."""
        matches: list[Match] = []

        for pattern, _description in self._accession_patterns:
            for m in pattern.finditer(text):
                start, end = m.start(), m.end()
                if not self._overlaps(occupied, start, end):
                    matches.append(
                        Match(
                            text=m.group(),
                            entity_type="accession_number",
                            char_start=start,
                            char_end=end,
                            canonical=m.group(),
                            match_method="regex",
                        )
                    )
                    occupied.update(range(start, end))

        return matches

    def _fuzzy_match(self, text: str, occupied: set[int]) -> list[Match]:
        """Phase 2: Fuzzy matching on unmatched tokens."""
        matches: list[Match] = []

        for token_match in _TOKEN_RE.finditer(text):
            start, end = token_match.start(), token_match.end()

            # Skip if overlapping with already-matched spans
            if self._overlaps(occupied, start, end):
                continue

            token = token_match.group()

            # Only try fuzzy on "entity-like" tokens
            if not self._is_entity_like(token):
                continue

            best_score = 0
            best_canonical = ""
            best_entity_type = ""

            for canonical, entity_type in self._fuzzy_terms:
                # Length filter: skip terms with very different lengths
                len_ratio = len(token) / max(len(canonical), 1)
                if len_ratio < 0.7 or len_ratio > 1.4:
                    continue

                score = fuzz.ratio(token.lower(), canonical.lower())
                if score > best_score:
                    best_score = score
                    best_canonical = canonical
                    best_entity_type = entity_type

            if best_score >= self._fuzzy_threshold:
                matches.append(
                    Match(
                        text=token,
                        entity_type=best_entity_type,
                        char_start=start,
                        char_end=end,
                        canonical=best_canonical,
                        match_method="fuzzy",
                    )
                )
                occupied.update(range(start, end))

        return matches

    @staticmethod
    def _is_word_boundary(text: str, start: int, end: int) -> bool:
        """Check that the match is at word boundaries (not a substring of a larger word)."""
        if start > 0 and text[start - 1].isalnum():
            return False
        return not (end < len(text) and text[end].isalnum())

    @staticmethod
    def _overlaps(occupied: set[int], start: int, end: int) -> bool:
        """Check if a span overlaps with already-occupied positions."""
        return any(i in occupied for i in range(start, end))

    @staticmethod
    def _is_entity_like(token: str) -> bool:
        """Heuristic: is this token likely to be a named entity?"""
        if len(token) < 3:
            return False
        # Contains uppercase letter (not just first char of sentence)
        has_upper = any(c.isupper() for c in token)
        # Contains digits
        has_digit = any(c.isdigit() for c in token)
        # Long enough to be meaningful
        is_long = len(token) >= 4
        return has_upper or has_digit or is_long


def _build_position_map(original: str, normalized: str) -> list[int]:
    """Build a mapping from normalized text positions back to original positions.

    Returns a list where position_map[norm_idx] = orig_idx.
    """
    position_map: list[int] = []
    orig_idx = 0

    for _norm_idx in range(len(normalized)):
        norm_char = normalized[_norm_idx]

        # Advance original pointer to find the matching character
        while orig_idx < len(original):
            orig_lower = original[orig_idx].lower()
            if orig_lower == norm_char:
                position_map.append(orig_idx)
                orig_idx += 1
                break
            # Skip characters that were removed during normalization
            # (extra whitespace, dashes that were unified, etc.)
            orig_idx += 1
        else:
            # Fallback: use last known position
            position_map.append(max(0, orig_idx - 1))

    return position_map
