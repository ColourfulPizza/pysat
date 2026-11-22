"""Correctness and variable numbering checks for the vector encodings."""
import pytest

from pysat.formula import IDPool
from pysat.vector import VecEnc


# both encodings, for the tests that apply to each of them
encodings = [VecEnc.lex_leq, VecEnc.lex_lt]
names = ['lex_leq', 'lex_lt']


def test_lex_leq_example():
    # the example from the docstring of lex_leq
    cnf = VecEnc.lex_leq([1, 2], [3, 4])
    assert cnf.clauses == [[-1, 3], [-1, 5], [3, 5], [-5, -2, 4]]
    assert cnf.nv == 5


def test_lex_lt_example():
    # the example from the docstring of lex_lt
    cnf = VecEnc.lex_lt([1, 2], [3, 4])
    assert cnf.clauses == [[-1, 3], [-1, 5], [3, 5], [-5, -2], [-5, 4]]
    assert cnf.nv == 5


@pytest.mark.parametrize('method', encodings, ids=names)
@pytest.mark.parametrize('a, b', [([0, 1], [2, 3]),
                                  ([1, 2], [3, 1.5]),
                                  ([1, 'x'], [2, 3])])
def test_lex_not_literals(method, a, b):
    with pytest.raises(ValueError):
        method(a, b)


@pytest.mark.parametrize('method', encodings, ids=names)
def test_lex_top_id_and_vpool(method):
    with pytest.raises(AssertionError):
        method([1], [2], top_id=5, vpool=IDPool())


@pytest.mark.parametrize('method', encodings, ids=names)
def test_lex_inputs_unchanged(method):
    a, b = [1, -2, 3], [4, 5]
    method(a, b)
    assert a == [1, -2, 3] and b == [4, 5]
