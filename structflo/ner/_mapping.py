"""Maps langextract Extraction objects to typed NEREntity instances."""

from __future__ import annotations

import langextract as lx

from structflo.ner._entities import (
    NEREntity,
    NERResult,
    entity_class_for,
    field_name_for,
)


def extraction_to_entity(extraction: lx.data.Extraction) -> NEREntity:
    """Convert a single lx.data.Extraction into the appropriate typed NEREntity."""
    entity_cls = entity_class_for(extraction.extraction_class)

    char_start = None
    char_end = None
    if extraction.char_interval is not None:
        char_start = extraction.char_interval.start_pos
        char_end = extraction.char_interval.end_pos

    alignment = None
    if extraction.alignment_status is not None:
        alignment = extraction.alignment_status.value

    attributes: dict[str, str] = {}
    if extraction.attributes:
        for key, value in extraction.attributes.items():
            if isinstance(value, list):
                attributes[key] = ", ".join(value)
            else:
                attributes[key] = str(value)

    return entity_cls(
        text=extraction.extraction_text,
        entity_type=extraction.extraction_class,
        char_start=char_start,
        char_end=char_end,
        attributes=attributes,
        alignment=alignment,
    )


def annotated_doc_to_result(
    doc: lx.data.AnnotatedDocument,
    source_text: str,
) -> NERResult:
    """Convert an AnnotatedDocument into a NERResult with typed entity lists."""
    # Group entities by their field name on NERResult
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

    for extraction in doc.extractions:
        entity = extraction_to_entity(extraction)
        field = field_name_for(type(entity))
        buckets[field].append(entity)

    return NERResult(
        source_text=source_text,
        **buckets,  # type: ignore[arg-type]
    )
