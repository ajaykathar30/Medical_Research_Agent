from ai.graph import route_after_decider


def test_routes_to_answer_when_not_relevant():
    state = {"relevant": False, "needs_retrieval": True, "topic_cached": True}
    assert route_after_decider(state) == "answer"


def test_routes_to_answer_when_no_retrieval_needed():
    state = {"relevant": True, "needs_retrieval": False, "topic_cached": True}
    assert route_after_decider(state) == "answer"


def test_routes_to_retrieval_on_cache_hit():
    state = {"relevant": True, "needs_retrieval": True, "topic_cached": True}
    assert route_after_decider(state) == "retrieval"


def test_routes_to_ingestion_on_cache_miss():
    state = {"relevant": True, "needs_retrieval": True, "topic_cached": False}
    assert route_after_decider(state) == "ingestion"


def test_defaults_to_answer_for_empty_state():
    assert route_after_decider({}) == "answer"
