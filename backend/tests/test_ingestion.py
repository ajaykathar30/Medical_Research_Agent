import json

from ai.nodes.ingestion import _extract, _to_documents


def test_extract_parses_json_string():
    raw = json.dumps([{"a": 1}])
    assert _extract(raw) == [{"a": 1}]


def test_extract_handles_invalid_json_string():
    assert _extract("not json") == []


def test_extract_parses_mcp_text_blocks():
    raw = [{"type": "text", "text": json.dumps({"a": 1})}]
    assert _extract(raw) == [{"a": 1}]


def test_extract_unwraps_result_key():
    assert _extract({"result": [{"a": 1}]}) == [{"a": 1}]


def test_extract_wraps_single_dict_without_result_key():
    assert _extract({"a": 1}) == [{"a": 1}]


def test_extract_passes_through_plain_list():
    items = [{"a": 1}, {"b": 2}]
    assert _extract(items) == items


def test_extract_returns_empty_for_unrecognized_type():
    assert _extract(42) == []


def test_to_documents_builds_literature_doc():
    items = [{"title": "Title", "abstract": "Abstract", "pmid": "123", "url": "http://x", "year": 2020}]
    docs = _to_documents("search_literature", items, topic="aspirin")
    assert len(docs) == 1
    assert "Title" in docs[0].page_content
    assert docs[0].metadata["source"] == "literature"
    assert docs[0].metadata["source_id"] == "123"


def test_to_documents_skips_literature_with_no_content():
    items = [{"title": "", "abstract": ""}]
    assert _to_documents("search_literature", items, topic="x") == []


def test_to_documents_builds_trial_doc():
    items = [{
        "title": "Trial", "summary": "Summary", "status": "Recruiting",
        "phases": "Phase 2", "lead_sponsor": "Acme", "nct_id": "NCT1", "url": "http://t",
    }]
    docs = _to_documents("search_trials", items, topic="x")
    assert len(docs) == 1
    assert docs[0].metadata["source"] == "trials"
    assert docs[0].metadata["status"] == "Recruiting"


def test_to_documents_builds_adverse_event_doc():
    items = [{
        "drug": "Ibuprofen",
        "top_reactions": [{"reaction": "Nausea", "count": 10}],
        "disclaimer": "FAERS data is voluntary.",
    }]
    docs = _to_documents("get_adverse_events", items, topic="x")
    assert len(docs) == 1
    assert "Nausea: 10 reports" in docs[0].page_content
    assert docs[0].metadata["source"] == "safety"


def test_to_documents_builds_label_doc_when_found():
    items = [{"found": True, "drug": "Aspirin", "indications": "Pain relief"}]
    docs = _to_documents("get_drug_label", items, topic="x")
    assert len(docs) == 1
    assert docs[0].metadata["source"] == "label"


def test_to_documents_skips_label_when_not_found():
    items = [{"found": False, "drug": "Aspirin"}]
    assert _to_documents("get_drug_label", items, topic="x") == []


def test_to_documents_skips_non_dict_items():
    assert _to_documents("search_literature", ["not-a-dict"], topic="x") == []
