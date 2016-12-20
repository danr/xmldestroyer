# -*- coding: utf-8 -*-
"""
`xmldestroyer`

Bottom-up transformation of XML into XML, JSON or text.
"""

import xml.etree.cElementTree as ET
import six
import bz2
import gzip
import itertools
import json
import inspect
from contextlib import contextmanager
from functools import wraps


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


class Element(object):

    """
    This object corresponds to a tag from an XML document.  The XML document's
    children cannot be accessed, but the processed children are available.
    It has the following attributes:

    - ``tag``: the tag name
    - ``text``: the text inside the tag
    - ``tail``: the text directly after the tag end until the next tag begins
    - ``attrib``: its attribute dictionary
    - ``children``: the _processed_ children (not the children in the XML.)
    - ``trail``: the trail of the node's ancestors, a list of Element objects,
       from youngest (most immediate) to oldest (the root).
       They have no children since they are not yet processed.
    - ``parent``: a convenience view: the immediate parent from the ``trail``
    - ``traildict``: another convenience: the ``trail`` list as a dict,
      keyed by tag names, duplicates removed (youngest survives).

    Further, the attributes of the tag are also attributes of this object as
    long as they do not collide with the attributes above.
    """

    def __init__(self, elem, trail):
        protected = set(('text', 'tail', 'children', '_finalize'))
        for k, v in six.iteritems(elem.attrib):
            if k not in protected:
                self.__dict__[k] = v
        parent = trail[0] if trail else None
        traildict = dict(((elem.tag, elem) for elem in trail[::-1]))
        self.__dict__.update(tag=elem.tag,
                             attrib=elem.attrib,
                             trail=trail,
                             parent=parent,
                             traildict=traildict)

    def _finalize(self, text, tail, children):
        self.__dict__.update(text=text or '',
                             tail=tail or '',
                             children=children or [])

    def __setattr__(self, *_):
        raise AttributeError("Immutable object")


def iterate(input,
            actions={},
            default_action=None,
            input_compression='ext',
            depth=1,
            parameter_puns=True,
            **more_actions):
    """
    Transforms an XML document bottom-up, returning an iterator of the results.

    Parameters
    ----------
    input : fileobject or filename
        A filename of an xml document or a file object.
        The file can be compressed, see 'input_compression'.
    actions : dictionary
        Actions to execute when processing a tag.  Keys are tag names:
        if a function for the current tag exists it is executed.

        If ``parameter_puns`` is ``False``, the function
        is passed one argument: a 'xmldestroyer.Element' object.
        If ``parameter_puns`` is ``True``, which is the default,
        the function's argument names are inspected and all attributes
        from 'xmldestroyer.Element' with these names are passed.

        The returned value from the actions is passed to nearest parent
        with an action function. If there is none, it is yielded.
        If the action returns a genererator or is a generator function,
        all generated elements are passed.

        Returned or yielded ``None`` are skipped.
    default_action : function
        If this function is given it is is executed at every tag not handled
        by other actions and is within the depth.
    input_compression : 'ext', 'bz2', 'gz' or 'none'
        Compression used on the input file. If `ext` then the file extension
        determines between `bz2` and `gz`.
    depth : int
        The xml nesting depth in the document to yield results from.
        No actions are executed before this depth.
    parameter_puns : boolean
        Default is True. See documentation for the 'actions' parameter.
    **more_actions : dictionary
        Works the same as the ``actions`` dictionary.
    """

    actions = dict(actions, **more_actions)
    if parameter_puns:
        actions = {k: __parameter_puns_decorator(v)
                   for k, v in six.iteritems(actions)}
        if default_action:
            default_action = __parameter_puns_decorator(default_action)

    def has_action(tag):
        return tag in actions or default_action

    stks = []
    trail = []
    with __compressed_open(input, 'r', input_compression) as f:
        context = iter(ET.iterparse(f, events=("start", "end")))
        for evt, elem in context:
            if evt == 'start':
                trail.append(Element(elem, trail[::-1]))
                if len(trail) > depth and has_action(elem.tag):
                    stks.append([])
            elif evt == 'end':
                element = trail.pop()
                if len(trail) >= depth and has_action(elem.tag):
                    element._finalize(elem.text, elem.tail, stks.pop())
                    res = actions.get(elem.tag, default_action)(element)
                    if not inspect.isgenerator(res):
                        res = (res,)
                    for x in res:
                        if x is not None:
                            if len(stks) > 0:
                                stks[-1].append(x)
                            else:
                                yield x
                elem.clear()


def write_iterator(iterator, output,
                   output_format='auto',
                   output_compression='ext',
                   many_outputs=True,
                   text_sep='\n',
                   text_end='\n',
                   json_indent=4,
                   xml_root='root'):
    """
    Writes an iterator as returned from `xmldestroyer.iterate` to disk.

    Parameters
    ----------
    iterator : iterator
        An iterator of strings, ElementTree nodes or JSON objects.
    output : filename
        File or file object to store the result.
    output_format : 'auto', 'text', 'xml', 'json'
        Output format to use.
        Determined by the type of the first element of the iterator if `auto`.
        This is the default.
    output_compression : 'ext', 'bz2', 'gz', 'none'
        Compression to use on the output.
        Determined by the filename extension of output if `ext`.
        This is the default.
    many_outputs : boolean
        For XML and JSON outputs only.
        By default this is true and has the following effects:
        - For XML output, an extra root tag wraps all output.
          The tag name is given by given by ``xml_root``.
        - For JSON output, an array wraps all output.
    text_sep : string
        For text output: separator between elements from the iterator.
    text_end : string
        For text output: written after all elements.
    json_indent : int
        For JSON output: indentation level.
        Set to None or non-positive for no pretty-printing.
    xml_root : string
        For XML output: The name of the root tag.
    """

    if output_format == 'auto':
        output_format, iterator = __output_format_from_iterator(iterator)

    if output_format not in ['text', 'xml', 'json']:
        raise ValueError("Invalid output format: " + output_format)

    if many_outputs and output_format == 'xml':
        header = '<?xml version="1.0" encoding="UTF-8"?>\n<' + xml_root + '>'
        footer = '</' + xml_root + '>\n'
    elif many_outputs and output_format == 'json':
        header = '['
        footer = '\n]'
    elif output_format == 'text':
        header = ''
        footer = text_end
    else:
        header = footer = ''

    header = __utf8(header)
    footer = __utf8(footer)
    text_sep = __utf8(text_sep)

    with __compressed_open(output, 'wb', output_compression) as of:

        of.write(header)

        for first, x in __tag_first(iterator):
            if output_format == 'text':
                if not first:
                    of.write(text_sep)
                of.write(__utf8(x))
            elif output_format == 'xml':
                t = ET.ElementTree(x)
                t.write(of, encoding='utf-8', xml_declaration=False)
                x.clear()
            elif output_format == 'json':
                if many_outputs and not first:
                    of.write(',\n')
                of.write(__utf8(json.dumps(x, indent=json_indent)))

        of.write(footer)


def xd(input, output, actions={}, limit=None, top_action=None, **args):
    """
    Transforms an XML document bottom-up and writes it to a file.
    Parameters are inherited from `xmldestroyer.iterate` and
    `xmldestroyer.write_iterator`.

    Parameters
    ----------
    limit : int
        If this limit is given then only so many elements are extracted from
        the iterator.
    top_action : function
        If this functions is given then it is executed on all elements
        of the iterator before they are written.
    """

    iterate_args = {}
    write_args = {}
    write_params = __args_of(write_iterator)

    for k, v in six.iteritems(args):
        if k in write_params:
            write_args[k] = v
        else:
            iterate_args[k] = v

    iterator = iterate(input, actions, **iterate_args)

    if limit is not None:
        iterator = itertools.islice(iterator, 0, limit)

    if top_action:
        iterator = map(top_action, iterator)

    write_iterator(iterator, output, **write_args)


def __parameters(fn):
    return fn.__doc__.split("Parameters")[1].split("----------")[1]


xd.__doc__ += __parameters(iterate) + __parameters(write_iterator)


# Utilities


def __compressed_open(filename, mode, compression='ext'):
    if hasattr(filename, 'read') or hasattr(filename, 'write'):
        @contextmanager
        def ignore_enter_and_exit(): yield filename
        return ignore_enter_and_exit()

    def match(ext):
        if compression == 'ext':
            return filename.endswith('.' + ext)
        else:
            return compression == ext
    if match('bz2'):
        return bz2.BZ2File(filename, mode)
    elif match('gz'):
        return gzip.GzipFile(filename, mode)
    else:
        return open(filename, mode)


def __output_format_from_iterator(iterator):
    first = next(iterator)
    if isinstance(first, six.string_types):
        fmt = 'text'
    elif type(first) == type(Tag('dummy', None)):
        # ET.Element in python2 does not support isinstance
        fmt = 'xml'
    else:
        fmt = 'json'
    return fmt, itertools.chain((first,), iterator)


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


def __args_of(f):
    return inspect.getargspec(f).args


def __parameter_puns_decorator(f):
    if not inspect.isfunction(f):
        raise TypeError('Not a function: ' + repr(f))
    params = __args_of(f)

    def arguments(elem):
        return (getattr(elem, x) for x in params)
    if inspect.isgeneratorfunction(f):
        @wraps(f)
        def wrap(elem):
            for x in f(*arguments(elem)):
                yield x
        return wrap
    else:
        @wraps(f)
        def wrap(elem):
            return f(*arguments(elem))
        return wrap
