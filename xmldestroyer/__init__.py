# -*- coding: utf-8 -*-
"""
`xmldestroyer`

Bottom-up transformation of XML into XML, JSON or text.
"""

import xml.etree.cElementTree as ET
import six
import bz2
import itertools
import json
import inspect


def Tag(tag, text, *children, **attribs):
    elem = ET.Element(tag, attribs)
    elem.text = text
    elem.extend(children)
    return elem


def TagWithTail(tag, text, tail, *children, **attribs):
    elem = ET.Element(tag, attribs)
    elem.text = text
    elem.tail = tail
    elem.extend(children)
    return elem


def iterator(infile,
             actions={},
             default_action=None,
             input_compression='ext',
             tails=False,
             depth=1,
             **more_actions):
    """
    Transforms an XML document bottom-up and returns an iterator of the results.

    Parameters
    ----------
    infile : filename
        The input filename.
    actions : dictionary
        Actions to execute when processing a tag.
        When encountering a tag, if a mapping with the
        same key as the tag name is found in this dictionary,
        it is executed. The function takes four arguments:
            ``text``, ``attrib``, ``children``, ``trail``
        where
            - ``text``: the tag's textual content,
            - ``attrib``: its attribute dictionary
            - ``children``: the _processed_ children (if any)
              note that is not the children in the XML document
            - ``trail``: a trail of the node's ancestors. this is a list
              of ``(tag_name, attrib)`` tuples, where ``tag_name`` is the
              name of the ancestor's tag and ``attrib`` its attribute dictionary.

        Exception: if ``tails`` = ``True``, another argument is provided after ``text``,
        namely ``tail`` which is the tail text content.
    default_action : function
        This function, if given, is executed at every tag which is not handled
        by other actions, and is within the depth. The signature of this function
        is the same as for actions, but with the exception that it gets a first
        argument which is the name of the tag.
    input_compression : 'ext', 'bz2', 'gz' or 'none'
        Compression used on the input file. If `ext` then the file extension
        determines between `bz2` and `gz`.
    tails : boolean
        If the action handlers are also passed the tail text contents.
        This is the text from the end of the tag to the start of the next tag.
    depth : int
        The xml nesting depth in the document to yield results from.
    **more_actions : dictionary
        Works the same as the ``actions`` dictionary.
    """

    actions = dict(actions, **more_actions)

    stks = []
    parents = []
    with __compressed_open(infile, 'r', input_compression) as f:
        context = iter(ET.iterparse(f, events=("start", "end")))
        for evt, elem in context:
            if evt == 'start':
                parents.append((elem.tag, elem))
                if len(parents) > depth and (elem.tag in actions or default_action):
                    stks.append([])
            elif evt == 'end':
                parents.pop()
                if len(parents) >= depth and (elem.tag in actions or default_action):
                    children = stks.pop()
                    k = actions.get(elem.tag, lambda *args: default_action(elem.tag, *args))
                    if tails:
                        res = k(elem.text, elem.tail, elem.attrib, children, dict(parents))
                    else:
                        res = k(elem.text, elem.attrib, children, dict(parents))
                    if not inspect.isgenerator(res):
                        res = (res,)
                    for x in res:
                        if x is not None:
                            if len(stks) > 0:
                                stks[-1].append(x)
                            else:
                                yield x
                elem.clear()


def write_iterator(iterator, outfile,
                   output_format='ext',
                   output_compression='ext',
                   limit=None,
                   top_action=None,
                   outputs='many',
                   text_sep='\n',
                   json_indent=4,
                   xml_root='root'):
    """
    Writes an iterator as returned from `xmldestroyer.iterator` to disk.

    Parameters
    ----------
    iterator : iterator
        An iterator that yields strings, ElementTree nodes or python
        objects that can be json-serialised.
    outfile : filename
        File to store the result.
    output_format : 'ext', 'auto', 'text', 'xml', 'json'
        Output format to use. When `ext` is given, it looks at the
        extension of the outfile (with `txt` for `text`).
        With `auto`, it looks at the type of the first element of the iterator.
    output_compression : 'ext', 'bz2', 'gz', 'none'
        Compression to use on the output. If `ext` is given it is determined
        by the filename.
    limit : int
        An optional limit for how many results from the iterator to write.
    top_action : function
        Function that is executed on all the elemnets from the iterator
        before they are written, if given.
    outputs : 'many', 'one'
        If this is set to 'many' (which is the default), the
        This affects the XML and JSON outputs.
        output is wrapped in a tag (given by ``xml_root``) for XML output,
        and is written as an array for JSON output.
    text_sep : string
        For text output: separator between elements from the iterator.
    json_indent : int
        For JSON output: indentation level. Set to None or non-positive for
        no pretty-printing.
    xml_root : string
        For XML output: The name of the root tag.
    """

    if output_format == 'text':
        output_format = 'txt'
    elif output_format == 'ext':
        output_format = __output_format_from_ext(outfile)
    elif output_format == 'auto':
        output_format, iterator = __output_format_from_iterator(iterator)

    if output_format not in ['txt', 'xml', 'json']:
        raise ValueError("Invalid output format: " + output_format)

    if outputs == 'many' and output_format == 'xml':
        header = '<?xml version="1.0" encoding="UTF-8"?>\n<' + xml_root + '>'
        footer = '</' + xml_root + '>\n'
    elif outputs == 'many' and output_format == 'json':
        header = '['
        footer = '\n]'
    else:
        header = footer = ''

    header = __utf8(header)
    footer = __utf8(footer)
    text_sep = __utf8(text_sep)

    if isinstance(limit, six.string_types) and str.isdigit(limit):
        limit = int(limit)

    with __compressed_open(outfile, 'wb', output_compression) as of:

        of.write(header)

        for first, x in __tag_first(itertools.islice(iterator, 0, limit)):
            if top_action:
                x = top_action(x)
            if output_format == 'txt':
                of.write(__utf8(x) + text_sep)
            elif output_format == 'xml':
                ET.ElementTree(x).write(of, encoding='utf-8', xml_declaration=False)
                x.clear()
            elif output_format == 'json':
                if outputs == 'many' and not first:
                    of.write(',\n')
                of.write(__utf8(json.dumps(x, indent=json_indent)))

        of.write(footer)


def xd(infile, outfile,
       actions={},
       default_action=None,
       output_format='ext',
       input_compression='ext',
       output_compression='ext',
       limit=None,
       top_action=None,
       tails=False,
       depth=1,
       outputs='many',
       text_sep='\n',
       json_indent=4,
       xml_root='root',
       **more_actions):
    """
    Transforms an XML document bottom-up and writes it to a file.
    Parameters are the same as for `xmldestroyer.iterator` and
    `xmldestroyer.write_iterator`.

    Parameters
    ----------
    """

    write_iterator(
        iterator(
            infile=infile,
            input_compression=input_compression,
            actions=actions,
            default_action=default_action,
            tails=tails,
            depth=depth,
            **more_actions),
        outfile=outfile,
        output_format=output_format,
        output_compression=output_compression,
        limit=limit,
        top_action=top_action,
        outputs=outputs,
        text_sep=text_sep,
        json_indent=4,
        xml_root=xml_root)


def __parameters(fn):
    return fn.__doc__.split("Parameters")[1].split("----------")[1]


xd.__doc__ += __parameters(iterator) + __parameters(write_iterator)


# Utilities


def __compressed_open(filename, mode, compression='ext'):
    def match(ext):
        if compression in ['ext']:
            return filename.endswith('.' + ext)
        else:
            return compression == ext
    if match('bz2'):
        return bz2.BZ2File(filename, mode)
    elif match('gz'):
        return gzip.GzipFile(filename, mode)
    else:
        return open(filename, mode)


def __output_format_from_ext(outfile):
    for ext in outfile.split('.')[1:][::-1]:
        for fmt in ['xml', 'json', 'txt']:
            if ext == fmt:
                return fmt
    raise ValueError("Cannot determine output format from the filename " + outfile)


def __output_format_from_iterator(iterator):
    first = next(iterator)
    if isinstance(first, six.string_types):
        fmt = 'txt'
    elif isinstance(first, ET.Element):
        fmt = 'xml'
    else:
        fmt = 'json'
    return fmt, itertools.chain([first], iterator)


def __tag_first(iterator):
    first = True
    for x in iterator:
        yield first, x
        first = False


def __utf8(s):
    if isinstance(s, six.string_types):
        return s.encode('utf-8')
    else:
        return s

