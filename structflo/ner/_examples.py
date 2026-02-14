"""Curated few-shot examples for each built-in EntityProfile.

These examples are representative of real drug discovery literature and are
designed to give the LLM strong signal about what to extract and at what
granularity.
"""
from __future__ import annotations

import langextract as lx

# ---------------------------------------------------------------------------
# Chemistry examples
# ---------------------------------------------------------------------------

_CHEMISTRY_EXAMPLE_1 = lx.data.ExampleData(
    text=(
        "Compound 14c (SMILES: Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1) "
        "demonstrated potent inhibitory activity against BCR-ABL1. "
        "The CAS number of imatinib is 152459-95-5 and its molecular formula is C29H31N7O."
    ),
    extractions=[
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="Compound 14c",
        ),
        lx.data.Extraction(
            extraction_class="smiles",
            extraction_text="Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1",
        ),
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="imatinib",
        ),
        lx.data.Extraction(
            extraction_class="cas_number",
            extraction_text="152459-95-5",
        ),
        lx.data.Extraction(
            extraction_class="molecular_formula",
            extraction_text="C29H31N7O",
        ),
    ],
)

_CHEMISTRY_EXAMPLE_2 = lx.data.ExampleData(
    text=(
        "Osimertinib (AZD9291, SMILES: COc1cc2c(Nc3cccc(NC(=O)/C=C/CN(C)C)c3)ncnc2cc1OCCCN1CCOCC1) "
        "is a third-generation EGFR inhibitor approved for NSCLC."
    ),
    extractions=[
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="Osimertinib",
            attributes={"synonyms": "AZD9291"},
        ),
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="AZD9291",
        ),
        lx.data.Extraction(
            extraction_class="smiles",
            extraction_text="COc1cc2c(Nc3cccc(NC(=O)/C=C/CN(C)C)c3)ncnc2cc1OCCCN1CCOCC1",
        ),
    ],
)

CHEMISTRY_EXAMPLES: list[lx.data.ExampleData] = [
    _CHEMISTRY_EXAMPLE_1,
    _CHEMISTRY_EXAMPLE_2,
]

# ---------------------------------------------------------------------------
# Biology examples
# ---------------------------------------------------------------------------

_BIOLOGY_EXAMPLE_1 = lx.data.ExampleData(
    text=(
        "The compound selectively inhibits EGFR (ERBB1) and HER2 (ERBB2) kinases "
        "while sparing ERBB3. KRAS G12C mutations are prevalent in lung adenocarcinoma "
        "and confer resistance to upstream EGFR inhibition. "
        "The PI3K/AKT/mTOR pathway is frequently co-activated in these tumors."
    ),
    extractions=[
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="EGFR",
            attributes={"gene_name": "ERBB1", "protein_family": "kinase"},
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="HER2",
            attributes={"gene_name": "ERBB2", "protein_family": "kinase"},
        ),
        lx.data.Extraction(
            extraction_class="protein_name",
            extraction_text="ERBB3",
        ),
        lx.data.Extraction(
            extraction_class="gene_name",
            extraction_text="KRAS",
            attributes={"full_name": "KRAS G12C"},
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="PI3K/AKT/mTOR pathway",
            attributes={"protein_family": "pathway"},
        ),
    ],
)

_BIOLOGY_EXAMPLE_2 = lx.data.ExampleData(
    text=(
        "TP53 loss-of-function mutations activate MDM2-mediated ubiquitination. "
        "Inhibitors of PD-1/PD-L1 restore T-cell mediated tumor killing. "
        "CDK4 and CDK6 are co-overexpressed in hormone receptor-positive breast cancer."
    ),
    extractions=[
        lx.data.Extraction(
            extraction_class="gene_name",
            extraction_text="TP53",
        ),
        lx.data.Extraction(
            extraction_class="protein_name",
            extraction_text="MDM2",
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="PD-1",
            attributes={"protein_family": "immune checkpoint"},
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="PD-L1",
            attributes={"protein_family": "immune checkpoint"},
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="CDK4",
            attributes={"protein_family": "kinase"},
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="CDK6",
            attributes={"protein_family": "kinase"},
        ),
    ],
)

BIOLOGY_EXAMPLES: list[lx.data.ExampleData] = [
    _BIOLOGY_EXAMPLE_1,
    _BIOLOGY_EXAMPLE_2,
]

# ---------------------------------------------------------------------------
# Bioactivity + assay examples
# ---------------------------------------------------------------------------

_BIOACTIVITY_EXAMPLE_1 = lx.data.ExampleData(
    text=(
        "Compound 7 inhibited EGFR with an IC50 of 2.3 nM in a cell-free enzymatic assay "
        "and showed an EC50 of 45 nM in A549 (human lung adenocarcinoma) cell proliferation assay. "
        "Selectivity over ERBB2 was >100-fold (Ki = 0.8 nM vs 95 nM)."
    ),
    extractions=[
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="IC50 of 2.3 nM",
            attributes={"value": "2.3", "unit": "nM", "assay_type": "IC50"},
        ),
        lx.data.Extraction(
            extraction_class="assay",
            extraction_text="cell-free enzymatic assay",
            attributes={"assay_format": "enzymatic"},
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="EC50 of 45 nM",
            attributes={"value": "45", "unit": "nM", "assay_type": "EC50"},
        ),
        lx.data.Extraction(
            extraction_class="assay",
            extraction_text="A549 (human lung adenocarcinoma) cell proliferation assay",
            attributes={"cell_line": "A549", "organism": "human", "assay_format": "cell proliferation"},
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="Ki = 0.8 nM",
            attributes={"value": "0.8", "unit": "nM", "assay_type": "Ki"},
        ),
    ],
)

BIOACTIVITY_EXAMPLES: list[lx.data.ExampleData] = [_BIOACTIVITY_EXAMPLE_1]

# ---------------------------------------------------------------------------
# Disease examples
# ---------------------------------------------------------------------------

_DISEASE_EXAMPLE_1 = lx.data.ExampleData(
    text=(
        "The compound showed efficacy in non-small cell lung cancer (NSCLC), "
        "acute myeloid leukemia (AML), and triple-negative breast cancer (TNBC). "
        "Secondary indications in inflammatory bowel disease and rheumatoid arthritis "
        "are under investigation."
    ),
    extractions=[
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="non-small cell lung cancer",
            attributes={"abbreviation": "NSCLC", "therapeutic_area": "oncology"},
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="NSCLC",
            attributes={"therapeutic_area": "oncology"},
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="acute myeloid leukemia",
            attributes={"abbreviation": "AML", "therapeutic_area": "oncology"},
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="triple-negative breast cancer",
            attributes={"abbreviation": "TNBC", "therapeutic_area": "oncology"},
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="inflammatory bowel disease",
            attributes={"therapeutic_area": "gastroenterology"},
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="rheumatoid arthritis",
            attributes={"therapeutic_area": "immunology"},
        ),
    ],
)

DISEASE_EXAMPLES: list[lx.data.ExampleData] = [_DISEASE_EXAMPLE_1]

# ---------------------------------------------------------------------------
# Mechanism of action examples
# ---------------------------------------------------------------------------

_MECHANISM_EXAMPLE_1 = lx.data.ExampleData(
    text=(
        "The compound acts as an ATP-competitive inhibitor of EGFR, "
        "binding irreversibly to Cys797 in the kinase domain via a covalent Michael addition. "
        "It is a type I kinase inhibitor with >500-fold selectivity over ERBB2."
    ),
    extractions=[
        lx.data.Extraction(
            extraction_class="mechanism_of_action",
            extraction_text="ATP-competitive inhibitor",
            attributes={"binding_mode": "ATP-competitive"},
        ),
        lx.data.Extraction(
            extraction_class="mechanism_of_action",
            extraction_text="binding irreversibly to Cys797 in the kinase domain via a covalent Michael addition",
            attributes={"binding_mode": "covalent", "selectivity": "irreversible"},
        ),
        lx.data.Extraction(
            extraction_class="mechanism_of_action",
            extraction_text="type I kinase inhibitor",
            attributes={"binding_mode": "type I"},
        ),
    ],
)

MECHANISM_EXAMPLES: list[lx.data.ExampleData] = [_MECHANISM_EXAMPLE_1]

# ---------------------------------------------------------------------------
# Combined FULL examples (one diverse example that spans all entity types)
# ---------------------------------------------------------------------------

_FULL_EXAMPLE_1 = lx.data.ExampleData(
    text=(
        "Gefitinib (ZD1839, SMILES: COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1) "
        "is a first-generation EGFR (ERBB1) tyrosine kinase inhibitor approved for "
        "non-small cell lung cancer (NSCLC). "
        "It inhibits EGFR with an IC50 of 0.033 µM in a cell-free biochemical assay "
        "and shows antiproliferative activity in A431 (human epidermoid carcinoma) cells "
        "with an IC50 of 0.4 µM. "
        "Gefitinib acts as an ATP-competitive, reversible inhibitor. "
        "Resistance frequently arises through KRAS mutations or amplification of MET."
    ),
    extractions=[
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="Gefitinib",
            attributes={"synonyms": "ZD1839"},
        ),
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="ZD1839",
        ),
        lx.data.Extraction(
            extraction_class="smiles",
            extraction_text="COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1",
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="EGFR",
            attributes={"gene_name": "ERBB1", "protein_family": "tyrosine kinase"},
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="non-small cell lung cancer",
            attributes={"abbreviation": "NSCLC", "therapeutic_area": "oncology"},
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="IC50 of 0.033 µM",
            attributes={"value": "0.033", "unit": "µM", "assay_type": "IC50"},
        ),
        lx.data.Extraction(
            extraction_class="assay",
            extraction_text="cell-free biochemical assay",
            attributes={"assay_format": "biochemical"},
        ),
        lx.data.Extraction(
            extraction_class="assay",
            extraction_text="A431 (human epidermoid carcinoma) cells",
            attributes={"cell_line": "A431", "organism": "human"},
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="IC50 of 0.4 µM",
            attributes={"value": "0.4", "unit": "µM", "assay_type": "IC50"},
        ),
        lx.data.Extraction(
            extraction_class="mechanism_of_action",
            extraction_text="ATP-competitive, reversible inhibitor",
            attributes={"binding_mode": "ATP-competitive", "selectivity": "reversible"},
        ),
        lx.data.Extraction(
            extraction_class="gene_name",
            extraction_text="KRAS",
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="MET",
            attributes={"protein_family": "kinase"},
        ),
    ],
)

FULL_EXAMPLES: list[lx.data.ExampleData] = (
    CHEMISTRY_EXAMPLES
    + BIOLOGY_EXAMPLES
    + BIOACTIVITY_EXAMPLES
    + DISEASE_EXAMPLES
    + MECHANISM_EXAMPLES
    + [_FULL_EXAMPLE_1]
)
