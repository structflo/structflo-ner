"""Load YAML gazetteer files and derive regex patterns for structured identifiers."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

import yaml

from structflo.ner._entities import _ENTITY_CLASS_MAP

logger = logging.getLogger(__name__)

# Default gazetteer directory (shipped with the package)
_DEFAULT_GAZETTEER_DIR = Path(__file__).parent / "gazetteers"


class IdPattern(NamedTuple):
    """A compiled identifier pattern and the entity class it resolves to."""

    regex: re.Pattern[str]
    description: str
    entity_type: str
    validate: Callable[[str], bool] | None = None


def _valid_cas(text: str) -> bool:
    """CAS registry numbers carry a trailing check digit; dates and ranges do not."""
    digits = [int(c) for c in text if c.isdigit()]
    return digits[-1] == sum(v * i for i, v in enumerate(reversed(digits[:-1]), start=1)) % 10


# Curated compound identifier patterns, always active. Unlike the accession
# patterns below these need no seed entry: a ChEMBL id is a ChEMBL id whatever
# the deployment's gazetteers happen to contain.
_COMPOUND_ID_PATTERNS: list[IdPattern] = [
    IdPattern(re.compile(pattern), description, "compound_name")
    for pattern, description in [
        # ── Public chemistry databases ──
        (r"\bCHEMBL\d+\b", "ChEMBL ID"),
        (r"\bSCHEMBL\d+\b", "SureChEMBL ID"),
        (r"\bCHEBI:\d+\b", "ChEBI ID"),
        (r"\bDB\d{5}\b", "DrugBank ID"),
        (r"\bZINC\d{6,}\b", "ZINC ID"),
        (r"\bHMDB\d{5,7}\b", "HMDB ID"),
        (r"\bDTX[SC]ID\d+\b", "EPA CompTox ID"),
        (r"\bNSC[-\s]?\d{3,6}\b", "NCI NSC number"),
        (r"\bNCGC\d{5,}(?:-\d+)?\b", "NCATS NCGC ID"),
        (r"\b[A-Z]{14}-[A-Z]{10}-[A-Z]\b", "InChIKey"),
        # ── Vendor / screening catalogues ──
        (r"\bEN300-\d+\b", "Enamine EN300"),
        (r"\bZ\d{8,10}\b", "Enamine Z-number"),
        (r"\bMolPort-\d{3}-\d{3}-\d{3}\b", "MolPort ID"),
        (r"\bMCULE-\d{10}\b", "Mcule ID"),
        (r"\bSTK\d{6}\b", "Vitas-M STK"),
        # ── TB / neglected-disease programme codes ──
        (r"\bSACC-?\d{3,}\b", "SACC series"),
        (r"\bTBDA-?\d{3,}\b", "TBDA series"),
        (r"\bLGENI-?\d{3,}\b", "LGENI series"),
        (r"\bTBA-?\d{3,}\b", "TB Alliance TBA"),
        (r"\bTBI-?\d{3,}\b", "TB Alliance TBI"),
        (r"\bMMV-?\d{6}\b", "MMV Open Box"),
        (r"\bDNDI-?\d{3,}\b", "DNDi series"),
        (r"\bGSK-?\d{3,}\b", "GSK series"),
        (r"\bAZD-?\d{3,}\b", "AstraZeneca AZD"),
        (r"\bNITD-?\d{3,}\b", "Novartis NITD"),
        (r"\bOPC-?\d{4,}\b", "Otsuka OPC"),
        (r"\bTMC-?\d{3,}\b", "Tibotec TMC"),
        (r"\bP?BTZ-?\d{3,}\b", "benzothiazinone"),
        (r"\bSQ-?\d{3,}\b", "Sequella SQ"),
        (r"\bSPR-?\d{3,}\b", "Spero SPR"),
        (r"\bBRD-?\d{3,}\b", "Broad BRD"),
        (r"\bAN\d{4,}\b", "Anacor AN"),
        (r"\bJSF-\d{3,}\b", "JSF series"),
        (r"\bPA-\d{3,}\b", "PA series"),
    ]
] + [
    # CAS numbers route to the existing cas_number class, and carry a check
    # digit: without validating it the pattern also matches dates (2020-11-5)
    # and dose ranges (100-50-3).
    IdPattern(re.compile(r"\b\d{2,7}-\d{2}-\d\b"), "CAS number", "cas_number", _valid_cas),
]

# Accession-number patterns, activated by a seed entry in accession_number.yml:
# (regex_to_detect_seed, full_pattern_with_word_boundaries, description)
_ACCESSION_PATTERNS: list[tuple[re.Pattern[str], re.Pattern[str], str]] = [
    # Rv locus tags: Rv0005, Rv3854c
    (re.compile(r"^Rv\d{4}[c]?$"), re.compile(r"\bRv\d{4}[c]?\b"), "Rv locus tag"),
    # Mycobrowser MT IDs: MT0005, MT18B_0001, MTB000001. The digit run keeps
    # MTT (viability assay), MTX and MTD from matching.
    (
        re.compile(r"^MT[A-Z]{0,2}\d{2,}\w*$"),
        re.compile(r"\bMT[A-Z]{0,2}\d{2,}\w*\b"),
        "Mycobrowser ID",
    ),
    # UniProt accessions: P9WGR1, O53617
    (
        re.compile(r"^[OPQ][0-9][A-Z0-9]{3}[0-9]$"),
        re.compile(r"\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b"),
        "UniProt accession",
    ),
    # PDB codes: 4TZK, 1P44. The leading lookahead requires at least one letter;
    # without it the pattern matches every four-digit number in the corpus.
    # ponytail: excludes hypothetical all-numeric PDB IDs, drop the lookahead
    # if one ever shows up in a real corpus.
    (
        re.compile(r"^(?=[A-Z0-9]{0,3}[A-Z])[1-9][A-Z0-9]{3}$"),
        re.compile(r"\b(?=[A-Z0-9]{0,3}[A-Z])[1-9][A-Z0-9]{3}\b"),
        "PDB code",
    ),
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


def derive_id_patterns(gazetteers: dict[str, list[str]]) -> list[IdPattern]:
    """Return the identifier patterns active for these gazetteers.

    Compound patterns are curated and always on. Accession patterns activate
    only when a matching seed appears in ``accession_number``, so a deployment's
    own gazetteer decides which ID families its corpus uses.

    Compound patterns come first because the matcher claims spans in list
    order: the PDB rule would otherwise take the ``3060`` out of ``SACC-3060``,
    and the Mycobrowser rule would take ``MT4501`` whole.
    """
    patterns = list(_COMPOUND_ID_PATTERNS)
    seen_descriptions: set[str] = set()

    for term in gazetteers.get("accession_number", []):
        for seed_re, full_re, description in _ACCESSION_PATTERNS:
            if description not in seen_descriptions and seed_re.match(term):
                patterns.append(IdPattern(full_re, description, "accession_number"))
                seen_descriptions.add(description)
                logger.debug("Auto-derived %s pattern from seed %r", description, term)

    return patterns
