from ai.nodes.retrieval import _compute_limits


def test_compute_limits_splits_budget_by_weight():
    assert _compute_limits(4, 8800) == [3520, 2640, 1760, 880]


def test_compute_limits_handles_fewer_docs_than_weights():
    assert _compute_limits(2, 8800) == [5028, 3771]


def test_compute_limits_handles_zero_docs():
    assert _compute_limits(0, 8800) == []
