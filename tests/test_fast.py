"""Tests for the fast dictionary-based NER extractor."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from structflo.ner._entities import (
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
    derive_id_patterns,
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


def _accessions(seeds: list[str]):
    """Derive patterns from accession seeds only (no compound gazetteer)."""
    return derive_id_patterns({"accession_number": seeds})


class TestDeriveIdPatterns:
    def test_rv_pattern_detected(self):
        descriptions = {p.description for p in _accessions(["Rv1484", "Rv3790"])}
        assert "Rv locus tag" in descriptions

    def test_pdb_pattern_detected(self):
        descriptions = {p.description for p in _accessions(["4TZK"])}
        assert "PDB code" in descriptions

    def test_uniprot_pattern_detected(self):
        descriptions = {p.description for p in _accessions(["P9WGR1"])}
        assert "UniProt accession" in descriptions

    def test_mixed_seeds(self):
        descriptions = {
            p.description for p in _accessions(["Rv0005", "P9WGR1", "4TZK", "WP_003407354"])
        }
        assert "Rv locus tag" in descriptions
        assert "UniProt accession" in descriptions
        assert "PDB code" in descriptions
        assert "NCBI RefSeq" in descriptions

    def test_deduplicates(self):
        descriptions = [p.description for p in _accessions(["Rv0005", "Rv1484", "Rv3790"])]
        assert descriptions.count("Rv locus tag") == 1

    def test_derived_accession_patterns_carry_their_type(self):
        derived = [p for p in _accessions(["Rv0005"]) if p.description == "Rv locus tag"]
        assert [p.entity_type for p in derived] == ["accession_number"]

    def test_compound_patterns_need_no_seed(self):
        """Chemistry registry patterns are curated, not activated by a gazetteer entry."""
        descriptions = {p.description for p in derive_id_patterns({})}
        assert "ChEMBL ID" in descriptions
        assert "SACC series" in descriptions

    def test_compound_patterns_precede_accession_patterns(self):
        """Ordering is load-bearing: the matcher gives the first pattern the span."""
        patterns = derive_id_patterns({"accession_number": ["4TZK", "Rv0005"]})
        types = [p.entity_type for p in patterns]
        assert types.index("accession_number") > max(
            i for i, t in enumerate(types) if t != "accession_number"
        )

    def test_pdb_pattern_requires_a_letter(self):
        """Bare four-digit numbers (years, counts) are not PDB codes."""
        pdb = next(p for p in _accessions(["4TZK"]) if p.description == "PDB code")
        assert pdb.regex.search("4TZK")
        assert pdb.regex.search("1P44")
        assert not pdb.regex.search("in 2019 the trial")
        assert not pdb.regex.search("n = 1234")

    def test_mycobrowser_pattern_needs_locus_digits(self):
        """MTT (viability assay), MTX and MTD are not Mycobrowser loci."""
        mt = next(p for p in _accessions(["MT18B_0001"]) if p.description == "Mycobrowser ID")
        for locus in ["MT0005", "MT18B_0001", "MTB000001"]:
            assert mt.regex.fullmatch(locus), locus
        assert not mt.regex.search("HepG2 MTT, MTX and MTD read-outs")

    def test_cas_check_digit_rejects_dates(self):
        cas = next(p for p in derive_id_patterns({}) if p.description == "CAS number")
        assert cas.validate("50-78-2")  # aspirin
        assert not cas.validate("2020-11-5")  # a date
        assert not cas.validate("100-50-3")  # a dose range


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

    def test_char_offsets_survive_newlines(self):
        """normalize() folds a newline into a space; offsets after it must not drift."""
        matcher = self._simple_matcher(fuzzy_threshold=0)
        text = "Targets:\nINHA and\n\nDPRE1."
        found = {m.canonical: text[m.char_start : m.char_end] for m in matcher.match(text)}
        assert found == {"InhA": "INHA", "DprE1": "DPRE1"}

    def test_regex_accession_matching(self):
        matcher = GazetteerMatcher(
            gazetteers={"target": ["InhA"]},
            id_patterns=_accessions(["Rv0005"]),
            fuzzy_threshold=0,
        )
        matches = matcher.match("The gene Rv1484 encodes InhA")
        accession_matches = [m for m in matches if m.entity_type == "accession_number"]
        assert len(accession_matches) == 1
        assert accession_matches[0].text == "Rv1484"

    def test_regex_matches_rv_with_c_suffix(self):
        matcher = GazetteerMatcher(
            gazetteers={},
            id_patterns=_accessions(["Rv3854c"]),
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

    def test_compound_registry_ids_are_compounds(self):
        """CHEMBL and friends resolve as compound_name via regex — no LLM involved."""
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("CHEMBL4521987, ZINC000012345678 and DB00945 were screened.")
        found = {c.text for c in result.compounds}
        assert {"CHEMBL4521987", "ZINC000012345678", "DB00945"} <= found
        assert all(isinstance(c, ChemicalEntity) for c in result.compounds)
        assert all(c.attributes["match_method"] == "regex" for c in result.compounds)
        assert result.accessions == []

    def test_programme_codes_are_compounds(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("SACC-3060 and TBDA-01187 were profiled against LGENI-4471.")
        assert {"SACC-3060", "TBDA-01187", "LGENI-4471"} <= {c.text for c in result.compounds}
        assert result.accessions == []

    def test_programme_code_not_split_by_pdb_pattern(self):
        """With a PDB seed active, SACC-3060 must be claimed whole, not just '3060'."""
        extractor = FastNERExtractor(
            fuzzy_threshold=0,
            extra_gazetteers={"accession_number": ["4TZK"]},
        )
        result = extractor.extract("SACC-3060 was docked into 4TZK.")
        assert [c.text for c in result.compounds] == ["SACC-3060"]
        assert [a.text for a in result.accessions] == ["4TZK"]

    def test_biological_accessions_still_accessions(self):
        extractor = FastNERExtractor(
            fuzzy_threshold=0,
            extra_gazetteers={"accession_number": ["P9WGR1", "4TZK"]},
        )
        result = extractor.extract("Rv1484 (UniProt P9WPS1) was modelled on PDB 1P44.")
        assert {"Rv1484", "P9WPS1", "1P44"} <= {a.text for a in result.accessions}
        assert all(isinstance(a, AccessionEntity) for a in result.accessions)
        assert result.compounds == []

    def test_mycobrowser_mt_pattern_unregressed(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        result = extractor.extract("The locus MT18B_0001 is annotated in Mycobrowser.")
        assert any(a.text == "MT18B_0001" for a in result.accessions)

    def test_cas_number_extracted_but_dates_are_not(self):
        extractor = FastNERExtractor(fuzzy_threshold=0)
        assert [c.text for c in extractor.extract("aspirin (50-78-2)").compounds] == ["50-78-2"]
        assert extractor.extract("submitted 2020-11-5").compounds == []

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
