
import xmldestroyer as xd
import sys
from collections import Counter
import six

def pos_freq(infile):
    def w(pos): return Counter({pos:1})
    def add(children): return sum(children, Counter())
    return next(xd.iterate(infile, depth=0, default_action=add, w=w))

if __name__ == '__main__':
    print('\n'.join(pos + ' ' + str(count)
                    for pos, count in pos_freq(sys.argv[1]).most_common()))

