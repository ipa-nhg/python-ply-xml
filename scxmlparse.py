#!/usr/bin/env python

import sys
from UserString import UserString

from ply import lex, yacc


_VERSION = '1.0'

import scxmllex

################################
# PARSER

tag_stack = []

# Grammer

# ROOT ELEMENT = SCXML
def p_root_element(p):
    '''root : element
            | element PCDATA
    '''
    _parser_trace(p)

    p[0] = p[1]

# not needed for scxml
def p_root_pcdata_element(p):
    '''root : PCDATA element
            | PCDATA element PCDATA
    '''
    _parser_trace(p)

    p[0] = p[2]


# tag 
# <children> OR <children/>
def p_element(p):
    '''element : opentag children closetag
               | lonetag
    '''
    _parser_trace(p)

    if len(p) == 4:
        p[1].children = p[2]

    p[0] = p[1]

# <name atrr="">
def p_opentag(p):
    '''opentag : OPENTAGOPEN TAGATTRNAME attributes TAGCLOSE
    '''
    _parser_trace(p)

    tag_stack.append(p[2])
    p[0] = DOM.Element(p[2], p[3])

# </name>
def p_closetag(p):
    '''closetag : CLOSETAGOPEN TAGATTRNAME TAGCLOSE
    '''
    _parser_trace(p)

    n = tag_stack.pop()
    if p[2] != n:
        raise ParserError('Close tag name ("%s") does not match the corresponding open tag ("%s").' % (p[2], n))
# <name atrr="" />
def p_lonetag(p):
    '''lonetag : OPENTAGOPEN TAGATTRNAME attributes LONETAGCLOSE
    '''
    _parser_trace(p)

    p[0] = DOM.Element(p[2], p[3])





# attr
def p_attributes(p):
    '''attributes : attribute attributes
                  | empty
    '''
    _parser_trace(p)

    if len(p) == 3:
        if p[2]:
            p[1].update(p[2])
            p[0] = p[1]
        else:
            p[0] = p[1]
    else:
        p[0] = {}

def p_attribute(p):
    '''attribute : TAGATTRNAME ATTRASSIGN attrvalue
    '''
    _parser_trace(p)

    p[0] = {p[1]: p[3]}

def p_attrvalue(p):
    '''attrvalue : ATTRVALUE1OPEN ATTRVALUE1STRING ATTRVALUE1CLOSE
                 | ATTRVALUE2OPEN ATTRVALUE2STRING ATTRVALUE2CLOSE
    '''
    _parser_trace(p)

    p[0] = _xml_unescape(p[2])

# child
def p_children(p):
    '''children : child children
                | empty
    '''
    _parser_trace(p)

    if len(p) > 2:
        if p[2]:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]
    else:
        p[0] = []

def p_child_element(p):
    '''child : element'''
    _parser_trace(p)

    p[0] = p[1]

def p_child_pcdata(p):
    '''child : PCDATA'''
    _parser_trace(p)

    p[0] = DOM.Pcdata(p[1])

# empty
def p_empty(p):
    '''empty :'''
    pass



# Error rule for syntax errors
class ParserError(Exception):
    pass

def p_error(p):
    raise ParserError("Parse error: %s" % (p,))
    pass

# Customization
def _parser_trace(x):
    _debug_print_('PARSER', '[%-16s] %s' % (sys._getframe(1).f_code.co_name, x))

def _yacc_production__str(p):
    #return "YaccProduction(%s, %s)" % (str(p.slice), str(p.stack))
    return "YaccP%s" % (str([i.value for i in p.slice]))
yacc.YaccProduction.__str__ = _yacc_production__str


################################
# DOM

class DOM:
    class Element:
        # Document object model
        #
        # Parser returns the root element of the XML document

        def __init__(self, name, attributes={}, children=[]):
            self.name = name
            self.attributes = attributes
            self.children = children

        def __str__(self):
            if self.name == 'scxml':
              print "root element scxml" 
              print self.name

            attributes_str = ''
            for attr in self.attributes:
                attributes_str += ' %s="%s"' % (attr, _xml_escape(self.attributes[attr]))

            #print attributes_str
            children_str = ''
            for child in self.children:
                if isinstance(child, self.__class__):
                    children_str += str(child)
                else:
                    children_str += child

            return '<%s%s>%s</%s>'% (self.name, attributes_str, children_str, self.name)

        def __repr__(self):
            return str(self)

    class Pcdata(UserString):
        pass


################################
# ESCAPE

_xml_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def _xml_escape(text):
    L=[]
    for c in text:
        L.append(_xml_escape_table.get(c,c))
    return "".join(L)

def _xml_unescape(s):
    rules = _xml_escape_table.items()
    rules.reverse()

    for x, y in rules:
        s = s.replace(y, x)

    return s

################################
# INTERFACE

def xml_parse(data):

    _debug_header('INPUT')
    _debug_print_('INPUT', data)
    _debug_footer('INPUT')

    # Tokenizer
    xml_lexer = scxmllex.XmlLexer()
    xml_lexer.build()

    _debug_header('LEXER')
    xml_lexer.test(data)
    _debug_footer('LEXER')

    # Parser
    global tokens
    tokens = scxmllex.XmlLexer.tokens

    yacc.yacc(method="SLR")

    _debug_header('PARSER')
    root = yacc.parse(data, lexer=xml_lexer.lexer, debug=False)
    _debug_footer('PARSER')

    _debug_header('OUTPUT')
    _debug_print_('OUTPUT', root)
    _debug_footer('OUTPUT')

    return root

################################
# DEBUG

_DEBUG = {
    'INPUT': False,
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

