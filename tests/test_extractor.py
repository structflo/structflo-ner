"""Tests for NERExtractor — mocks lx.extract to avoid real API calls."""

from __future__ import annotations

from unittest.mock import MagicMock

import langextract as lx

from structflo.ner import (
    BIOLOGY,
    CHEMISTRY,
    FULL,
    TB,
    TB_BIOLOGY,
    TB_CHEMISTRY,
    AccessionEntity,
    ChemicalEntity,
    NERExtractor,
    NERResult,
    TargetEntity,
)


def _make_annotated_doc(extractions: list[lx.data.Extraction]) -> lx.data.AnnotatedDocument:
    return lx.data.AnnotatedDocument(
        text="sample text",
        extractions=extractions,
    )


class TestNERExtractorInit:
    def test_defaults(self):
        extractor = NERExtractor()
        assert extractor._model_id == "gemini-2.5-flash"
        assert extractor._default_profile is FULL
        assert extractor._extra_examples == []

    def test_custom_profile(self):
        extractor = NERExtractor(profile=CHEMISTRY)
        assert extractor._default_profile is CHEMISTRY

    def test_extra_examples_stored(self):
        extra = [MagicMock(spec=lx.data.ExampleData)]
        extractor = NERExtractor(extra_examples=extra)
        assert extractor._extra_examples == extra


class TestNERExtractorExtract:
    def _extractor_with_mock(self, extractions: list[lx.data.Extraction]) -> NERExtractor:
        extractor = NERExtractor(api_key="test-key")
        doc = _make_annotated_doc(extractions)
        extractor._run_extraction = MagicMock(return_value=doc)
        return extractor

    def test_single_text_returns_ner_result(self):
        extractor = self._extractor_with_mock([])
        result = extractor.extract("Some text")
        assert isinstance(result, NERResult)

    def test_list_text_returns_list(self):
        extractor = self._extractor_with_mock([])
        results = extractor.extract(["text one", "text two"])
        assert isinstance(results, list)
        assert len(results) == 2

    def test_compounds_populated(self):
        extractions = [
            lx.data.Extraction(extraction_class="compound_name", extraction_text="Gefitinib"),
            lx.data.Extraction(extraction_class="smiles", extraction_text="CCO"),
        ]
        extractor = self._extractor_with_mock(extractions)
        result = extractor.extract("Gefitinib (CCO)")
        assert len(result.compounds) == 2
        assert result.compounds[0].text == "Gefitinib"
        assert isinstance(result.compounds[0], ChemicalEntity)

    def test_targets_populated(self):
        extractions = [
            lx.data.Extraction(
                extraction_class="target",
                extraction_text="EGFR",
                attributes={"gene_name": "ERBB1"},
            )
        ]
        extractor = self._extractor_with_mock(extractions)
        result = extractor.extract("EGFR inhibitor")
        assert len(result.targets) == 1
        assert result.targets[0].text == "EGFR"
        assert isinstance(result.targets[0], TargetEntity)
        assert result.targets[0].attributes["gene_name"] == "ERBB1"

    def test_unclassified_entity_bucketed(self):
        extractions = [
            lx.data.Extraction(extraction_class="novel_type", extraction_text="some entity"),
        ]
        extractor = self._extractor_with_mock(extractions)
        result = extractor.extract("some entity")
        assert len(result.unclassified) == 1
        assert result.unclassified[0].text == "some entity"

    def test_per_call_profile_override(self):
        extractor = NERExtractor(profile=FULL)
        doc = _make_annotated_doc([])
        extractor._run_extraction = MagicMock(return_value=doc)

        extractor.extract("text", profile=BIOLOGY)
        call_profile = extractor._run_extraction.call_args[0][1]
        assert call_profile is BIOLOGY

    def test_default_profile_used_when_no_override(self):
        extractor = NERExtractor(profile=CHEMISTRY)
        doc = _make_annotated_doc([])
        extractor._run_extraction = MagicMock(return_value=doc)

        extractor.extract("text")
        call_profile = extractor._run_extraction.call_args[0][1]
        assert call_profile is CHEMISTRY

    def test_source_text_preserved_in_result(self):
        extractor = self._extractor_with_mock([])
        result = extractor.extract("My source text")
        assert result.source_text == "My source text"


class TestProviderRouting:
    """Explicit provider selection routes deterministically via ModelConfig,
    instead of relying on langextract's model_id regex inference."""

    def _run_and_capture(self, monkeypatch, **init_kwargs):
        from structflo.ner import extractor as extractor_mod

        captured = {}

        def fake_extract(**kwargs):
            captured.update(kwargs)
            return _make_annotated_doc([])

        monkeypatch.setattr(extractor_mod.lx, "extract", fake_extract)
        NERExtractor(**init_kwargs).extract("some text")
        return captured

    def test_provider_defaults_to_none(self):
        assert NERExtractor()._provider is None

    def test_provider_stored(self):
        assert NERExtractor(provider="openai")._provider == "openai"

    def test_no_provider_uses_legacy_model_id_path(self, monkeypatch):
        captured = self._run_and_capture(
            monkeypatch, model_id="gemma3:27b", model_url="http://ollama:11434"
        )
        assert captured["model_id"] == "gemma3:27b"
        assert captured["model_url"] == "http://ollama:11434"
        assert "config" not in captured

    def test_explicit_provider_uses_config_not_top_level_model_id(self, monkeypatch):
        captured = self._run_and_capture(
            monkeypatch,
            provider="ollama",
            model_id="medgemma:latest",
            model_url="http://ollama:11434",
        )
        # Deterministic routing: config carries provider + model_id, and the
        # top-level model_id/model_url are NOT passed (would conflict with config).
        assert "config" in captured
        assert "model_id" not in captured
        assert "model_url" not in captured
        config = captured["config"]
        assert config.provider == "ollama"
        assert config.model_id == "medgemma:latest"

    def test_ollama_provider_kwargs_carry_base_url_and_num_ctx(self, monkeypatch):
        captured = self._run_and_capture(
            monkeypatch,
            provider="ollama",
            model_id="medgemma:latest",
            model_url="http://ollama:11434",
        )
        pk = captured["config"].provider_kwargs
        assert pk["base_url"] == "http://ollama:11434"
        assert pk["num_ctx"] == 8192

    def test_cloud_provider_kwargs_carry_api_key(self, monkeypatch):
        captured = self._run_and_capture(
            monkeypatch, provider="openai", model_id="gpt-4o", api_key="sk-test"
        )
        pk = captured["config"].provider_kwargs
        assert pk["api_key"] == "sk-test"
        assert "num_ctx" not in pk
        assert "base_url" not in pk


class TestBuildPrompt:
    def test_prompt_includes_entity_class_constraint(self):
        extractor = NERExtractor()
        prompt = extractor._build_prompt(CHEMISTRY)
        assert "ONLY these entity classes" in prompt
        for cls in CHEMISTRY.entity_classes:
            assert cls in prompt

    def test_prompt_includes_all_tb_classes(self):
        extractor = NERExtractor()
        prompt = extractor._build_prompt(TB)
        for cls in TB.entity_classes:
            assert cls in prompt


class TestFilterExtractions:
    def test_keeps_valid_extractions(self):
        doc = _make_annotated_doc(
            [
                lx.data.Extraction(extraction_class="compound_name", extraction_text="Aspirin"),
                lx.data.Extraction(extraction_class="target", extraction_text="COX-2"),
            ]
        )
        filtered = NERExtractor._filter_extractions(doc, {"compound_name", "target"})
        assert len(filtered.extractions) == 2

    def test_drops_hallucinated_classes(self):
        doc = _make_annotated_doc(
            [
                lx.data.Extraction(extraction_class="compound_name", extraction_text="Aspirin"),
                lx.data.Extraction(extraction_class="enzyme", extraction_text="COX-2"),
                lx.data.Extraction(extraction_class="toxicity", extraction_text="hepatotoxic"),
            ]
        )
        filtered = NERExtractor._filter_extractions(doc, {"compound_name", "target"})
        assert len(filtered.extractions) == 1
        assert filtered.extractions[0].extraction_text == "Aspirin"

    def test_empty_extractions(self):
        doc = _make_annotated_doc([])
        filtered = NERExtractor._filter_extractions(doc, {"compound_name"})
        assert len(filtered.extractions) == 0


class TestBuildExamples:
    def test_extra_examples_appended(self):
        extra = lx.data.ExampleData(text="extra", extractions=[])
        extractor = NERExtractor(extra_examples=[extra])
        examples = extractor._build_examples(CHEMISTRY)
        assert extra in examples
        assert all(e in examples for e in CHEMISTRY.examples)

    def test_no_extra_examples_returns_profile_examples(self):
        extractor = NERExtractor()
        examples = extractor._build_examples(CHEMISTRY)
        assert examples == CHEMISTRY.examples


class TestEntityProfileMerge:
    def test_merge_combines_entity_classes(self):
        merged = CHEMISTRY.merge(BIOLOGY)
        for cls in CHEMISTRY.entity_classes + BIOLOGY.entity_classes:
            assert cls in merged.entity_classes

    def test_merge_deduplicates_entity_classes(self):
        merged = CHEMISTRY.merge(CHEMISTRY)
        assert len(merged.entity_classes) == len(set(merged.entity_classes))

    def test_merge_combines_examples(self):
        merged = CHEMISTRY.merge(BIOLOGY)
        assert len(merged.examples) == len(CHEMISTRY.examples) + len(BIOLOGY.examples)


class TestTBProfile:
    def test_tb_has_all_entity_classes(self):
        assert "compound_name" in TB.entity_classes
        assert "target" in TB.entity_classes
        assert "disease" in TB.entity_classes
        assert "bioactivity" in TB.entity_classes
        assert "assay" in TB.entity_classes
        assert "mechanism_of_action" in TB.entity_classes
        assert "accession_number" in TB.entity_classes
        assert "product" in TB.entity_classes
        assert "functional_category" in TB.entity_classes
        assert "screening_method" in TB.entity_classes

    def test_tb_chemistry_is_subset(self):
        for cls in TB_CHEMISTRY.entity_classes:
            assert cls in TB.entity_classes

    def test_tb_biology_is_subset(self):
        for cls in TB_BIOLOGY.entity_classes:
            assert cls in TB.entity_classes

    def test_tb_examples_count(self):
        assert len(TB.examples) == 5
        assert len(TB_CHEMISTRY.examples) == 2
        assert len(TB_BIOLOGY.examples) == 2

    def test_tb_profile_extract(self):
        extractor = NERExtractor(profile=TB)
        doc = _make_annotated_doc(
            [
                lx.data.Extraction(
                    extraction_class="compound_name",
                    extraction_text="Bedaquiline",
                ),
                lx.data.Extraction(
                    extraction_class="target",
                    extraction_text="AtpE",
                    attributes={"gene_name": "Rv1305"},
                ),
                lx.data.Extraction(
                    extraction_class="accession_number",
                    extraction_text="Rv1305",
                ),
                lx.data.Extraction(
                    extraction_class="disease",
                    extraction_text="MDR-TB",
                ),
            ]
        )
        extractor._run_extraction = MagicMock(return_value=doc)
        result = extractor.extract("Bedaquiline targets AtpE (Rv1305) in MDR-TB.")
        assert len(result.compounds) == 1
        assert len(result.targets) == 1
        assert len(result.accessions) == 1
        assert isinstance(result.accessions[0], AccessionEntity)
        assert result.accessions[0].text == "Rv1305"
        assert len(result.diseases) == 1
