# structflo.ner

Drug discovery NER powered by [LangExtract](https://github.com/google/langextract).

Extract compounds, targets, bioactivity data, diseases, and more from scientific text — zero configuration required.

## Install

```bash
pip install structflo-ner
# or with uv
uv add structflo-ner

# optional pandas support
pip install "structflo-ner[dataframe]"
```

## Quick start

```python
from structflo.ner import NERExtractor

extractor = NERExtractor(api_key="YOUR_GEMINI_KEY")
result = extractor.extract(
    "Gefitinib (ZD1839) is a first-generation EGFR inhibitor with IC50 = 0.033 µM approved for NSCLC."
)

print(result.compounds)      # [ChemicalEntity(text='Gefitinib', ...)]
print(result.targets)        # [TargetEntity(text='EGFR', ...)]
print(result.bioactivities)  # [BioactivityEntity(text='IC50 = 0.033 µM', ...)]
print(result.diseases)       # [DiseaseEntity(text='NSCLC', ...)]

df = result.to_dataframe()   # flat pandas DataFrame
```

## Local models via Ollama

Run extraction entirely on your own hardware — no API key needed:

```python
extractor = NERExtractor(
    model_id="gemma3:27b",
    model_url="http://localhost:11434",
)
result = extractor.extract("Sorafenib inhibits VEGFR-2 and RAF kinases.")
```

Any model served by Ollama works (gemma, llama, mistral, qwen, deepseek, etc.).

## Built-in profiles

| Profile | Entity classes |
|---|---|
| `FULL` (default) | compounds, targets, diseases, bioactivities, assays, mechanisms |
| `CHEMISTRY` | compound names, SMILES, CAS numbers, molecular formulas |
| `BIOLOGY` | targets, gene names, protein names |
| `BIOACTIVITY` | bioactivity measurements, assays |
| `DISEASE` | diseases and clinical indications |

```python
from structflo.ner import NERExtractor, CHEMISTRY

extractor = NERExtractor(api_key="YOUR_GEMINI_KEY")
result = extractor.extract(text, profile=CHEMISTRY)
```

Profiles can be merged:

```python
from structflo.ner import CHEMISTRY, BIOLOGY

combined = CHEMISTRY.merge(BIOLOGY)
result = extractor.extract(text, profile=combined)
```

## Custom profiles

```python
from structflo.ner import NERExtractor, EntityProfile

my_profile = EntityProfile(
    name="kinase_inhibitors",
    entity_classes=["compound_name", "smiles", "target", "bioactivity"],
    prompt="Extract kinase inhibitor names, SMILES, targets, and potency values.",
    examples=my_examples,
)
result = extractor.extract(text, profile=my_profile)
```

## Working with results

```python
result.all_entities()   # flat list of every entity
result.to_dict()        # plain dictionary
result.to_dataframe()   # pandas DataFrame (requires structflo-ner[dataframe])
```

## Notebooks

See the [notebooks/](notebooks/) directory for worked examples:

- **01_quickstart.ipynb** — end-to-end extraction with cloud and local models
