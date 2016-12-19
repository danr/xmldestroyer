
from functools import reduce
import xmldestroyer as xd
import sys

def calc(infile):
    def add(s, d, xs, ps): return sum(xs)
    def mul(s, d, xs, ps): return reduce(lambda x, y: x * y, xs, 1)
    def num(s, d, xs, ps): return int(s)
    return next(xd.iterator(infile, add=add, mul=mul, num=num))

if __name__ == '__main__':
    print(str(calc(sys.argv[1])))
