"""Load YAML gazetteer files and auto-derive regex patterns for accession numbers."""

from __future__ import annotations

import logging
import re
from pathlib import Path

import yaml

from structflo.ner._entities import _ENTITY_CLASS_MAP

logger = logging.getLogger(__name__)

# Default gazetteer directory (shipped with the package)
_DEFAULT_GAZETTEER_DIR = Path(__file__).parent / "gazetteers"

# Known accession-number patterns: (regex_to_detect_seed, full_pattern_with_word_boundaries)
_ACCESSION_PATTERNS: list[tuple[re.Pattern[str], re.Pattern[str], str]] = [
    # Rv locus tags: Rv0005, Rv3854c
    (re.compile(r"^Rv\d{4}[c]?$"), re.compile(r"\bRv\d{4}[c]?\b"), "Rv locus tag"),
    # Mycobrowser MT IDs: MT0005, MTCI00.01
    (re.compile(r"^MT\w+$"), re.compile(r"\bMT\w+\b"), "Mycobrowser ID"),
    # UniProt accessions: P9WGR1, O53617
    (
        re.compile(r"^[OPQ][0-9][A-Z0-9]{3}[0-9]$"),
        re.compile(r"\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b"),
        "UniProt accession",
    ),
    # PDB codes: 4TZK, 1P44
    (re.compile(r"^[0-9][A-Z0-9]{3}$"), re.compile(r"\b[0-9][A-Z0-9]{3}\b"), "PDB code"),
    # NCBI RefSeq protein: WP_003407354
    (re.compile(r"^WP_\d+$"), re.compile(r"\bWP_\d+\b"), "NCBI RefSeq"),
]


def load_gazetteer(path: Path) -> tuple[str, list[str]]:
    """Load a single YAML gazetteer file.

    Returns:
        Tuple of (entity_type, list_of_terms) where entity_type is derived
        from the filename stem.
    """
    entity_type = path.stem
    with open(path) as f:
        terms = yaml.safe_load(f)

    if not isinstance(terms, list):
        msg = f"Gazetteer {path.name} must be a YAML list, got {type(terms).__name__}"
        raise ValueError(msg)

    # Coerce all entries to strings
    terms = [str(t).strip() for t in terms if t is not None and str(t).strip()]
    return entity_type, terms


def load_all_gazetteers(
    directory: Path | str | None = None,
) -> dict[str, list[str]]:
    """Load all YAML gazetteer files from a directory.

    Args:
        directory: Path to gazetteer directory. Defaults to the built-in
            gazetteers shipped with the package.

    Returns:
        Dict mapping entity_type → list of canonical terms.
    """
    dirpath = Path(directory) if directory is not None else _DEFAULT_GAZETTEER_DIR

    if not dirpath.is_dir():
        msg = f"Gazetteer directory does not exist: {dirpath}"
        raise FileNotFoundError(msg)

    gazetteers: dict[str, list[str]] = {}

    for yml_path in sorted(dirpath.glob("*.yml")):
        entity_type, terms = load_gazetteer(yml_path)

        if entity_type not in _ENTITY_CLASS_MAP:
            logger.warning(
                "Gazetteer %s maps to unknown entity_type %r — entities will be unclassified",
                yml_path.name,
                entity_type,
            )

        gazetteers[entity_type] = terms
        logger.debug("Loaded %d terms for %s from %s", len(terms), entity_type, yml_path.name)

    return gazetteers


def derive_accession_patterns(terms: list[str]) -> list[tuple[re.Pattern[str], str]]:
    """Auto-derive regex patterns from accession number seed entries.

    Examines each term against known ID formats and returns compiled regex
    patterns that will match the entire family (not just the listed seeds).

    Returns:
        List of (compiled_pattern, description) tuples.
    """
    detected: list[tuple[re.Pattern[str], str]] = []
    seen_descriptions: set[str] = set()

    for term in terms:
        for seed_re, full_re, description in _ACCESSION_PATTERNS:
            if description not in seen_descriptions and seed_re.match(term):
                detected.append((full_re, description))
                seen_descriptions.add(description)
                logger.debug(
                    "Auto-derived %s pattern from seed %r",
                    description,
                    term,
                )

    return detected
