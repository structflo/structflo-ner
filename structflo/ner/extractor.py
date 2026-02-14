"""NERExtractor: the main user-facing class for drug discovery NER."""

from __future__ import annotations

import langextract as lx

from structflo.ner._entities import NERResult
from structflo.ner._mapping import annotated_doc_to_result
from structflo.ner.profiles import FULL, EntityProfile


class NERExtractor:
    """Extract drug discovery entities from text with zero configuration.

    Example::

        from structflo.ner import NERExtractor

        # Cloud model (Gemini)
        extractor = NERExtractor(api_key="YOUR_GEMINI_KEY")

        # Local model via Ollama
        extractor = NERExtractor(
            model_id="gemma3:27b",
            model_url="http://localhost:11434",
        )

        result = extractor.extract(
            "Gefitinib (ZD1839) inhibits EGFR with IC50 = 0.033 µM in NSCLC."
        )

        print(result.compounds)      # [ChemicalEntity(text='Gefitinib', ...)]
        print(result.targets)        # [TargetEntity(text='EGFR', ...)]
        print(result.bioactivities)  # [BioactivityEntity(text='IC50 = 0.033 µM', ...)]
        df = result.to_dataframe()

    Args:
        model_id: LLM model identifier passed to langextract. Defaults to
            ``"gemini-2.5-flash"``.
        api_key: API key for the LLM provider. If ``None``, uses the provider's
            default environment-variable lookup.
        model_url: Base URL for self-hosted models (e.g. Ollama at
            ``"http://localhost:11434"``). When set, langextract routes
            requests to this endpoint instead of a cloud API.
        profile: Default :class:`EntityProfile` to use when no per-call
            profile is specified. Defaults to :data:`FULL`.
        extra_examples: Additional :class:`lx.data.ExampleData` objects that
            are appended to the profile's built-in examples on every call.
            Useful for domain-specific fine-tuning without replacing the
            built-in examples.
        langextract_kwargs: Additional keyword arguments forwarded verbatim to
            :func:`lx.extract`. Use this escape hatch for advanced settings
            like ``extraction_passes``, ``max_char_buffer``, or a custom
            ``model`` instance.
    """

    def __init__(
        self,
        model_id: str = "gemini-2.5-flash",
        api_key: str | None = None,
        model_url: str | None = None,
        profile: EntityProfile = FULL,
        extra_examples: list[lx.data.ExampleData] | None = None,
        langextract_kwargs: dict | None = None,
    ) -> None:
        self._model_id = model_id
        self._api_key = api_key
        self._model_url = model_url
        self._default_profile = profile
        self._extra_examples = extra_examples or []
        self._langextract_kwargs = langextract_kwargs or {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract(
        self,
        text: str | list[str],
        profile: EntityProfile | None = None,
    ) -> NERResult | list[NERResult]:
        """Extract drug discovery entities from text.

        Args:
            text: Input text (or list of texts) to process.
            profile: Override the default profile for this call only.

        Returns:
            A :class:`NERResult` for a single string input, or a list of
            :class:`NERResult` when a list of strings is provided.
        """
        active_profile = profile if profile is not None else self._default_profile
        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]

        results = []
        for single_text in texts:
            doc = self._run_extraction(single_text, active_profile)
            results.append(annotated_doc_to_result(doc, single_text))

        return results if is_batch else results[0]

    # ------------------------------------------------------------------
    # Protected — override in subclasses to customise behaviour
    # ------------------------------------------------------------------

    def _build_examples(self, profile: EntityProfile) -> list[lx.data.ExampleData]:
        """Combine profile examples with any user-supplied extra examples."""
        return profile.examples + self._extra_examples

    def _build_prompt(self, profile: EntityProfile) -> str:
        """Return the prompt string for the given profile."""
        return profile.prompt

    def _run_extraction(
        self,
        text: str,
        profile: EntityProfile,
    ) -> lx.data.AnnotatedDocument:
        """Call lx.extract and return the AnnotatedDocument."""
        examples = self._build_examples(profile)
        prompt = self._build_prompt(profile)

        kwargs: dict = dict(self._langextract_kwargs)
        kwargs.setdefault("use_schema_constraints", True)
        kwargs.setdefault("show_progress", False)

        result = lx.extract(
            text_or_documents=text,
            prompt_description=prompt,
            examples=examples,
            model_id=self._model_id,
            api_key=self._api_key,
            model_url=self._model_url,
            **kwargs,
        )

        # lx.extract returns a list when given a list; we always pass a single string
        if isinstance(result, list):
            return result[0]
        return result
