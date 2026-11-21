from pysat.formula import CNF


class VecEnc:

    @classmethod
    def lex_leq(cls, l): # assuming a and b have the same size
        res = []
        for i in range(l):
            # a[i] b[i]
            clause = [[f"-a[{i}]", f"b[{i}]"],
                    [f"-a[{i}]", f"e[{i}]"],
                    [f" b[{i}]", f"e[{i}]"]] if (i != l - 1) else [[f"-a[{i}]", f"b[{i}]"]]

            if i > 0:
                for cl in clause:
                    cl.insert(0, f"-e[{i-1}]")
            
            res += clause

        return res

if __name__ == '__main__':
    res = VecEnc.lex_leq(5)
    for x in res:
        print(x)

