% xmldestroyer Workshop
% Dan Rosén

# Example xml
\inputminted{xml}{wiki_small.xml}

#
\inputminted[firstline=5,lastline=12]{xml}{wiki_small.xml}
\begin{overlayarea}{\textwidth}{4cm}
\only<+>{\inputminted{python}{desc1}}
\only<+>{\inputminted{python}{desc2}}
\only<+>{\inputminted{python}{desc3}}
\only<+>{\inputminted{python}{desc4}}
\only<+>{\inputminted{python}{desc5}}
\only<+>{\inputminted{python}{desc6}}
\only<+>{\inputminted{python}{desc7}}
\only<+>{\inputminted{python}{desc8}}
\end{overlayarea}

#
\inputminted[firstline=2,lastline=6]{xml}{wiki_small.xml}
\begin{overlayarea}{\textwidth}{8cm}
\only<+>{\inputminted{python}{desc8}}
\only<+>{\inputminted{python}{desc9}}
\only<+>{\inputminted{python}{desc10}}
\only<+>{\inputminted{python}{desc11}}
\end{overlayarea}

# Extracting the text using `xmldestroyer`
\begin{overlayarea}{\textwidth}{8cm}
\only<+>{\inputminted[firstline=2,  lastline=4]{python}{../examples/corpus_sentences.py}}
\only<+>{\inputminted[firstline=2,  lastline=6]{python}{../examples/corpus_sentences.py}}
\only<+>{\inputminted[firstline=2,  lastline=9]{python}{../examples/corpus_sentences.py}}
\only<+>{\inputminted[firstline=2, lastline=13]{python}{../examples/corpus_sentences.py}}
\only<+>{\inputminted[firstline=2, lastline=15]{python}{../examples/corpus_sentences.py}}
\end{overlayarea}


# Making a word frequency table using `xmldestroyer`
\begin{overlayarea}{\textwidth}{8cm}
\only<+>{\inputminted[firstline=3,  lastline=5]{python}{../examples/corpus_word_freq.py}}
\only<+>{\inputminted[firstline=3,  lastline=7]{python}{../examples/corpus_word_freq.py}}
\only<+>{\inputminted[firstline=3,  lastline=10]{python}{../examples/corpus_word_freq.py}}
\only<+>{\inputminted[firstline=3, lastline=12]{python}{../examples/corpus_word_freq.py}}
\only<+>{\inputminted[firstline=3, lastline=18]{python}{../examples/corpus_word_freq.py}}
\end{overlayarea}


# Try it yourself!

    pip install xmldestroyer

Exercises at:

    http://demo.spraakdata.gu.se/dan/xmldestroyer

