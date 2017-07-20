#!/usr/bin/env python

import sys
from UserString import UserString

from ply import lex, yacc


_VERSION = '1.0'

import scxmllex
import scxmlparse


def tree(node, level=0, init_prefix=''):
    'Returns a tree view of the XML data'

    prefix = '    '
    attr_prefix = '@'
    tag_postfix = ':\t'
    attr_postfix = ':\t'

    s_node = init_prefix + node.name + tag_postfix
    s_attributes = ''
    s_children = ''

    for attr in node.attributes:
        s_attributes += init_prefix + prefix + attr_prefix + attr + attr_postfix + node.attributes[attr] + '\n'

    if len(node.children) == 1 and not isinstance(node.children[0], scxmlparse.DOM.Element):
        s_node += node.children[0] + '\n'

    else:
        for child in node.children:
            if isinstance(child, scxmlparse.DOM.Element):
                s_children += tree(child, level+1, init_prefix + prefix)

        s_node += '\n'

    return s_node + s_attributes + s_children


################################
# DEBUG

_DEBUG = {
    'INPUT': True,
    'LEXER': False,
    'PARSER': False,
    'OUTPUT': False,
}

def _debug_header(part):
    if _DEBUG[part]:
        print '--------'
        print '%s:' % part

def _debug_footer(part):
    if _DEBUG[part]:
        pass

def _debug_print_(part, s):
    if _DEBUG[part]:
        print s


################################
# MAIN

def main():
    data = open(sys.argv[1]).read()
    root = scxmlparse.xml_parse(data)
    print tree(root)

if __name__ == '__main__':
    main()

