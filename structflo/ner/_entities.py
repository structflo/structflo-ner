"""Typed entity dataclasses for drug discovery NER results."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


@dataclasses.dataclass(frozen=True)
class NEREntity:
    """Base class for all extracted drug discovery entities."""

    text: str
    entity_type: str
    char_start: int | None = None
    char_end: int | None = None
    attributes: dict[str, str] = dataclasses.field(default_factory=dict)
    alignment: str | None = None


@dataclasses.dataclass(frozen=True)
class ChemicalEntity(NEREntity):
    """A chemical entity: compound name, SMILES, CAS number, or molecular formula."""


@dataclasses.dataclass(frozen=True)
class TargetEntity(NEREntity):
    """A biological target: protein, gene, or receptor."""


@dataclasses.dataclass(frozen=True)
class DiseaseEntity(NEREntity):
    """A disease or clinical indication."""


@dataclasses.dataclass(frozen=True)
class BioactivityEntity(NEREntity):
    """A bioactivity measurement: IC50, EC50, Ki, Kd, etc."""


@dataclasses.dataclass(frozen=True)
class AssayEntity(NEREntity):
    """An assay description or experimental system."""


@dataclasses.dataclass(frozen=True)
class MechanismEntity(NEREntity):
    """A mechanism of action or binding mode description."""


@dataclasses.dataclass(frozen=True)
class AccessionEntity(NEREntity):
    """A database accession: Rv locus tag, UniProt ID, or PDB code."""


@dataclasses.dataclass(frozen=True)
class ProductEntity(NEREntity):
    """A gene product description (e.g., enzyme name, protein function)."""


@dataclasses.dataclass(frozen=True)
class FunctionalCategoryEntity(NEREntity):
    """A protein functional category (e.g., cell wall, lipid metabolism)."""


@dataclasses.dataclass(frozen=True)
class ScreeningMethodEntity(NEREntity):
    """A screening approach: fragment, biochemical, DEL, hypomorph, etc."""


# Maps extraction_class → typed entity class
_ENTITY_CLASS_MAP: dict[str, type[NEREntity]] = {
    "compound_name": ChemicalEntity,
    "smiles": ChemicalEntity,
    "cas_number": ChemicalEntity,
    "molecular_formula": ChemicalEntity,
    "target": TargetEntity,
    "gene_name": TargetEntity,
    "protein_name": TargetEntity,
    "disease": DiseaseEntity,
    "bioactivity": BioactivityEntity,
    "assay": AssayEntity,
    "mechanism_of_action": MechanismEntity,
    "accession_number": AccessionEntity,
    "product": ProductEntity,
    "functional_category": FunctionalCategoryEntity,
    "screening_method": ScreeningMethodEntity,
}

# Maps typed entity class → NERResult field name
_ENTITY_FIELD_MAP: dict[type[NEREntity], str] = {
    ChemicalEntity: "compounds",
    TargetEntity: "targets",
    DiseaseEntity: "diseases",
    BioactivityEntity: "bioactivities",
    AssayEntity: "assays",
    MechanismEntity: "mechanisms",
    AccessionEntity: "accessions",
    ProductEntity: "products",
    FunctionalCategoryEntity: "functional_categories",
    ScreeningMethodEntity: "screening_methods",
}


def entity_class_for(extraction_class: str) -> type[NEREntity]:
    """Return the typed entity class for a given extraction_class string."""
    return _ENTITY_CLASS_MAP.get(extraction_class, NEREntity)


def field_name_for(entity_cls: type[NEREntity]) -> str:
    """Return the NERResult field name for a given entity class."""
    return _ENTITY_FIELD_MAP.get(entity_cls, "unclassified")


@dataclasses.dataclass
class NERResult:
    """The result of a drug discovery NER extraction."""

    source_text: str
    compounds: list[ChemicalEntity] = dataclasses.field(default_factory=list)
    targets: list[TargetEntity] = dataclasses.field(default_factory=list)
    diseases: list[DiseaseEntity] = dataclasses.field(default_factory=list)
    bioactivities: list[BioactivityEntity] = dataclasses.field(default_factory=list)
    assays: list[AssayEntity] = dataclasses.field(default_factory=list)
    mechanisms: list[MechanismEntity] = dataclasses.field(default_factory=list)
    accessions: list[AccessionEntity] = dataclasses.field(default_factory=list)
    products: list[ProductEntity] = dataclasses.field(default_factory=list)
    functional_categories: list[FunctionalCategoryEntity] = dataclasses.field(default_factory=list)
    screening_methods: list[ScreeningMethodEntity] = dataclasses.field(default_factory=list)
    unclassified: list[NEREntity] = dataclasses.field(default_factory=list)

    def all_entities(self) -> list[NEREntity]:
        """Return all extracted entities as a flat list."""
        return (
            list(self.compounds)
            + list(self.targets)
            + list(self.diseases)
            + list(self.bioactivities)
            + list(self.assays)
            + list(self.mechanisms)
            + list(self.accessions)
            + list(self.products)
            + list(self.functional_categories)
            + list(self.screening_methods)
            + list(self.unclassified)
        )

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "source_text": self.source_text,
            "compounds": [dataclasses.asdict(e) for e in self.compounds],
            "targets": [dataclasses.asdict(e) for e in self.targets],
            "diseases": [dataclasses.asdict(e) for e in self.diseases],
            "bioactivities": [dataclasses.asdict(e) for e in self.bioactivities],
            "assays": [dataclasses.asdict(e) for e in self.assays],
            "mechanisms": [dataclasses.asdict(e) for e in self.mechanisms],
            "accessions": [dataclasses.asdict(e) for e in self.accessions],
            "products": [dataclasses.asdict(e) for e in self.products],
            "functional_categories": [dataclasses.asdict(e) for e in self.functional_categories],
            "screening_methods": [dataclasses.asdict(e) for e in self.screening_methods],
            "unclassified": [dataclasses.asdict(e) for e in self.unclassified],
        }

    def display(self) -> None:
        """Render the result as interactive HTML in a Jupyter notebook."""
        from structflo.ner._display import display as _display  # noqa: PLC0415

        _display(self)

    def _repr_html_(self) -> str:
        """Auto-render as HTML when displayed in Jupyter."""
        from structflo.ner._display import render_html  # noqa: PLC0415

        return render_html(self)

    def to_dataframe(self) -> pd.DataFrame:
        """Return all entities as a flat pandas DataFrame.

        Requires pandas to be installed: pip install structflo-ner[dataframe]
        """
        try:
            import pandas as pd  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "pandas is required for to_dataframe(). "
                "Install it with: pip install structflo-ner[dataframe]"
            ) from exc

        rows = []
        for entity in self.all_entities():
            row = {
                "text": entity.text,
                "entity_type": entity.entity_type,
                "entity_class": type(entity).__name__,
                "char_start": entity.char_start,
                "char_end": entity.char_end,
                "alignment": entity.alignment,
            }
            row.update(entity.attributes)
            rows.append(row)
        return pd.DataFrame(rows)
