from pysat.formula import CNF


class VecEnc:

    @classmethod
    def lex_leq(cls, a, b, top_id=None, vpool=None): # assuming a and b have the same size
        assert not top_id or not vpool, (
            'Use either a top id or a pool of variables but not both.')
        
        top_id = max(abs(l) for l in a + b + [top_id if top_id != None else 0])
        l = len(a)

        if vpool:
            vpool.top = max(top_id, vpool.top)
            e = [vpool.id() for _ in range(l - 1)] 
        else:
            e = [i for i in range(top_id + 1, top_id + l)]

        cnf = CNF(from_clauses=cls._build_clauses(a, b, e))
        cnf.nv = max([top_id] + e) # the largest variable used so far

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
