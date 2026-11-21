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
        
        res = []
        l = len(a)
        e = [i for i in range(top_id + 1, top_id + l)] # store equality

        for i in range(l):
            # a[i] b[i]
            clause = [[-a[i], b[i]],
                    [-a[i], e[i]],
                    [ b[i], e[i]]] if (i != l - 1) else [[-a[i], b[i]]]

            if i > 0:
                for cl in clause:
                    cl.insert(0, -e[i-1])
            
            res += clause

        return res

if __name__ == '__main__':
    a = [-1, 2, 3, 4]
    b = [5, 6, 7, 8]
    e = [9, 10, 11]
    res = VecEnc.lex_leq(a, b)
    for x in res:
        print(x)

