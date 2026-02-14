"""EntityProfile: defines what entity types to extract, with what prompt and examples.

Users can use the built-in profiles or create their own:

    from structflo.ner import EntityProfile, CHEMISTRY

    # Use a built-in profile
    extractor.extract(text, profile=CHEMISTRY)

    # Create a custom profile
    my_profile = EntityProfile(
        name="kinase_inhibitors",
        entity_classes=["compound_name", "smiles", "target", "bioactivity"],
        prompt="Extract kinase inhibitor names, their SMILES, kinase targets, and IC50 values.",
        examples=my_examples,
    )
    extractor.extract(text, profile=my_profile)
"""

from __future__ import annotations

import dataclasses

import langextract as lx

from structflo.ner import _examples, _prompts


@dataclasses.dataclass
class EntityProfile:
    """Configuration for what and how to extract.

    Attributes:
        name: Human-readable name for this profile.
        entity_classes: The extraction_class values this profile targets.
            These drive schema constraints so the LLM stays on-topic.
        prompt: Instruction string passed to the LLM.
        examples: Few-shot ExampleData objects to guide the LLM.
    """

    name: str
    entity_classes: list[str]
    prompt: str
    examples: list[lx.data.ExampleData]

    def merge(self, other: EntityProfile) -> EntityProfile:
        """Return a new profile combining this profile with another."""
        return EntityProfile(
            name=f"{self.name}+{other.name}",
            entity_classes=list(dict.fromkeys(self.entity_classes + other.entity_classes)),
            prompt=self.prompt + "\n\n" + other.prompt,
            examples=self.examples + other.examples,
        )


# ---------------------------------------------------------------------------
# Built-in profiles
# ---------------------------------------------------------------------------

CHEMISTRY: EntityProfile = EntityProfile(
    name="chemistry",
    entity_classes=["compound_name", "smiles", "cas_number", "molecular_formula"],
    prompt=_prompts.CHEMISTRY_PROMPT,
    examples=_examples.CHEMISTRY_EXAMPLES,
)

BIOLOGY: EntityProfile = EntityProfile(
    name="biology",
    entity_classes=["target", "gene_name", "protein_name"],
    prompt=_prompts.BIOLOGY_PROMPT,
    examples=_examples.BIOLOGY_EXAMPLES,
)

BIOACTIVITY: EntityProfile = EntityProfile(
    name="bioactivity",
    entity_classes=["bioactivity", "assay"],
    prompt=_prompts.BIOACTIVITY_PROMPT,
    examples=_examples.BIOACTIVITY_EXAMPLES,
)

DISEASE: EntityProfile = EntityProfile(
    name="disease",
    entity_classes=["disease"],
    prompt=_prompts.DISEASE_PROMPT,
    examples=_examples.DISEASE_EXAMPLES,
)

FULL: EntityProfile = EntityProfile(
    name="full",
    entity_classes=[
        "compound_name",
        "smiles",
        "cas_number",
        "molecular_formula",
        "target",
        "gene_name",
        "protein_name",
        "disease",
        "bioactivity",
        "assay",
        "mechanism_of_action",
    ],
    prompt=_prompts.FULL_PROMPT,
    examples=_examples.FULL_EXAMPLES,
)
