"""FastNERExtractor: dictionary-based NER for TB drug discovery — no LLM required."""

from __future__ import annotations

import logging
from pathlib import Path

from structflo.ner._entities import (
    NEREntity,
    NERResult,
    entity_class_for,
    field_name_for,
)
from structflo.ner.fast._loader import (
    _DEFAULT_GAZETTEER_DIR,
    derive_accession_patterns,
    load_all_gazetteers,
)
from structflo.ner.fast._matcher import GazetteerMatcher, Match

logger = logging.getLogger(__name__)


class FastNERExtractor:
    """Extract drug discovery entities using dictionary matching — no LLM.

    Uses curated YAML gazetteers with auto-derived matching rules for fast,
    deterministic entity extraction. Produces the same :class:`NERResult`
    objects as :class:`NERExtractor` so all downstream tooling (DataFrames,
    display, etc.) works identically.

    Example::

        from structflo.ner.fast import FastNERExtractor

        extractor = FastNERExtractor()
        result = extractor.extract(
            "Bedaquiline inhibits AtpE (Rv1305) in M. tuberculosis."
        )

        print(result.compounds)   # [ChemicalEntity(text='Bedaquiline', ...)]
        print(result.targets)     # [TargetEntity(text='AtpE', ...)]
        print(result.accessions)  # [AccessionEntity(text='Rv1305', ...)]
        df = result.to_dataframe()

    Args:
        gazetteer_dir: Path to directory containing YAML gazetteer files.
            Each ``.yml`` file is auto-discovered; the filename (without
            extension) becomes the ``entity_type``. Defaults to the built-in
            TB gazetteers shipped with the package.
        extra_gazetteers: Additional terms to merge programmatically, as a
            dict mapping ``entity_type`` to a list of terms. These are
            combined with terms loaded from YAML files.
        fuzzy_threshold: Minimum fuzzy match score (0–100) for Phase 2
            matching. Set to 0 to disable fuzzy matching entirely.
            Default is 85.
    """

    def __init__(
        self,
        gazetteer_dir: str | Path | None = None,
        extra_gazetteers: dict[str, list[str]] | None = None,
        fuzzy_threshold: int = 85,
    ) -> None:
        # Load gazetteers from YAML
        dir_path = Path(gazetteer_dir) if gazetteer_dir is not None else _DEFAULT_GAZETTEER_DIR
        gazetteers = load_all_gazetteers(dir_path)

        # Merge programmatic additions
        if extra_gazetteers:
            for entity_type, terms in extra_gazetteers.items():
                existing = gazetteers.get(entity_type, [])
                gazetteers[entity_type] = existing + terms

        # Auto-derive accession patterns from seed entries
        accession_patterns = []
        if "accession_number" in gazetteers:
            accession_patterns = derive_accession_patterns(gazetteers["accession_number"])

        # Build the matcher
        self._matcher = GazetteerMatcher(
            gazetteers=gazetteers,
            accession_patterns=accession_patterns,
            fuzzy_threshold=fuzzy_threshold,
        )

        total_terms = sum(len(t) for t in gazetteers.values())
        logger.info(
            "FastNERExtractor ready: %d gazetteers, %d terms, %d accession patterns",
            len(gazetteers),
            total_terms,
            len(accession_patterns),
        )

    def extract(
        self,
        text: str | list[str],
    ) -> NERResult | list[NERResult]:
        """Extract entities from text using dictionary matching.

        Args:
            text: Input text (or list of texts) to process.

        Returns:
            A :class:`NERResult` for a single string, or a list of
            :class:`NERResult` when a list of strings is provided.
        """
        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]

        results = [self._extract_single(t) for t in texts]
        return results if is_batch else results[0]

    def _extract_single(self, text: str) -> NERResult:
        """Extract entities from a single text."""
        matches = self._matcher.match(text)
        return _matches_to_result(matches, text)


def _match_to_entity(m: Match) -> NEREntity:
    """Convert a Match to the appropriate typed NEREntity."""
    entity_cls = entity_class_for(m.entity_type)
    attributes: dict[str, str] = {}
    if m.canonical != m.text:
        attributes["canonical"] = m.canonical
    attributes["match_method"] = m.match_method
    return entity_cls(
        text=m.text,
        entity_type=m.entity_type,
        char_start=m.char_start,
        char_end=m.char_end,
        attributes=attributes,
    )


def _matches_to_result(matches: list[Match], source_text: str) -> NERResult:
    """Convert a list of Matches into a NERResult with typed entity lists."""
    buckets: dict[str, list[NEREntity]] = {
        "compounds": [],
        "targets": [],
        "diseases": [],
        "bioactivities": [],
        "assays": [],
        "mechanisms": [],
        "accessions": [],
        "products": [],
        "functional_categories": [],
        "screening_methods": [],
        "unclassified": [],
    }

    for m in matches:
        entity = _match_to_entity(m)
        field = field_name_for(type(entity))
        buckets[field].append(entity)

    return NERResult(
        source_text=source_text,
        **buckets,  # type: ignore[arg-type]
    )
