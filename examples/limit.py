
import xmldestroyer as xd
import sys

def identity(infile, outfile, limit=None, depth=1, xml_root='root'):
    def default_action(tag, text, tail, attrs, children, _parents):
        return xd.TagWithTail(tag, text, tail, *children, **attrs)
    depth=int(depth)
    xd.xd(tails=True, **locals())

if __name__ == '__main__':
    identity(*sys.argv[1:])

