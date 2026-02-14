"""Prompt strings for each built-in EntityProfile."""

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
    "Extract bioactivity measurements and assay data from the text. "
    "Include: potency values (IC50, EC50, Ki, Kd, GI50, CC50), selectivity ratios, "
    "percent inhibition values, and Hill coefficients. "
    "For each value, capture the numeric value, unit (nM, µM, mM), and measurement type. "
    "Also extract assay descriptions: cell lines used (e.g. 'HeLa', 'A549'), assay formats "
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
    "- Bioactivity data: IC50, EC50, Ki, Kd, and other potency/selectivity measurements "
    "with their numeric values and units.\n"
    "- Assay information: cell lines, assay formats, experimental organisms.\n"
    "- Diseases and indications: cancer types, disease names, therapeutic areas.\n"
    "- Mechanisms of action: binding modes, inhibition types, selectivity descriptions.\n"
    "Extract only what is explicitly stated; do not infer or generate values."
)
