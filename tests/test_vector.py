"""Correctness and variable numbering checks for the vector encodings."""
from pysat.vector import VecEnc


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
