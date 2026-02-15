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
        assert len(TB.examples) == 4
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
