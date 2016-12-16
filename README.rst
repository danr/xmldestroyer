xmldestroyer
============

This library does a bottom-up transformation of XML documents, extracting the
parts that are relevant for the task at hand, and either returning it as a
python generator, or serializing it to disk as XML (again!), JSON or text.

One design goal is to be able to process gigabyte-sized documents with constant
memory footprint.

Inspired by the Haskell libraries
`Scrap Your Boilerplate <https://hackage.haskell.org/package/syb>`__,
`uniplate <https://hackage.haskell.org/package/uniplate>`__ and
`geniplate <https://hackage.haskell.org/package/geniplate-mirror>`__.

Example, get the texts from all ``<p>`` tags in a document:

::

    from xmldestroyer import xd
    import sys

    def p(text, _attrs, _children, _parents):
        return text

    infile, outfile = sys.args

    xd(infile, outfile, p=p)

This outputs a text file with the text from all ``<p>`` tags, one per line.

Works with python 2.7, 3.3, 3.4 and 3.5.
