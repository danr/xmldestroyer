import sys
import xmldestroyer as xd

def sentences(infile, outfile):
    def w(text, attrib, children, trail):
        return text

    def sentence(text, attrib, children, trail):
        return ' '.join(children)

    def text(text, attrib, children, trail):
        header = ' '.join(attrib[k] for k in ['title', 'url'])
        return header + '\n' + '\n'.join(children) + '\n\n'

    xd.xd(infile, outfile, w=w, sentence=sentence, text=text)


if __name__ == '__main__':
    sentences(*sys.argv[1:])

