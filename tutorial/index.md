<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/8.4/styles/github.min.css">
<script src="https://code.jquery.com/jquery-2.1.3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/8.4/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/8.4/languages/python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/8.4/languages/xml.min.js"></script>

<style>body { padding: 20px; max-width: 600px; margin: auto; } pre { padding: 0 }</style>

<script>
$(function() {
    $("pre > code").each(function(i, block) {
        var codeClass = $(this).parent().attr("class");
        if (codeClass == null || codeClass === "") {
            $(this).addClass("hljs");
        } else {
            var map = {
                js: "javascript"
            };
            if (map[codeClass]) {
                codeClass = map[codeClass];
            }
            $(this).addClass(codeClass);
            hljs.highlightBlock(this);
        }
    });
});
</script>

# xmldestroyer exercises

Install it!

    pip install xmldestroyer

Access documentation in the python interpreter like so:

    import xmldestroyer
    help(xmldestroyer)

You can also look at the [tutorial slides](tutorial.pdf).

### Examples

Getting the texts out of [wiki_small.xml](wiki_small.xml):

```python
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

    # use xd to save results directly to a file
    xd.xd(infile, outfile, w=w, sentence=sentence, text=text)

if __name__ == '__main__':
    sentences(*sys.argv[1:])
```

Word frequencies out of [wiki_small.xml](wiki_small.xml):

```python
import sys
import xmldestroyer as xd
from collections import Counter

def word_freq(infile):
    def w(text, attrib, children, trail):
        return Counter({text:1})

    def add(tag, text, attrib, children, trail):
        return sum(children, Counter())

    # use iterator to get the iterator instead of saving to a file.
    # use depth to only yield at the root note (default is 1)
    # use next to get the first element from the iterator.
    # default_action gets the tag name as the first argument
    #   and is applied at all levels (within the depth)
    return next(xd.iterator(infile, depth=0,
                            default_action=add, w=w))

if __name__ == '__main__':
    table = word_freq(sys.argv[1]).most_common(100)
    print('\n'.join(pos + ' ' + str(count)
                    for pos, count in table))
```

### 1. Make a frequency table of the part-of-speech

Use the `attrib` dictionary to instead make a frequency table
of the part of speech.

If you want you can look at a bigger corpus:

    wget http://spraakbanken.gu.se/lb/resurser/meningsmangder/vivill.xml.bz2

Note that xmldestroyer handles input compressed using bz2 or gzip.
More corpora can be found at [https://spraakbanken.gu.se/eng/resources/corpus](https://spraakbanken.gu.se/eng/resources/corpus)

### 2. Make a simple word list from a lexicon

Look at [thesaurus_example.xml](thesaurus_example.xml). There are entries such as:

```{.xml}
      <Sense id="missbildad..1">
        <SenseRelation targets="abnorm..1">
          <feat att="label" val="syn" />
          <feat att="degree" val="64" />
          <feat att="source" val="fsl" />
        </SenseRelation>
```

Process the file and output a line such as

    missbildad abnorm

for this entry.

The entire thesaurus can be obtained like this:

    wget https://svn.spraakdata.gu.se/sb-arkiv/pub/lmf/swesaurus/swesaurus.xml

### 3. Expression calculator

Look at [expression_example.xml](expression_example.xml).
Replace all `num` nodes with their number,
the `add` nodes with the sum of their children's calculated
values. For `mul`, calculate the product.

### 4. Webpage to markdown

Look at [webpage_example.xml](webpage_example.xml).
Transform this to markdown.
We will need to look at the _tails_ of tags,
which is the text from the closing tag until the start
of the next tag. We do this by passing `tails=True` to
`xmldestroyer.iterator` or `xmldestroyer.xd`. Then
the action handlers get an additional argument after text
containing the tail text.

Here is something to get you started:

```python
import xmldestroyer as xd
import sys

def zap_adjacent_space(s):
    return ' '.join(s.split())

def main(infile, outfile):
    def p(text, tail, attrib, children, trail):
        return zap_adjacent_space(text + ' '.join(children)) + '\n'

    def b(text, tail, attrib, children, trail):
        return '**' + text + ' '.join(children) + '**' + tail

    xd.xd(infile, outfile, output_format='txt', tails=True,
          p=p, b=b)

if __name__ == '__main__':
    main(*sys.argv[1:])
```

### 5. Webpage tables to csv

Take some html table and transform it to csv.

### 6. XML to JSON

There are some libraries that try to transform
XML to JSON in a systematic way. Invent your own
way of representing the data in a HTML document and
save it as JSON.
