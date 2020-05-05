from .. import calc
import pytest

numeric_datas = [
    (1, 1, 2),
    (2, 2, 4),
    (3, 3, 6),
    (4, 4, 8),
    (5, 5, 10),
]


@pytest.mark.parametrize("a, b, expect", numeric_datas)
def test_multiple(a, b, expect):
    assert calc.add(a, b) == expect


numeric_datas = [
    (1, 1, 0),
    (2, 2, 0),
    (3, 3, 0),
    (4, 4, 0),
    (5, 5, 0),
]


@pytest.mark.parametrize("a, b, expect", numeric_datas)
def test_minus(a, b, expect):
    assert calc.minus(a, b) == expect


def test_reverse():
    assert calc.reverse(["a", "b", "c"]) == ["c", "b", "a"]


def test_lambda():
    assert calc.lambda_c([1, 2, 3]) == [1, 4, 9]
