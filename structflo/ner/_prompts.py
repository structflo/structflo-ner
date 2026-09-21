"""Prompt strings for each built-in EntityProfile."""

# Shared by every prompt that extracts bioactivity values. The attribute names
# must match the keys used in the few-shot examples: langextract derives the
# output schema from those keys, not from this text.
_BIOACTIVITY_ATTRIBUTES = (
    "For each bioactivity value capture:\n"
    "- value: the number as reported, keeping qualifiers ('>20.0', '<1.0') and dropping "
    "footnote markers ('0.3*' → '0.3').\n"
    "- unit: as written (nM, µM, µg/mL, mg/kg, %, h).\n"
    "- assay_type: the endpoint only, in plain characters (CC₅₀ → CC50). Common endpoints: "
    "IC50, IC90, EC50, EC90, pIC50, Ki, Kd, '% inhibition at <concentration>'; "
    "MIC, MIC50, MIC90, MIC99, MBC, log10 CFU reduction; CC50, TC50, SI (selectivity index); "
    "GI50, TGI, LC50; DC50, Dmax (degraders); ED50, ED90, %TGI, T/C (in vivo); "
    "PRR (parasite reduction ratio), parasite clearance half-life.\n"
    "- assay: the assay, cell line or read-out the value was measured in, e.g. 'MABA', "
    "'LORA', 'HepG2 MTT', 'THP-1 macrophage infection assay', 'asexual blood-stage', "
    "'liver-stage', 'gametocyte', 'NCI-60', 'hERG', 'P. berghei 4-day suppressive test'. "
    "null when no assay is stated.\n"
    "- compound_name: the compound the value belongs to, by its name or identifier "
    "(e.g. 'bedaquiline', 'BTZ043', 'CHEMBL1234', 'SACC-3000'); a document-local label "
    "('7a', 'Compound 9b') only when nothing else names the compound.\n"
)
_BIOACTIVITY_TABLES = (
    "In a data table, extract every cell value as its own bioactivity. An ID or registry "
    "column, when present, supplies the compound_name and the row label is only its synonym; "
    "otherwise the row label is the compound_name. A column header naming an assay or cell "
    "line is the assay, and the endpoint and unit often come from the caption or a footnote "
    "('CC50 in µM')."
)

CHEMISTRY_PROMPT = (
    "Extract chemical entities from the text. "
    "Include: compound names (generic names, IUPAC names, code names like 'Compound 5b', "
    "brand names, and abbreviations), SMILES strings (the exact SMILES notation as written), "
    "CAS registry numbers (e.g. '50-78-2'), and molecular formulas (e.g. 'C9H8O4'). "
    "Do not infer or generate SMILES — only extract them if explicitly present in the text."
)

BIOLOGY_PROMPT = (
    "Extract biological target entities from the text. "
    "Include: protein targets (e.g. 'EGFR', 'CDK4/6', 'PD-L1'), gene names (e.g. 'KRAS', 'TP53', "
    "'BRCA1'), receptor names, enzyme names, and pathway names. "
    "For each target, capture the gene symbol if mentioned alongside a protein name. "
    "Capture the organism context if specified (e.g. 'human', 'mouse')."
)

BIOACTIVITY_PROMPT = (
    "Extract bioactivity measurements and assay data from the text: potency, selectivity, "
    "cytotoxicity and efficacy values.\n"
    + _BIOACTIVITY_ATTRIBUTES
    + _BIOACTIVITY_TABLES
    + "\nAlso extract assay descriptions: cell lines used (e.g. 'HeLa', 'A549'), assay formats "
    "(e.g. 'cell viability', 'binding assay', 'enzymatic assay'), and organisms."
)

DISEASE_PROMPT = (
    "Extract disease names and clinical indications from the text. "
    "Include: cancer types (e.g. 'non-small cell lung cancer', 'AML', 'NSCLC'), "
    "non-oncology diseases (e.g. 'type 2 diabetes', 'rheumatoid arthritis'), "
    "and therapeutic areas (e.g. 'oncology', 'CNS'). "
    "Capture both full names and abbreviations. "
    "For each disease, note the therapeutic area if discernible from context."
)

FULL_PROMPT = (
    "Extract all drug discovery entities from the text. "
    "This includes:\n"
    "- Chemical entities: compound names (generic, IUPAC, code names, brand names), "
    "SMILES strings (only if explicitly written), CAS numbers, molecular formulas.\n"
    "- Biological targets: protein names, gene names, receptor names, enzyme names, pathways.\n"
    "- Bioactivity data: potency, selectivity, cytotoxicity and efficacy values "
    "(attributes below).\n"
    "- Assay information: cell lines, assay formats, experimental organisms.\n"
    "- Diseases and indications: cancer types, disease names, therapeutic areas.\n"
    "- Mechanisms of action: binding modes, inhibition types, selectivity descriptions.\n"
    + _BIOACTIVITY_ATTRIBUTES
    + _BIOACTIVITY_TABLES
    + "\nExtract only what is explicitly stated; do not infer or generate values."
)

# ── Tuberculosis early drug discovery prompts ──────────────────────────

TB_PROMPT = (
    "Extract drug discovery entities from this tuberculosis research text.\n\n"
    + _BIOACTIVITY_ATTRIBUTES
    + "- strain: the organism or strain tested (H37Rv, Erdman, Pf3D7, Dd2, K1), "
    "null when not stated.\n" + _BIOACTIVITY_TABLES + "\n\n"
    "DISAMBIGUATION RULES:\n"
    "- Mycobacterial proteins (e.g. ClpC1, DprE1, InhA, AtpE, MmpL3, QcrB) "
    "are biological targets, NOT compounds.\n"
    "- Rv locus tags (Rv3790, Rv1484), UniProt IDs (P9WPS1), and PDB codes "
    "are accession_number, not target or gene_name.\n"
    "- Compound registry and programme identifiers (CHEMBL4521987, ZINC000012345678, "
    "DB00945, SACC-3060, TBDA-01187, GSK3036656) are compound_name; only Rv locus "
    "tags, UniProt IDs, PDB codes and RefSeq IDs are accession_number.\n"
    "- A compound with both a document-local label (a number with an optional letter: 7a, "
    "12, 'Compound 9b') and a longer identifier (registry ID; programme, partner or vendor "
    "code: CHEMBL…, SACC-…, a ChemBridge number) is extracted once, as the identifier, with "
    "the label in synonyms; its bioactivities use the identifier as compound_name. A label "
    "is the compound_name only when the document gives nothing else.\n"
    "- Enzyme descriptions like 'enoyl-ACP reductase' are product, not target.\n"
    "- 'cell wall', 'lipid metabolism' are functional_category, not mechanism_of_action.\n"
    "- 'fragment screening', 'biochemical assay' are screening_method, not assay.\n"
    "- Use target for proteins in a drug-targeting context, gene_name for loci, "
    "protein_name for non-drug-target proteins.\n\n"
    "Extract only what is explicitly stated; do not infer or generate values."
)

TB_CHEMISTRY_PROMPT = (
    "Extract chemical entities from this tuberculosis drug discovery text. "
    "Include compound names, SMILES (only if explicitly written), CAS numbers, "
    "and molecular formulas. "
    "Mycobacterial proteins (ClpC1, DprE1, InhA, AtpE, etc.) are NOT compounds. "
    "Extract only what is explicitly stated; do not infer or generate values."
)

TB_BIOLOGY_PROMPT = (
    "Extract biological entities from this tuberculosis research text. "
    "Use target for proteins in a drug-targeting context, gene_name for loci, "
    "protein_name for non-drug-target proteins. "
    "Rv locus tags and UniProt IDs are accession_number. "
    "Enzyme descriptions (e.g. 'enoyl-ACP reductase') are product. "
    "Protein functional categories (e.g. 'cell wall', 'lipid metabolism') "
    "are functional_category. "
    "Extract only what is explicitly stated; do not infer or generate values."
)
