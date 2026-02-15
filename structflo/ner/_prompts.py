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

# ── Tuberculosis early drug discovery prompts ──────────────────────────

TB_PROMPT = (
    "Extract drug discovery entities from this tuberculosis (TB) research text. "
    "This is specialized for early-stage TB drug discovery: target identification, "
    "hit finding, fragment screening, lead optimization, and in vitro/in vivo profiling.\n\n"
    "COMPOUNDS:\n"
    "- First-line drugs: Isoniazid (INH), Rifampicin (RIF), Ethambutol (EMB), Pyrazinamide (PZA).\n"
    "- New-generation: Bedaquiline (TMC207), Delamanid (OPC-67683), Pretomanid (PA-824), "
    "Linezolid, Clofazimine, Moxifloxacin.\n"
    "- Pipeline: BTZ043, PBTZ169 (Macozinone), SQ109, Q203 (Telacebec), TBA-7371, "
    "GSK656, OPC-167832, SPR720, BRD-8000, Sanfetrinem, DG167, NITD-304, NITD-349.\n"
    "- Extract compound names (generic, code names, series IDs like 'Compound 14a'), "
    "SMILES (only if explicitly present), CAS numbers, and molecular formulas.\n\n"
    "BIOLOGICAL TARGETS:\n"
    "- Mycobacterial proteins are biological targets, NOT compounds. Examples: "
    "ClpC1, DprE1, InhA, MmpL3, AtpE, QcrB, Pks13, KasA, GyrA, GyrB, MbtA, "
    "EthA, PanC, LdtMt2, RpoB, PncA, EmbB, Ag85.\n"
    "- Use 'target' for proteins with drug-targeting context. "
    "Use 'gene_name' for gene loci and gene symbols. "
    "Use 'protein_name' for proteins without drug-targeting context.\n\n"
    "ACCESSION NUMBERS:\n"
    "- Rv locus tags (Rv3596c, Rv3790, Rv1484, Rv0206c, Rv1305, etc.), "
    "UniProt accessions (P9WPS1, P9WGR1, etc.), PDB codes (6CQ4, 5V3Y, etc.).\n"
    "- Extract each accession as a separate entity.\n\n"
    "PRODUCTS:\n"
    "- Gene product descriptions from databases: enzyme names, protein function descriptions "
    "(e.g., 'enoyl-ACP reductase', 'ATP synthase subunit c', "
    "'decaprenylphosphoryl-beta-D-ribose 2-epimerase').\n\n"
    "FUNCTIONAL CATEGORIES:\n"
    "- Mycobacterial protein functional categories: intermediary metabolism and respiration, "
    "cell wall and cell processes, virulence/detoxification/adaptation, "
    "lipid metabolism, information pathways, regulatory proteins, "
    "PE/PPE family, conserved hypotheticals.\n\n"
    "SCREENING METHODS:\n"
    "- Early drug discovery screening approaches: affinity-based screening, "
    "biochemical assay, DNA encoded library (DEL), fragment screening, "
    "hypomorph screening, whole-cell phenotypic screening, "
    "target-based HTS, virtual screening, SPR-based screening.\n\n"
    "DISEASES:\n"
    "- Tuberculosis variants: TB, MDR-TB, XDR-TB, pre-XDR-TB, TDR-TB, "
    "LTBI, active TB, pulmonary TB, extrapulmonary TB, TB meningitis, miliary TB.\n"
    "- Capture both full names and abbreviations as separate entities.\n\n"
    "BIOACTIVITY:\n"
    "- MIC (against H37Rv, Erdman, CDC1551, clinical isolates, MDR/XDR strains), "
    "MIC90, MBC, IC50, EC50, Ki. "
    "Capture numeric value, unit (ug/mL, uM, nM), measurement type, and strain context.\n\n"
    "ASSAYS:\n"
    "- MABA, LORA, REMA, macrophage infection (THP-1, J774, RAW264.7), "
    "time-kill kinetics, checkerboard synergy, mouse acute/chronic infection models, "
    "guinea pig aerosol model.\n\n"
    "MECHANISMS OF ACTION:\n"
    "- Mycolic acid biosynthesis inhibition, ATP synthase inhibition, "
    "cell wall arabinan biosynthesis disruption, menaquinone biosynthesis inhibition, "
    "trehalose monomycolate transport inhibition, covalent modification, "
    "DNA gyrase inhibition, decaprenylphosphoryl-beta-D-ribose oxidation.\n\n"
    "Extract only what is explicitly stated; do not infer or generate values."
)

TB_CHEMISTRY_PROMPT = (
    "Extract chemical entities from this tuberculosis drug discovery text. "
    "Include: compound names (generic names, IUPAC names, clinical codes like 'TMC207', "
    "series identifiers like 'Compound 14a', brand names), "
    "SMILES strings (only if explicitly written), CAS registry numbers, and molecular formulas. "
    "TB compound naming conventions: first-line drugs (INH, RIF, EMB, PZA), "
    "second-line drugs (Bedaquiline, Delamanid, Pretomanid), "
    "pipeline compounds (BTZ043, PBTZ169, SQ109, Q203, TBA-7371, GSK656, DG167, NITD-304). "
    "Capture all synonyms and code names as separate compound_name entities."
)

TB_BIOLOGY_PROMPT = (
    "Extract biological target entities from this tuberculosis research text. "
    "Focus on mycobacterial drug targets and their identifiers. "
    "Key targets: DprE1, InhA, MmpL3, AtpE, ClpC1, ClpP1P2, QcrB, Pks13, KasA, "
    "GyrA, GyrB, MbtA, EthA, PanC, LdtMt2, RpoB, PncA, EmbB, Ag85 complex. "
    "These are biological targets, NOT compounds. "
    "Use 'target' for proteins with drug-targeting context, 'gene_name' for gene loci "
    "and gene symbols, 'protein_name' for other proteins. "
    "Extract Rv locus tags and UniProt accessions as 'accession_number'. "
    "Extract enzyme names and protein function descriptions as 'product'. "
    "Extract functional categories (cell wall, lipid metabolism, virulence, etc.) "
    "as 'functional_category'."
)
