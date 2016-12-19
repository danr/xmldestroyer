
import xmldestroyer as xd
import sys
from collections import Counter
import six

def pos_freq(infile):
    def w(s, d, xs, ps): return Counter({d['pos']:1})
    def add(tag, s, d, xs, ps): return sum(xs, Counter())
    return next(xd.iterator(infile, depth=0, default_action=add, w=w))

if __name__ == '__main__':
    print('\n'.join(pos + ' ' + str(count)
                    for pos, count in pos_freq(sys.argv[1]).most_common()))

