# structflo.ner.fast — Dictionary-Based NER for TB Drug Discovery

Fast, deterministic entity extraction using curated YAML gazetteers. No LLM, no API key, no network — runs in milliseconds.

## Install

```bash
uv add "structflo-ner[fast]"

# with DataFrame support
uv add "structflo-ner[fast,dataframe]"
```

## Quick Start

```python
from structflo.ner.fast import FastNERExtractor

fast = FastNERExtractor()
result = fast.extract("Bedaquiline inhibits AtpE (Rv1305) in MDR-TB.")

print(result.compounds)  # [ChemicalEntity(text='Bedaquiline', ...)]
print(result.targets)  # [TargetEntity(text='AtpE', ...)]
print(result.accessions)  # [AccessionEntity(text='Rv1305', ...)]
print(result.diseases)  # [DiseaseEntity(text='MDR-TB', ...)]

df = result.to_dataframe()
result.display()  # interactive HTML in Jupyter
```

## How It Works

Three-phase matching, all without an LLM:

### Phase 1 — Exact Dictionary Match
Looks up every text span against a normalized dictionary built from the YAML gazetteers. Auto-derived variants include:
- **Case variants**: InhA, inha, INHA
- **Hyphen-optional**: DprE-1 ↔ DprE1, MDR-TB ↔ MDRTB
- **Period-optional**: M. tuberculosis ↔ M tuberculosis
- **Greek letters**: β-lactam ↔ beta-lactam

Word boundaries are enforced — "Rho" won't match inside "Rhodamine".

### Phase 1b — Regex Patterns (Structured Identifiers)
Two families of pattern run here, compound patterns first. Order matters: the
matcher gives each span to the first pattern that claims it, and the PDB rule
would otherwise take the `3060` out of `SACC-3060`.

**Compound identifiers** — curated in `_loader.py`, always active, no seed needed:

| Pattern | Matches | Class |
|---|---|---|
| `CHEMBL\d+`, `SCHEMBL\d+`, `CHEBI:\d+` | ChEMBL / SureChEMBL / ChEBI | `compound_name` |
| `DB\d{5}`, `ZINC\d{6,}`, `HMDB\d{5,7}`, `DTX[SC]ID\d+` | DrugBank, ZINC, HMDB, CompTox | `compound_name` |
| `NSC-?\d{3,6}`, `NCGC\d{5,}`, InChIKey | NCI, NCATS, InChIKey | `compound_name` |
| `EN300-\d+`, `Z\d{8,10}`, `MolPort-…`, `MCULE-…`, `STK\d{6}` | vendor catalogues | `compound_name` |
| `SACC-?\d{3,}`, `TBDA-?\d{3,}`, `TBA-?\d{3,}`, `GSK-?\d{3,}`, … | TB / ND programme codes | `compound_name` |
| `\d{2,7}-\d{2}-\d` + check digit | CAS registry numbers | `cas_number` |

The CAS check digit is validated — without it the pattern also matches dates
(`2020-11-5`) and dose ranges (`100-50-3`).

**Accession numbers** — seed entries in `accession_number.yml` activate a family,
so a deployment's own gazetteer decides which ones apply:

| Seed | Auto-derived Pattern | Matches |
|---|---|---|
| `Rv0005` | `Rv\d{4}[c]?` | All Rv locus tags |
| `MT0005` | `MT\w+` | Mycobrowser IDs |
| `P9WGR1` | `[OPQ][0-9][A-Z0-9]{3}[0-9]` | UniProt accessions |
| `4TZK` | `(?=[A-Z0-9]{0,3}[A-Z])[1-9][A-Z0-9]{3}` | PDB codes |
| `WP_003407354` | `WP_\d+` | NCBI RefSeq proteins |

The PDB pattern requires at least one letter; without that guard it matches
every four-digit number in the corpus.

### Phase 2 — Fuzzy Match
Unmatched "entity-like" tokens (capitalized, contain digits, length ≥ 4) are compared against the dictionary using rapidfuzz. Catches typos and minor variants.

```python
# Configurable threshold (0–100, default 85)
strict = FastNERExtractor(fuzzy_threshold=0)  # disable fuzzy
lenient = FastNERExtractor(fuzzy_threshold=75)  # more permissive
```

## Gazetteers

YAML files live in `structflo/ner/fast/gazetteers/`. Each file is a simple list of names — **nothing else**:

```yaml
# target.yml
- InhA
- DprE1
- MmpL3
- AtpE
```

The filename (without `.yml`) becomes the `entity_type`. Built-in gazetteers:

| File | Entity Type | Coverage |
|---|---|---|
| `target.yml` | target → `TargetEntity` | ~80 TB drug targets |
| `gene_name.yml` | gene_name → `TargetEntity` | ~75 Mtb gene names |
| `compound_name.yml` | compound_name → `ChemicalEntity` | ~50 TB compounds & abbreviations |
| `disease.yml` | disease → `DiseaseEntity` | TB disease variants |
| `accession_number.yml` | accession_number → `AccessionEntity` | Seed entries → regex patterns |
| `screening_method.yml` | screening_method → `ScreeningMethodEntity` | ~35 screening approaches |
| `functional_category.yml` | functional_category → `FunctionalCategoryEntity` | ~25 Mtb functional categories |
| `product.yml` | product → `ProductEntity` | ~35 gene product descriptions |

## Adding New Gazetteers

### Option 1: Add to existing files
Edit a YAML file and add names:

```yaml
# target.yml
- InhA
- DprE1
- MyNewTarget  # just add it
```

### Option 2: Create a new YAML file
Drop a new `.yml` file into any directory:

```yaml
# my_gazetteers/assay.yml
- resazurin assay
- luciferase reporter assay
- disk diffusion assay
```

```python
fast = FastNERExtractor(gazetteer_dir="my_gazetteers/")
```

### Option 3: Add terms programmatically

```python
fast = FastNERExtractor(
    extra_gazetteers={
        "target": ["NovelTarget1", "NovelTarget2"],
        "compound_name": ["CompoundXYZ"],
    }
)
```

## Output Compatibility

`FastNERExtractor` produces identical `NERResult` objects as the LLM-based `NERExtractor`. Everything downstream works the same:

```python
result.all_entities()  # flat list
result.to_dict()  # serializable dict
result.to_dataframe()  # pandas DataFrame
result.display()  # interactive HTML
```

Each entity includes `match_method` ("exact", "regex", or "fuzzy") and `canonical` (the gazetteer term it matched) in its `attributes` dict.

## Fast vs LLM

| | `FastNERExtractor` | `NERExtractor` |
|---|---|---|
| Speed | ~1–5 ms per abstract | ~2–5 s per abstract |
| Novel entities | Only known terms | Discovers new entities |
| Context | String matching | Full contextual understanding |
| Cost | Free | API calls or GPU |
| Setup | Zero config | API key or Ollama |

**Recommended workflow**: Fast extractor as first pass (bulk screening), LLM extractor as second pass (deep analysis on interesting papers).
