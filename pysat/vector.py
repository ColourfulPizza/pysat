from pysat.formula import CNF


class VecEnc:

    @classmethod
    def lex_leq(cls, a, b, top_id=None, vpool=None): # assuming a and b have the same size
        assert not top_id or not vpool, (
            'Use either a top id or a pool of variables but not both.')
        
        if not top_id:
            top_id = max(abs(l) for l in a + b)
        if vpool:
            top_id = max(top_id, vpool.top)
        
        l = len(a)
        e = [i for i in range(top_id + 1, top_id + l)] # store equality

        cnf = CNF(from_clauses=cls._build_clauses(a, b, e))

        # the largest variable used so far, including the helper variables,
        # so that callers can number their next variables above it
        cnf.nv = top_id + len(e)

        return cnf

    @classmethod
    def _build_clauses(cls, a, b, e):
        """
            Return the clauses of ``a <=lex b``. ``e[i]`` is a helper
            variable meaning "a and b are equal on all positions up to
            ``i``".
        """

        clauses = []
        last = len(a) - 1

        for i in range(len(a)):
            # clauses only apply if all previous positions are equal
            prefix = [-e[i - 1]] if i > 0 else []

            if i < last:
                clauses += [prefix + [-a[i], b[i]],
                            prefix + [-a[i], e[i]],
                            prefix + [b[i], e[i]]]
            else:
                # the strict version will differ only here
                clauses.append(prefix + [-a[i], b[i]])

        return clauses

if __name__ == '__main__':
    a = [-1, 2, 3, 4]
    b = [5, 6, 7, 8]
    e = [9, 10, 11]
    res = VecEnc.lex_leq(a, b)
    for x in res:
        print(x)

