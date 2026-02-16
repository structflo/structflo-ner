"""Tests for entity dataclasses and NERResult serialization."""

import dataclasses

import pytest

from structflo.ner._entities import (
    AccessionEntity,
    AssayEntity,
    BioactivityEntity,
    ChemicalEntity,
    DiseaseEntity,
    FunctionalCategoryEntity,
    MechanismEntity,
    NEREntity,
    NERResult,
    ProductEntity,
    ScreeningMethodEntity,
    TargetEntity,
    entity_class_for,
    field_name_for,
)


class TestEntityClassFor:
    def test_known_chemistry_classes(self):
        assert entity_class_for("compound_name") is ChemicalEntity
        assert entity_class_for("smiles") is ChemicalEntity
        assert entity_class_for("cas_number") is ChemicalEntity
        assert entity_class_for("molecular_formula") is ChemicalEntity

    def test_known_biology_classes(self):
        assert entity_class_for("target") is TargetEntity
        assert entity_class_for("gene_name") is TargetEntity
        assert entity_class_for("protein_name") is TargetEntity

    def test_known_other_classes(self):
        assert entity_class_for("disease") is DiseaseEntity
        assert entity_class_for("bioactivity") is BioactivityEntity
        assert entity_class_for("assay") is AssayEntity
        assert entity_class_for("mechanism_of_action") is MechanismEntity

    def test_known_tb_classes(self):
        assert entity_class_for("accession_number") is AccessionEntity
        assert entity_class_for("product") is ProductEntity
        assert entity_class_for("functional_category") is FunctionalCategoryEntity
        assert entity_class_for("screening_method") is ScreeningMethodEntity

    def test_unknown_class_falls_back_to_base(self):
        assert entity_class_for("unknown_type") is NEREntity


class TestFieldNameFor:
    def test_all_known_types(self):
        assert field_name_for(ChemicalEntity) == "compounds"
        assert field_name_for(TargetEntity) == "targets"
        assert field_name_for(DiseaseEntity) == "diseases"
        assert field_name_for(BioactivityEntity) == "bioactivities"
        assert field_name_for(AssayEntity) == "assays"
        assert field_name_for(MechanismEntity) == "mechanisms"
        assert field_name_for(AccessionEntity) == "accessions"
        assert field_name_for(ProductEntity) == "products"
        assert field_name_for(FunctionalCategoryEntity) == "functional_categories"
        assert field_name_for(ScreeningMethodEntity) == "screening_methods"

    def test_unknown_falls_back_to_unclassified(self):
        assert field_name_for(NEREntity) == "unclassified"


class TestNEREntity:
    def test_frozen(self):
        e = ChemicalEntity(text="Gefitinib", entity_type="compound_name")
        with pytest.raises(dataclasses.FrozenInstanceError):
            e.text = "other"  # type: ignore[misc]

    def test_default_attributes_empty(self):
        e = ChemicalEntity(text="Gefitinib", entity_type="compound_name")
        assert e.attributes == {}

    def test_optional_fields_default_none(self):
        e = ChemicalEntity(text="Gefitinib", entity_type="compound_name")
        assert e.char_start is None
        assert e.char_end is None
        assert e.alignment is None


class TestNERResult:
    def _make_result(self) -> NERResult:
        return NERResult(
            source_text="Gefitinib inhibits EGFR in NSCLC with IC50=33nM.",
            compounds=[ChemicalEntity(text="Gefitinib", entity_type="compound_name")],
            targets=[TargetEntity(text="EGFR", entity_type="target")],
            diseases=[DiseaseEntity(text="NSCLC", entity_type="disease")],
            bioactivities=[
                BioactivityEntity(
                    text="IC50=33nM",
                    entity_type="bioactivity",
                    attributes={"value": "33", "unit": "nM", "assay_type": "IC50"},
                )
            ],
        )

    def test_all_entities_flat(self):
        result = self._make_result()
        all_e = result.all_entities()
        assert len(all_e) == 4
        texts = {e.text for e in all_e}
        assert texts == {"Gefitinib", "EGFR", "NSCLC", "IC50=33nM"}

    def test_to_dict_keys(self):
        result = self._make_result()
        d = result.to_dict()
        assert set(d.keys()) == {
            "source_text",
            "compounds",
            "targets",
            "diseases",
            "bioactivities",
            "assays",
            "mechanisms",
            "accessions",
            "products",
            "functional_categories",
            "screening_methods",
            "strains",
            "unclassified",
        }
        assert d["source_text"] == result.source_text
        assert len(d["compounds"]) == 1
        assert d["compounds"][0]["text"] == "Gefitinib"

    def test_to_dict_attributes_preserved(self):
        result = self._make_result()
        d = result.to_dict()
        bio = d["bioactivities"][0]
        assert bio["attributes"] == {"value": "33", "unit": "nM", "assay_type": "IC50"}

    def test_to_dataframe_requires_pandas(self, monkeypatch):
        import builtins

        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "pandas":
                raise ImportError("no pandas")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        result = self._make_result()
        with pytest.raises(ImportError, match="pandas"):
            result.to_dataframe()

    def test_to_dataframe_shape(self):
        pytest.importorskip("pandas")
        result = self._make_result()
        df = result.to_dataframe()
        assert len(df) == 4
        assert "text" in df.columns
        assert "entity_type" in df.columns
        assert "entity_class" in df.columns
