from rag_store import rag_store


def test_add_and_query_text():
    text = (
        "This document explains Python testing.\n"
        "Use pytest to run tests.\n"
        "Testing helps prevent regressions.\n"
        "Use fixtures for setup and teardown."
    )

    doc_id = rag_store.add_text(text, doc_id='test-doc')
    results = rag_store.query(doc_id, 'How do I run tests?', top_k=2)
    assert results
    assert any('pytest' in r['chunk'] or 'tests' in r['chunk'] for r in results)
