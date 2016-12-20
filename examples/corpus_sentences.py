# -*- coding: utf-8 -*-
import sys
import xmldestroyer as xd

def sentences(infile, outfile):
    def w(text):
        return text

    def sentence(children):
        return ' '.join(children)

    def text(children, title, url):
        return title + ' ' + url + '\n' + '\n'.join(children) + '\n\n'

    xd.xd(infile, outfile, w=w, sentence=sentence, text=text)


if __name__ == '__main__':
    sentences(*sys.argv[1:])

