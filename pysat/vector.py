from pysat.formula import CNF


class VecEnc:

    @classmethod
    def lex_leq(cls, a, b, top_id=None, vpool=None):
        """
            Create a CNF encoding of the lexicographic ordering constraint
            ``a <=lex b`` over two vectors of literals. The first position
            is the most significant one, and false is smaller than true.
            The vectors may have different lengths: if one of them is a
            prefix of the other, the shorter one is smaller, as with Python
            tuples.

            Helper variables are numbered above ``top_id``, or taken from
            ``vpool``. The two cannot be given at the same time.

            :param a: the left-hand side vector of literals.
            :param b: the right-hand side vector of literals.
            :param top_id: the largest variable identifier used so far.
            :param vpool: pool of variable identifiers to take the helper
                variables from.

            :type a: list(int)
            :type b: list(int)
            :type top_id: int or None
            :type vpool: :class:`pysat.formula.IDPool` or None

            :raises ValueError: if a vector contains something other than a
                non-zero integer.

            :rtype: :class:`pysat.formula.CNF`

            Example:

            .. code-block:: python

                >>> from pysat.vector import VecEnc
                >>> cnf = VecEnc.lex_leq([1, 2], [3, 4])
                >>> print(cnf.clauses)
                [[-1, 3], [-1, 5], [3, 5], [-5, -2, 4]]
                >>> print(cnf.nv)
                5
        """

        return cls._encode(a, b, False, top_id, vpool)

    @classmethod
    def lex_lt(cls, a, b, top_id=None, vpool=None):
        return cls._encode(a, b, True, top_id, vpool)

    @classmethod
    def _encode(cls, a, b, strict, top_id, vpool):
        assert not top_id or not vpool, (
            'Use either a top id or a pool of variables but not both.')

        for lit in a + b:
            if not isinstance(lit, int) or lit == 0:
                raise ValueError('Not a literal: {0!r}'.format(lit))

        if top_id is None:
            top_id = 0
        top_id = max([top_id] + [abs(lit) for lit in a + b])

        # positions are compared up to the end of the shorter vector
        size = min(len(a), len(b))

        # if a is longer and starts with b, then a is larger
        # so a <=lex b needs the common part of a to be strictly smaller
        if len(a) != len(b):
            strict = len(a) > len(b)

        if vpool:
            vpool.top = max(top_id, vpool.top)
            e = [vpool.id() for _ in range(size - 1)]
            nv = vpool.top
        else:
            e = [i for i in range(top_id + 1, top_id + size)]
            nv = max([top_id] + e)

        clauses = cls._build_clauses(a[:size], b[:size], e, strict)

        cnf = CNF(from_clauses=clauses)
        cnf.nv = nv  # the largest variable used so far

        return cnf

    @classmethod
    def _build_clauses(cls, a, b, e, strict=False):
        """
            Return the clauses of ``a <=lex b``, or of ``a <lex b`` if
            ``strict`` is true, for two vectors of the same length.
            ``e[i]`` is a helper variable meaning "a and b are equal on all
            positions up to ``i``".
        """

        if not a:
            # empty vectors are equal: a non-strict comparison always holds,
            # and a strict one never does (an empty clause is unsatisfiable)
            return [[]] if strict else []

        clauses = []
        last = len(a) - 1

        for i in range(len(a)):
            # clauses only apply if all previous positions are equal
            prefix = [-e[i - 1]] if i > 0 else []

            if i < last:
                clauses += [prefix + [-a[i], b[i]],
                            prefix + [-a[i], e[i]],
                            prefix + [b[i], e[i]]]
            elif strict:
                # a[i] must be false and b[i] must be true
                clauses += [prefix + [-a[i]],
                            prefix + [b[i]]]
            else:
                clauses.append(prefix + [-a[i], b[i]])

        return clauses


if __name__ == '__main__':
    a = [-1, 2, 3, 4]
    b = [5, 6, 7, 8]
    e = [9, 10, 11]
    res = VecEnc.lex_leq(a, b)
    for x in res:
        print(x)
