"""Correctness and variable numbering checks for the vector encodings."""
from itertools import product
import operator

import pytest

from pysat.formula import IDPool
from pysat.solvers import Solver
from pysat.vector import VecEnc


# both encodings, for the tests that apply to each of them
ENCODINGS = [pytest.param(VecEnc.lex_leq, id='lex_leq'),
             pytest.param(VecEnc.lex_lt, id='lex_lt')]

# each encoding, together with the comparison of tuples it should match
METHODS = [pytest.param(VecEnc.lex_leq, operator.le, id='lex_leq'),
           pytest.param(VecEnc.lex_lt, operator.lt, id='lex_lt')]

# vectors containing something other than a literal
NOT_LITERALS = [pytest.param([0, 1], [2, 3], id='zero'),
                pytest.param([1, 2], [3, 1.5], id='float'),
                pytest.param([1, 'x'], [2, 3], id='string')]

# vectors that share variables or repeat a literal
SHARED = [pytest.param([1, 2, -3], [2, 1, 3], id='swapped'),
          pytest.param([1, 1], [1, -1], id='repeated'),
          pytest.param([1, -2], [1, -2], id='identical'),
          pytest.param([-1, 2, 1], [1], id='longer')]


def vectors(n, m):
    """
        Two vectors of lengths ``n`` and ``m`` over distinct variables, with
        literals of both signs.
    """

    a = [i if i % 2 else -i for i in range(1, n + 1)]
    b = [-i if i % 2 else i for i in range(n + 1, n + m + 1)]

    return a, b


def check(method, compare, a, b, **kwargs):
    """
        Check that the encoding is satisfiable under exactly those
        assignments of the input variables under which ``compare`` holds for
        the values of the two vectors.
    """

    cnf = method(a, b, **kwargs)
    inputs = sorted(set(abs(lit) for lit in a + b))

    with Solver(name='g3', bootstrap_with=cnf.clauses) as solver:
        for bits in product((False, True), repeat=len(inputs)):
            value = dict(zip(inputs, bits))
            assumptions = [v if value[v] else -v for v in inputs]
            left = tuple(value[abs(lit)] == (lit > 0) for lit in a)
            right = tuple(value[abs(lit)] == (lit > 0) for lit in b)
            expected = compare(left, right)

            assert solver.solve(assumptions=assumptions) == expected, (
                'wrong result for {0} and {1}'.format(left, right))

    return cnf


def helper_vars(cnf, a, b):
    """
        The variables of the encoding that do not occur in the vectors.
    """

    inputs = set(abs(lit) for lit in a + b)

    return sorted(set(abs(lit) for cl in cnf.clauses for lit in cl) - inputs)


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


@pytest.mark.parametrize('method', ENCODINGS)
@pytest.mark.parametrize('a, b', NOT_LITERALS)
def test_lex_not_literals(method, a, b):
    with pytest.raises(ValueError):
        method(a, b)


@pytest.mark.parametrize('method', ENCODINGS)
def test_lex_top_id_and_vpool(method):
    with pytest.raises(AssertionError):
        method([1], [2], top_id=5, vpool=IDPool())


@pytest.mark.parametrize('method', ENCODINGS)
def test_lex_inputs_unchanged(method):
    a, b = [1, -2, 3], [4, 5]
    method(a, b)
    assert a == [1, -2, 3] and b == [4, 5]


@pytest.mark.parametrize('method, compare', METHODS)
@pytest.mark.parametrize('n, m', list(product(range(5), repeat=2)))
def test_lex_lengths(method, compare, n, m):
    a, b = vectors(n, m)
    check(method, compare, a, b)


@pytest.mark.parametrize('method, compare', METHODS)
@pytest.mark.parametrize('a, b', SHARED)
def test_lex_shared_variables(method, compare, a, b):
    check(method, compare, a, b)


@pytest.mark.parametrize('n', range(1, 6))
def test_lex_size(n):
    a, b = vectors(n, n)

    cnf = VecEnc.lex_leq(a, b)
    assert len(helper_vars(cnf, a, b)) == n - 1
    assert len(cnf.clauses) == 3 * n - 2

    cnf = VecEnc.lex_lt(a, b)
    assert len(helper_vars(cnf, a, b)) == n - 1
    assert len(cnf.clauses) == 3 * n - 1


@pytest.mark.parametrize('method, compare', METHODS)
def test_lex_top_id(method, compare):
    a, b = vectors(4, 4)

    # the helper variables come right after top_id
    cnf = check(method, compare, a, b, top_id=20)
    assert helper_vars(cnf, a, b) == [21, 22, 23]
    assert cnf.nv == 23

    # a top_id below the input variables is raised above them
    cnf = check(method, compare, a, b, top_id=3)
    assert helper_vars(cnf, a, b) == [9, 10, 11]
    assert cnf.nv == 11

    # without helper variables, nv still covers top_id
    cnf = method([1], [2], top_id=20)
    assert cnf.nv == 20
