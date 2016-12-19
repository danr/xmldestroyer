
import corpus_pos_freq
import corpus_word_freq
import corpus_sentences

import os
import codecs
from nose.tools import eq_, with_setup

CORPUS='examples/corpus_example.xml'

def test_pos_freq():
    table = corpus_pos_freq.pos_freq(CORPUS).most_common(2)
    eq_(table, [('NN',996),('PP',530)])

def test_word_freq():
    table = corpus_word_freq.word_freq(CORPUS).most_common(2)
    eq_(table, [('.',200),(',',185)])

def file_eq(file1, file2):
    with codecs.open(file1, 'r', encoding='utf-8') as f1:
        with codecs.open(file2, 'r', encoding='utf-8') as f2:
            eq_(f1.read(), f2.read())

SENTS_TMP='sents_tmp.txt'

@with_setup(None, lambda: os.remove(SENTS_TMP))
def test_sentences():
    corpus_sentences.sentences(CORPUS, SENTS_TMP)
    file_eq(SENTS_TMP, 'examples/corpus_sentences.txt')

