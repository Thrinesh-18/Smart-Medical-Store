from app.services.preprocessing import QueryProcessor


def test_normalization():
    qp = QueryProcessor([], {}, {})
    assert qp.normalize_text("ParacetMol!! 500") == "paracetmol 500"


def test_spell_correct():
    qp = QueryProcessor(["paracetamol", "azithromycin"], {}, {})
    assert qp.spell_correct("paracetmol") == "paracetamol"
