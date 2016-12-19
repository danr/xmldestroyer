# -*- coding: utf-8 -*-

import xmldestroyer as xd
import xml.etree.cElementTree as ET
import os
import six
import codecs
import json
import xmltodict
from collections import OrderedDict, defaultdict

from nose.tools import eq_, with_setup


def po_str_iter(actions, expected):
    out = '\n'.join(xd.iterator('test_data/po.xml', actions)) + '\n'
    eq_(out, expected)



@with_setup(None, lambda: os.remove('test_data/po_tmp.txt'))
def po_str_file(actions, expected):
    xd.xd('test_data/po.xml', 'test_data/po_tmp.txt', actions)
    with codecs.open('test_data/po_tmp.txt', 'r', encoding='utf-8') as f:
        eq_(f.read(), expected)


def po_str(actions, expected):
    yield po_str_iter, actions, expected
    yield po_str_file, actions, expected


def test_po_names():
    def name(text, attrs, children, parents):
        return text
    for u in po_str(dict(name=name), "Alice Smith\nRobert Smith\n"):
        yield u


def test_po_partNum():
    def item(text, attrs, children, parents):
        return attrs['partNum']
    for u in po_str(dict(item=item), "872-AA\n926-AA\n"):
        yield u



def test_po_partNum_productName():
    def item(text, attrs, children, parents):
        return children[0] + ',' + attrs['partNum']

    def productName(text, attrs, children, parents):
        return text

    for u in po_str(dict(item=item, productName=productName),
                    "Lawnmower,872-AA\nBaby Monitor,926-AA\n"):
        yield u


def __pretty_xmlfile(filename):
    return __pretty_xml(ET.parse(filename).getroot())


def __pretty_xml(node):
    return ET.tostring(node)


def test_identity():
    def default_action(tag, text, tail, attrs, children, _parents):
        return xd.TagWithTail(tag, text, tail, *children, **attrs)

    original = __pretty_xmlfile('test_data/po.xml')
    iterator = xd.iterator('test_data/po.xml', tails=True, depth=0,
                           default_action=default_action)
    roundtrip = __pretty_xml(next(iterator))
    eq_(roundtrip, original)


@with_setup(None, lambda: os.remove('test_data/po_tmp.xml'))
def test_identity_file():
    def default_action(tag, text, tail, attrs, children, _parents):
        return xd.TagWithTail(tag, text, tail, *children, **attrs)

    original = __pretty_xmlfile('test_data/po.xml')
    xd.xd('test_data/po.xml', 'test_data/po_tmp.xml',
          tails=True, depth=0, outputs='one',
          default_action=default_action)
    roundtrip = __pretty_xmlfile('test_data/po_tmp.xml')
    eq_(roundtrip, original)


@with_setup(None, lambda: os.remove('test_data/tmp.txt'))
def test_abc_unicode_text():
    def abc(text, attrs, children, parents):
        return text

    xd.xd('test_data/abc.xml', 'test_data/tmp.txt', abc=abc, depth=0)

    with codecs.open('test_data/tmp.txt', 'r', encoding='utf-8') as f:
        eq_(u"åäö\n", f.read())


@with_setup(None, lambda: os.remove('test_data/tmp.xml'))
def test_abc_unicode_xml():
    def abc(text, attrs, children, parents):
        return xd.Tag('abc', text)

    xd.xd(
        'test_data/abc.xml',
        'test_data/tmp.xml',
        outputs='one',
        abc=abc,
        depth=0)

    original = __pretty_xmlfile('test_data/abc.xml')
    roundtrip = __pretty_xmlfile('test_data/tmp.xml')

    eq_(original, roundtrip)


@with_setup(None, lambda: os.remove('test_data/tmp.json'))
def test_abc_unicode_json():
    def abc(text, attrs, children, parents):
        return text

    xd.xd('test_data/abc.xml', 'test_data/tmp.json', outputs='one', abc=abc, depth=0)

    with codecs.open('test_data/tmp.json', 'r', encoding='utf-8') as f:
        eq_(u'åäö', json.load(f))


def my_xml_to_dict(xmlfile):
    """
    An attempt at reimplementing xmltodict.
    But it's not very well specified.
    """
    def default_action(tag, text, attrs, children, _parents):
        if not attrs and not children:
            d = OrderedDict()
            d[tag]=text
            return d
        else:
            content = OrderedDict()
            for k, v in six.iteritems(attrs):
                content['@'+k] = v
            if text and not text.isspace():
                content['#text'] = text
            count = defaultdict(int)
            for c in children:
                for k,v in six.iteritems(c):
                    count[k]+=1
            for c in children:
                for k,v in six.iteritems(c):
                    if count[k] > 1:
                        content[k] = content.get(k, []) + [v]
                    else:
                        content[k] = v
            return {tag:content}
    return xd.iterator(xmlfile, default_action=default_action, depth=0)



def test_xml_to_dict():
    out = next(my_xml_to_dict('test_data/po.xml'))
    with codecs.open('test_data/po.xml', 'r', encoding='utf-8') as f:
        eq_(out, xmltodict.parse(f.read()))
