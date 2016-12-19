import sys
import xmldestroyer as xd
from collections import Counter

def word_freq(infile):
    def w(text, attrib, children, trail):
        return Counter({text:1})

    def add(tag, text, attrib, children, trail):
        return sum(children, Counter())

    return next(xd.iterator(infile, depth=0,
                            default_action=add, w=w))

if __name__ == '__main__':
    table = word_freq(sys.argv[1]).most_common(100)
    print('\n'.join(pos + ' ' + str(count)
                    for pos, count in table))

