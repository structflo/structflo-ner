"""structflo.ner — Drug discovery NER powered by LangExtract.

Quick start::

    from structflo.ner import NERExtractor

    extractor = NERExtractor(api_key="YOUR_GEMINI_KEY")
    result = extractor.extract(
        "Gefitinib inhibits EGFR with IC50 = 0.033 µM in NSCLC."
    )
    print(result.compounds)
    print(result.targets)
    print(result.bioactivities)
    df = result.to_dataframe()

Local models via Ollama::

    extractor = NERExtractor(
        model_id="gemma3:27b",
        model_url="http://localhost:11434",
    )

Custom profile::

    from structflo.ner import NERExtractor, EntityProfile

    my_profile = EntityProfile(
        name="kinase_inhibitors",
        entity_classes=["compound_name", "smiles", "target", "bioactivity"],
        prompt="Extract kinase inhibitor names, SMILES, targets, and IC50/Ki values.",
        examples=my_examples,
    )
    result = extractor.extract(text, profile=my_profile)
"""

from structflo.ner._entities import (
    AssayEntity,
    BioactivityEntity,
    ChemicalEntity,
    DiseaseEntity,
    MechanismEntity,
    NEREntity,
    NERResult,
    TargetEntity,
)
from structflo.ner.extractor import NERExtractor
from structflo.ner.profiles import (
    BIOACTIVITY,
    BIOLOGY,
    CHEMISTRY,
    DISEASE,
    FULL,
    EntityProfile,
)

__version__ = "0.1.0"

__all__ = [
    # Main class
    "NERExtractor",
    # Profile system
    "EntityProfile",
    "FULL",
    "CHEMISTRY",
    "BIOLOGY",
    "BIOACTIVITY",
    "DISEASE",
    # Result types
    "NERResult",
    "NEREntity",
    "ChemicalEntity",
    "TargetEntity",
    "DiseaseEntity",
    "BioactivityEntity",
    "AssayEntity",
    "MechanismEntity",
]
