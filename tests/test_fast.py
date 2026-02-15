"""Tests for the fast dictionary-based NER extractor."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

pytest.importorskip("rapidfuzz", reason="rapidfuzz required for fast NER tests")
pytest.importorskip("yaml", reason="PyYAML required for fast NER tests")

from structflo.ner._entities import (  # noqa: E402
    AccessionEntity,
    ChemicalEntity,
    DiseaseEntity,
    FunctionalCategoryEntity,
    NERResult,
    ProductEntity,
    ScreeningMethodEntity,
    TargetEntity,
)
from structflo.ner.fast._loader import (
    derive_accession_patterns,
    load_all_gazetteers,
    load_gazetteer,
)
from structflo.ner.fast._matcher import GazetteerMatcher
from structflo.ner.fast._normalize import expand_variants, normalize
from structflo.ner.fast.extractor import FastNERExtractor

# ---------------------------------------------------------------------------
# _normalize tests
# ---------------------------------------------------------------------------


class TestNormalize:
    def test_lowercase(self):
        assert normalize("InhA") == "inha"

    def test_collapse_whitespace(self):
        assert normalize("cell  wall   and") == "cell wall and"

    def test_unify_dashes(self):
        assert normalize("MDR\u2013TB") == "mdr-tb"  # en-dash → hyphen

    def test_strip(self):
        assert normalize("  hello  ") == "hello"


class TestExpandVariants:
    def test_includes_original_and_lowercase(self):
        variants = expand_variants("InhA")
        assert "InhA" in variants
        assert "inha" in variants

    def test_hyphen_optional(self):
        variants = expand_variants("MDR-TB")
        assert "MDRTB" in variants or "mdrtb" in variants

    def test_alphanumeric_boundary_hyphenation(self):
        variants = expand_variants("DprE1")
        normalized = {normalize(v) for v in variants}
        assert "dpre-1" in normalized

    def test_period_optional(self):
        variants = expand_variants("M. tuberculosis")
        normalized = {normalize(v) for v in variants}
        assert "m tuberculosis" in normalized

    def test_greek_expansion(self):
        variants = expand_variants("β-lactam")
        normalized = {normalize(v) for v in variants}
        assert "beta-lactam" in normalized


# ---------------------------------------------------------------------------
# _loader tests
# ---------------------------------------------------------------------------


class TestLoadGazetteer:
    def test_load_single_file(self, tmp_path: Path):
        yml = tmp_path / "target.yml"
        yml.write_text("- InhA\n- DprE1\n- MmpL3\n")
        entity_type, terms = load_gazetteer(yml)
        assert entity_type == "target"
        assert terms == ["InhA", "DprE1", "MmpL3"]

    def test_filename_becomes_entity_type(self, tmp_path: Path):
        yml = tmp_path / "compound_name.yml"
        yml.write_text("- Bedaquiline\n")
        entity_type, _terms = load_gazetteer(yml)
        assert entity_type == "compound_name"

    def test_invalid_format_raises(self, tmp_path: Path):
        yml = tmp_path / "bad.yml"
        yml.write_text("key: value\n")
        with pytest.raises(ValueError, match="must be a YAML list"):
            load_gazetteer(yml)

    def test_skips_empty_entries(self, tmp_path: Path):
        yml = tmp_path / "target.yml"
        yml.write_text("- InhA\n- \n- DprE1\n")
        _entity_type, terms = load_gazetteer(yml)
        assert terms == ["InhA", "DprE1"]


class TestLoadAllGazetteers:
    def test_loads_multiple_files(self, tmp_path: Path):
        (tmp_path / "target.yml").write_text("- InhA\n")
        (tmp_path / "disease.yml").write_text("- TB\n- MDR-TB\n")
        gazetteers = load_all_gazetteers(tmp_path)
        assert "target" in gazetteers
        assert "disease" in gazetteers
        assert gazetteers["target"] == ["InhA"]
        assert len(gazetteers["disease"]) == 2

    def test_missing_dir_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_all_gazetteers(tmp_path / "nonexistent")

    def test_loads_default_gazetteers(self):
        gazetteers = load_all_gazetteers()
        assert len(gazetteers) > 0
        assert "target" in gazetteers


class TestDeriveAccessionPatterns:
    def test_rv_pattern_detected(self):
        patterns = derive_accession_patterns(["Rv1484", "Rv3790"])
        assert len(patterns) >= 1
        descriptions = {desc for _, desc in patterns}
        assert "Rv locus tag" in descriptions

    def test_pdb_pattern_detected(self):
        patterns = derive_accession_patterns(["4TZK"])
        descriptions = {desc for _, desc in patterns}
        assert "PDB code" in descriptions

    def test_uniprot_pattern_detected(self):
        patterns = derive_accession_patterns(["P9WGR1"])
        descriptions = {desc for _, desc in patterns}
        assert "UniProt accession" in descriptions

    def test_mixed_seeds(self):
        patterns = derive_accession_patterns(["Rv0005", "P9WGR1", "4TZK", "WP_003407354"])
        descriptions = {desc for _, desc in patterns}
        assert "Rv locus tag" in descriptions
        assert "UniProt accession" in descriptions
        assert "PDB code" in descriptions
        assert "NCBI RefSeq" in descriptions

    def test_deduplicates(self):
        patterns = derive_accession_patterns(["Rv0005", "Rv1484", "Rv3790"])
        descriptions = [desc for _, desc in patterns]
        assert descriptions.count("Rv locus tag") == 1


# ---------------------------------------------------------------------------
# _matcher tests
# ---------------------------------------------------------------------------


class TestGazetteerMatcher:
    def _simple_matcher(self, **kwargs) -> GazetteerMatcher:
        return GazetteerMatcher(
            gazetteers={
                "target": ["InhA", "DprE1", "MmpL3"],
                "compound_name": ["Bedaquiline", "Isoniazid"],
                "disease": ["TB", "MDR-TB"],
            },
            **kwargs,
        )

    def test_exact_match_case_sensitive(self):
        matcher = self._simple_matcher(fuzzy_threshold=0)
        matches = matcher.match("InhA is a target")
        assert len(matches) >= 1
        assert any(m.text == "InhA" and m.entity_type == "target" for m in matches)

    def test_exact_match_case_insensitive(self):
        matcher = self._simple_matcher(fuzzy_threshold=0)
        matches = matcher.match("bedaquiline is a drug")
        assert any(m.canonical == "Bedaquiline" for m in matches)

    def test_word_boundary_enforcement(self):
        matcher = self._simple_matcher(fuzzy_threshold=0)
        # "TB" should not match inside "ESTABLISH"
        matches = matcher.match("We ESTABLISH the protocol")
        tb_matches = [m for m in matches if m.canonical == "TB"]
        assert len(tb_matches) == 0

    def test_no_substring_match(self):
        matcher = GazetteerMatcher(
            gazetteers={"target": ["Rho"]},
            fuzzy_threshold=0,
        )
        matches = matcher.match("Rhodamine staining was performed")
        assert len(matches) == 0

    def test_multiple_matches_in_text(self):
        matcher = self._simple_matcher(fuzzy_threshold=0)
        matches = matcher.match("Bedaquiline targets InhA in TB")
        entity_types = {m.entity_type for m in matches}
        assert "compound_name" in entity_types
        assert "target" in entity_types
        assert "disease" in entity_types

    def test_char_offsets_correct(self):
        matcher = self._simple_matcher(fuzzy_threshold=0)
        text = "InhA is essential"
        matches = matcher.match(text)
        inha_matches = [m for m in matches if m.canonical == "InhA"]
        assert len(inha_matches) == 1
        m = inha_matches[0]
        assert text[m.char_start : m.char_end] == "InhA"

    def test_regex_accession_matching(self):
        patterns = derive_accession_patterns(["Rv0005"])
        matcher = GazetteerMatcher(
            gazetteers={"target": ["InhA"]},
            accession_patterns=patterns,
            fuzzy_threshold=0,
        )
        matches = matcher.match("The gene Rv1484 encodes InhA")
        accession_matches = [m for m in matches if m.entity_type == "accession_number"]
        assert len(accession_matches) == 1
        assert accession_matches[0].text == "Rv1484"

    def test_regex_matches_rv_with_c_suffix(self):
        patterns = derive_accession_patterns(["Rv3854c"])
        matcher = GazetteerMatcher(
            gazetteers={},
            accession_patterns=patterns,
            fuzzy_threshold=0,
        )
        matches = matcher.match("Rv3854c encodes EthA")
        assert any(m.text == "Rv3854c" for m in matches)

    def test_fuzzy_matching(self):
        matcher = self._simple_matcher(fuzzy_threshold=80)
        # "Isoniazi" is a close misspelling of "Isoniazid"
        matches = matcher.match("Isoniazi was administered")
        fuzzy_matches = [m for m in matches if m.match_method == "fuzzy"]
        assert any(m.canonical == "Isoniazid" for m in fuzzy_matches)

    def test_fuzzy_disabled_when_threshold_zero(self):
        matcher = self._simple_matcher(fuzzy_threshold=0)
        matches = matcher.match("Isoniazi was administered")
        assert not any(m.canonical == "Isoniazid" for m in matches)

    def test_matches_sorted_by_position(self):
        matcher = self._simple_matcher(fuzzy_threshold=0)
        matches = matcher.match("Bedaquiline inhibits InhA in TB patients")
        if len(matches) >= 2:
            for i in range(len(matches) - 1):
                assert matches[i].char_start <= matches[i + 1].char_start


# ---------------------------------------------------------------------------
# FastNERExtractor integration tests
# ---------------------------------------------------------------------------


class TestFastNERExtractor:
    def test_basic_extraction(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("Bedaquiline inhibits AtpE in tuberculosis")
        assert isinstance(result, NERResult)
        assert len(result.compounds) >= 1
        assert any(c.text == "Bedaquiline" for c in result.compounds)
        assert len(result.targets) >= 1
        assert any(t.text == "AtpE" for t in result.targets)

    def test_batch_extraction(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        results = extractor.extract(["InhA is essential", "Bedaquiline treats TB"])
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(r, NERResult) for r in results)

    def test_source_text_preserved(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        text = "InhA is a target"
        result = extractor.extract(text)
        assert result.source_text == text

    def test_typed_entities(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("Bedaquiline targets InhA in MDR-TB")
        assert all(isinstance(c, ChemicalEntity) for c in result.compounds)
        assert all(isinstance(t, TargetEntity) for t in result.targets)
        assert all(isinstance(d, DiseaseEntity) for d in result.diseases)

    def test_accession_regex(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("The gene Rv2043c encodes PptT")
        assert len(result.accessions) >= 1
        assert any(a.text == "Rv2043c" for a in result.accessions)
        assert all(isinstance(a, AccessionEntity) for a in result.accessions)

    def test_to_dataframe(self):
        pytest.importorskip("pandas")
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("Bedaquiline inhibits AtpE (Rv1305) in TB")
        df = result.to_dataframe()
        assert len(df) >= 3
        assert "text" in df.columns
        assert "entity_type" in df.columns
        assert "char_start" in df.columns

    def test_custom_gazetteer_dir(self, tmp_path: Path):
        (tmp_path / "target.yml").write_text("- MyTarget\n")
        extractor = FastNERExtractor(gazetteer_dir=tmp_path, fuzzy_threshold=0)
        result = extractor.extract("MyTarget is interesting")
        assert len(result.targets) == 1
        assert result.targets[0].text == "MyTarget"

    def test_extra_gazetteers(self):
        extractor = FastNERExtractor(
            extra_gazetteers={"target": ["NovelTarget"]},
            fuzzy_threshold=0,
        )
        result = extractor.extract("NovelTarget shows promise")
        assert any(t.text == "NovelTarget" for t in result.targets)

    def test_multiword_entity(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("fragment-based screening identified hits")
        assert len(result.screening_methods) >= 1
        assert any(isinstance(s, ScreeningMethodEntity) for s in result.screening_methods)

    def test_functional_category(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("Proteins involved in lipid metabolism are essential")
        assert len(result.functional_categories) >= 1
        assert all(isinstance(f, FunctionalCategoryEntity) for f in result.functional_categories)

    def test_product_entity(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("enoyl-ACP reductase is the target of isoniazid")
        assert len(result.products) >= 1
        assert all(isinstance(p, ProductEntity) for p in result.products)

    def test_tb_abstract(self):
        text = textwrap.dedent("""\
            Bedaquiline (TMC207) is a diarylquinoline that inhibits the
            mycobacterial ATP synthase subunit c encoded by atpE (Rv1305).
            It shows potent activity against Mycobacterium tuberculosis
            including MDR-TB and XDR-TB strains such as H37Rv. The compound
            was identified through whole-cell screening and targets the
            energy metabolism pathway.
        """)
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract(text)

        # Should find multiple entity types
        assert len(result.compounds) >= 1, "Expected at least one compound"
        assert len(result.diseases) >= 1, "Expected at least one disease"
        assert len(result.accessions) >= 1, "Expected at least one accession"

    def test_match_method_in_attributes(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("InhA is essential")
        for entity in result.all_entities():
            assert "match_method" in entity.attributes

    def test_empty_text(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("")
        assert len(result.all_entities()) == 0

    def test_no_false_positives_on_common_words(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("The cat sat on the mat and ate fish")
        assert len(result.all_entities()) == 0
