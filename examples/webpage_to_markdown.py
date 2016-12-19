
import xmldestroyer as xd
import sys

def remove_adjacent_space(s):
    return ' '.join(s.split())

def main(infile, outfile):
    def p(text, tail, attrib, children, trail):
        return remove_adjacent_space(text + ' '.join(children)) + '\n'

    def b(text, tail, attrib, children, trail):
        return '**' + text + ' '.join(children) + '**' + tail

    def i(text, tail, attrib, children, trail):
        return '_' + text + ' '.join(children) + '_' + tail

    def h1(text, tail, attrib, children, trail):
        return '# ' + text + ' '.join(children) + '\n'

    def h2(text, tail, attrib, children, trail):
        return '# ' + text + ' '.join(children) + '\n'

    def a(text, tail, attrib, children, trail):
        return '[' + text + ' '.join(children) + '](' + attrib['href'] + ')' + tail

    xd.xd(infile, outfile, output_format='txt', tails=True,
          p=p, b=b, i=i, h1=h1, h2=h2, a=a)

if __name__ == '__main__':
    main(*sys.argv[1:])
