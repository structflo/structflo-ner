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
            attributes={
                "cell_line": "A549",
                "organism": "human",
                "assay_format": "cell proliferation",
            },
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

# ---------------------------------------------------------------------------
# Tuberculosis early drug discovery examples
# ---------------------------------------------------------------------------

_TB_EXAMPLE_1 = lx.data.ExampleData(
    text=(
        "Bedaquiline (TMC207) targets the c subunit of mycobacterial ATP synthase "
        "(AtpE, Rv1305, UniProt P9WPS1), a proton pump classified under intermediary "
        "metabolism and respiration. The gene product is ATP synthase subunit c. "
        "In a biochemical screening campaign, bedaquiline showed a MIC of 0.03 ug/mL "
        "against M. tuberculosis H37Rv in a Microplate Alamar Blue Assay (MABA) and "
        "demonstrated bactericidal activity in a mouse chronic infection model. "
        "Bedaquiline is approved for multidrug-resistant tuberculosis (MDR-TB)."
    ),
    extractions=[
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="Bedaquiline",
            attributes={"synonyms": "TMC207"},
        ),
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="TMC207",
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="ATP synthase",
            attributes={"protein_family": "ATP synthase", "organism": "M. tuberculosis"},
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="AtpE",
            attributes={"gene_name": "Rv1305", "protein_family": "ATP synthase"},
        ),
        lx.data.Extraction(
            extraction_class="accession_number",
            extraction_text="Rv1305",
        ),
        lx.data.Extraction(
            extraction_class="accession_number",
            extraction_text="P9WPS1",
            attributes={"database": "UniProt"},
        ),
        lx.data.Extraction(
            extraction_class="functional_category",
            extraction_text="intermediary metabolism and respiration",
        ),
        lx.data.Extraction(
            extraction_class="product",
            extraction_text="ATP synthase subunit c",
        ),
        lx.data.Extraction(
            extraction_class="screening_method",
            extraction_text="biochemical screening",
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="MIC of 0.03 ug/mL",
            attributes={"value": "0.03", "unit": "ug/mL", "assay_type": "MIC", "strain": "H37Rv"},
        ),
        lx.data.Extraction(
            extraction_class="assay",
            extraction_text="Microplate Alamar Blue Assay",
            attributes={"abbreviation": "MABA", "assay_format": "whole-cell", "strain": "H37Rv"},
        ),
        lx.data.Extraction(
            extraction_class="assay",
            extraction_text="mouse chronic infection model",
            attributes={"organism": "mouse", "assay_format": "in vivo"},
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="multidrug-resistant tuberculosis",
            attributes={"abbreviation": "MDR-TB", "therapeutic_area": "infectious disease"},
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="MDR-TB",
            attributes={"therapeutic_area": "infectious disease"},
        ),
    ],
)

_TB_EXAMPLE_2 = lx.data.ExampleData(
    text=(
        "BTZ043, a benzothiazinone identified through whole-cell phenotypic screening, "
        "irreversibly inhibits DprE1 (Rv3790), the decaprenylphosphoryl-beta-D-ribose "
        "2-epimerase involved in cell wall and cell processes, via covalent modification "
        "of the active-site cysteine Cys387. BTZ043 exhibited a MIC of 1 ng/mL against "
        "M. tuberculosis H37Rv and a MIC of 4 ng/mL against the Erdman strain. "
        "Its optimized analog PBTZ169 (Macozinone) showed a MIC of 0.6 ng/mL. "
        "Both compounds disrupt cell wall arabinan biosynthesis and are active against "
        "extensively drug-resistant TB (XDR-TB)."
    ),
    extractions=[
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="BTZ043",
        ),
        lx.data.Extraction(
            extraction_class="screening_method",
            extraction_text="whole-cell phenotypic screening",
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="DprE1",
            attributes={
                "gene_name": "Rv3790",
                "protein_family": "epimerase",
            },
        ),
        lx.data.Extraction(
            extraction_class="accession_number",
            extraction_text="Rv3790",
        ),
        lx.data.Extraction(
            extraction_class="product",
            extraction_text="decaprenylphosphoryl-beta-D-ribose 2-epimerase",
        ),
        lx.data.Extraction(
            extraction_class="functional_category",
            extraction_text="cell wall and cell processes",
        ),
        lx.data.Extraction(
            extraction_class="mechanism_of_action",
            extraction_text="covalent modification of the active-site cysteine Cys387",
            attributes={"binding_mode": "covalent", "selectivity": "irreversible"},
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="MIC of 1 ng/mL",
            attributes={"value": "1", "unit": "ng/mL", "assay_type": "MIC", "strain": "H37Rv"},
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="MIC of 4 ng/mL",
            attributes={"value": "4", "unit": "ng/mL", "assay_type": "MIC", "strain": "Erdman"},
        ),
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="PBTZ169",
            attributes={"synonyms": "Macozinone"},
        ),
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="Macozinone",
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="MIC of 0.6 ng/mL",
            attributes={"value": "0.6", "unit": "ng/mL", "assay_type": "MIC"},
        ),
        lx.data.Extraction(
            extraction_class="mechanism_of_action",
            extraction_text="cell wall arabinan biosynthesis",
            attributes={"binding_mode": "cell wall biosynthesis inhibition"},
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="extensively drug-resistant TB",
            attributes={"abbreviation": "XDR-TB", "therapeutic_area": "infectious disease"},
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="XDR-TB",
            attributes={"therapeutic_area": "infectious disease"},
        ),
    ],
)

_TB_EXAMPLE_3 = lx.data.ExampleData(
    text=(
        "Compound 14a inhibited InhA (Rv1484), the NADH-dependent enoyl-ACP reductase "
        "involved in lipid metabolism, with an IC50 of 85 nM in a biochemical assay. "
        "Whole-cell activity was assessed using the REMA against M. tuberculosis H37Rv, "
        "yielding a MIC90 of 0.5 uM. The compound also showed intracellular activity "
        "in a THP-1 macrophage infection assay with an EC50 of 1.2 uM. "
        "In a Low Oxygen Recovery Assay (LORA), it retained activity against non-replicating "
        "bacilli with a MIC of 3.1 uM. No cytotoxicity was observed in HepG2 cells "
        "up to 50 uM (CC50 >50 uM)."
    ),
    extractions=[
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="Compound 14a",
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="InhA",
            attributes={"gene_name": "Rv1484", "protein_family": "reductase"},
        ),
        lx.data.Extraction(
            extraction_class="accession_number",
            extraction_text="Rv1484",
        ),
        lx.data.Extraction(
            extraction_class="product",
            extraction_text="NADH-dependent enoyl-ACP reductase",
        ),
        lx.data.Extraction(
            extraction_class="functional_category",
            extraction_text="lipid metabolism",
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="IC50 of 85 nM",
            attributes={"value": "85", "unit": "nM", "assay_type": "IC50"},
        ),
        lx.data.Extraction(
            extraction_class="screening_method",
            extraction_text="biochemical assay",
        ),
        lx.data.Extraction(
            extraction_class="assay",
            extraction_text="REMA",
            attributes={
                "full_name": "Resazurin Microtiter Assay",
                "assay_format": "whole-cell",
                "strain": "H37Rv",
            },
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="MIC90 of 0.5 uM",
            attributes={"value": "0.5", "unit": "uM", "assay_type": "MIC90", "strain": "H37Rv"},
        ),
        lx.data.Extraction(
            extraction_class="assay",
            extraction_text="THP-1 macrophage infection assay",
            attributes={"cell_line": "THP-1", "assay_format": "intracellular"},
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="EC50 of 1.2 uM",
            attributes={"value": "1.2", "unit": "uM", "assay_type": "EC50"},
        ),
        lx.data.Extraction(
            extraction_class="assay",
            extraction_text="Low Oxygen Recovery Assay",
            attributes={"abbreviation": "LORA", "assay_format": "non-replicating"},
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="MIC of 3.1 uM",
            attributes={"value": "3.1", "unit": "uM", "assay_type": "MIC"},
        ),
        lx.data.Extraction(
            extraction_class="assay",
            extraction_text="HepG2 cells",
            attributes={"cell_line": "HepG2", "assay_format": "cytotoxicity"},
        ),
        lx.data.Extraction(
            extraction_class="bioactivity",
            extraction_text="CC50 >50 uM",
            attributes={"value": ">50", "unit": "uM", "assay_type": "CC50"},
        ),
    ],
)

_TB_EXAMPLE_4 = lx.data.ExampleData(
    text=(
        "Using fragment screening and affinity-based methods, Q203 (Telacebec) was "
        "identified as an inhibitor of the cytochrome bc1 complex subunit QcrB (Rv2196), "
        "an oxidoreductase classified under intermediary metabolism and respiration. "
        "SQ109 disrupts trehalose monomycolate transport by inhibiting MmpL3 (Rv0206c), "
        "a membrane transporter involved in cell wall and cell processes. "
        "Resistance to isoniazid frequently arises through mutations in katG (Rv1908c) "
        "or the inhA promoter region. Rifampicin resistance maps to rpoB (Rv0667). "
        "These compounds are under evaluation for active pulmonary TB and latent TB "
        "infection (LTBI)."
    ),
    extractions=[
        lx.data.Extraction(
            extraction_class="screening_method",
            extraction_text="fragment screening",
        ),
        lx.data.Extraction(
            extraction_class="screening_method",
            extraction_text="affinity-based methods",
        ),
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="Q203",
            attributes={"synonyms": "Telacebec"},
        ),
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="Telacebec",
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="QcrB",
            attributes={"gene_name": "Rv2196", "protein_family": "oxidoreductase"},
        ),
        lx.data.Extraction(
            extraction_class="accession_number",
            extraction_text="Rv2196",
        ),
        lx.data.Extraction(
            extraction_class="functional_category",
            extraction_text="intermediary metabolism and respiration",
        ),
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="SQ109",
        ),
        lx.data.Extraction(
            extraction_class="mechanism_of_action",
            extraction_text="trehalose monomycolate transport",
            attributes={"binding_mode": "transport inhibition"},
        ),
        lx.data.Extraction(
            extraction_class="target",
            extraction_text="MmpL3",
            attributes={"gene_name": "Rv0206c", "protein_family": "transporter"},
        ),
        lx.data.Extraction(
            extraction_class="accession_number",
            extraction_text="Rv0206c",
        ),
        lx.data.Extraction(
            extraction_class="functional_category",
            extraction_text="cell wall and cell processes",
        ),
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="isoniazid",
        ),
        lx.data.Extraction(
            extraction_class="gene_name",
            extraction_text="katG",
        ),
        lx.data.Extraction(
            extraction_class="accession_number",
            extraction_text="Rv1908c",
        ),
        lx.data.Extraction(
            extraction_class="gene_name",
            extraction_text="inhA",
        ),
        lx.data.Extraction(
            extraction_class="compound_name",
            extraction_text="Rifampicin",
        ),
        lx.data.Extraction(
            extraction_class="gene_name",
            extraction_text="rpoB",
        ),
        lx.data.Extraction(
            extraction_class="accession_number",
            extraction_text="Rv0667",
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="pulmonary TB",
            attributes={"therapeutic_area": "infectious disease"},
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="latent TB infection",
            attributes={"abbreviation": "LTBI", "therapeutic_area": "infectious disease"},
        ),
        lx.data.Extraction(
            extraction_class="disease",
            extraction_text="LTBI",
            attributes={"therapeutic_area": "infectious disease"},
        ),
    ],
)

TB_EXAMPLES: list[lx.data.ExampleData] = [
    _TB_EXAMPLE_1,
    _TB_EXAMPLE_2,
    _TB_EXAMPLE_3,
    _TB_EXAMPLE_4,
]

TB_CHEMISTRY_EXAMPLES: list[lx.data.ExampleData] = [
    _TB_EXAMPLE_1,
    _TB_EXAMPLE_2,
]

TB_BIOLOGY_EXAMPLES: list[lx.data.ExampleData] = [
    _TB_EXAMPLE_2,
    _TB_EXAMPLE_4,
]
