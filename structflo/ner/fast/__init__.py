"""Fast dictionary-based NER for TB drug discovery — no LLM required.

Quick start::

    from structflo.ner.fast import FastNERExtractor

    extractor = FastNERExtractor()
    result = extractor.extract(
        "Bedaquiline inhibits AtpE (Rv1305) in M. tuberculosis."
    )
    print(result.compounds)
    print(result.targets)
    df = result.to_dataframe()

Custom gazetteers::

    extractor = FastNERExtractor(gazetteer_dir="/path/to/my/gazetteers")
"""

from structflo.ner.fast.extractor import FastNERExtractor

__all__ = ["FastNERExtractor"]
