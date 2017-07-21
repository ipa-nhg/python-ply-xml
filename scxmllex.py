#!/usr/bin/env python

import sys
from UserString import UserString

from ply import lex
import scxmlparse

################################
# LEXER


class XmlLexer:
    '''The SCXML lexer'''

    # states:
    #   tag:        The document tag context
    #   attrvalue1: Single-quoted tag attribute value
    #   attrvalue2: Double-quoted tag attribute value

    states = (
        ('tag', 'exclusive'),
        ('attrvalue1', 'exclusive'),
        ('attrvalue2', 'exclusive'),
        ('state', 'exclusive'),
        ('scxml', 'exclusive')
    )

##########################################################
#################SCXML specific ##########################
##########################################################

    keywords= ( 'FINAL',  'INITIAL',  'LOG', 'ONENTRY', 'ONEXIT', 'PARALLEL',  'SCXML', 'STATE', 'TRANSITION') # 'ASSIGN', 'CANCEL', 'CONTENT', 'DATA', 'DATAMODEL', 'DONEDATA', 'ELSE', 'ELSEIF', 'FINALIZE', 'FOREACH', 'HISTORY', 'IF', 'INVOKE','PARAM', 'RAISE', 'SCRIPT', 'SEND', 'VALIDATE'

##########################################################
##########################################################

    tokens = keywords + (
        # state: INITIAL
        'PCDATA',
        'OPENTAGOPEN',
        'CLOSETAGOPEN',
        # state: tag
        'TAGATTRNAME',
        'TAGCLOSE',
        'LONETAGCLOSE',
        'ATTRASSIGN',
        # state: attrvalue1
        'ATTRVALUE1OPEN',
        'ATTRVALUE1STRING',
        'ATTRVALUE1CLOSE',
        # state: attrvalue2
        'ATTRVALUE2OPEN',
        'ATTRVALUE2STRING',
        'ATTRVALUE2CLOSE',
    )


    # Complex patterns
    re_digit       = r'([0-9])'
    re_nondigit    = r'([_A-Za-z])'
    re_identifier  = r'(' + re_nondigit + r'(' + re_digit + r'|' + re_nondigit + r')*)'


    # ANY
    def t_ANY_error(self, t):
        raise SyntaxError("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
        pass

    # INITIAL
    t_ignore  = ''

    def t_CLOSETAGOPEN(self, t):
        r'</'
        t.lexer.push_state('tag')
        return t

    def t_OPENTAGOPEN(self, t):
        r'<'
        t.lexer.push_state('tag')
        return t

    def t_PCDATA(self, t):
        '[^<]+'
        return t


    # tag: name

    t_tag_ignore  = ' \t'

    def t_tag_TAGATTRNAME(self, t):
        return t
    t_tag_TAGATTRNAME.__doc__ = re_identifier

    def t_tag_TAGCLOSE(self, t):
        r'>'
        t.lexer.pop_state()
        return t

    def t_tag_LONETAGCLOSE(self, t):
        r'/>'
        t.lexer.pop_state()
        return t


    # tag: attr

    t_tag_ATTRASSIGN    = r'='

    def t_tag_ATTRVALUE1OPEN(self, t):
        r'\''
        t.lexer.push_state('attrvalue1')
        return t

    def t_tag_ATTRVALUE2OPEN(self, t):
        r'"'
        t.lexer.push_state('attrvalue2')
        return t


    # attrvalue1

    def t_attrvalue1_ATTRVALUE1STRING(self, t):
        r'[^\']+'
        t.value = unicode(t.value)
        return t

    def t_attrvalue1_ATTRVALUE1CLOSE(self, t):
        r'\''
        t.lexer.pop_state()
        return t

    t_attrvalue1_ignore  = ''


    # attrvalue2

    def t_attrvalue2_ATTRVALUE2STRING(self, t):
        r'[^"]+'
        t.value = unicode(t.value)
        return t

    def t_attrvalue2_ATTRVALUE2CLOSE(self, t):
        r'"'
        t.lexer.pop_state()
        return t

    t_attrvalue2_ignore  = ''

##########################################################
#################SCXML specific ##########################
##########################################################

    # ROOT - SCXML
    def t_SCXML(self, t):
        r'<scxml'
        return t

    # CHILDREN OF ROOT: state, parallel, final, datamodel, script
    def t_STATE(self, t):
        r'<state'
        t.lexer.push_state('state')
        return t

###########################################################
##########################################################


    # misc

    literals = '$%^'

    def t_ANY_newline(self, t):
        r'\n'
        t.lexer.lineno += len(t.value)


    # Build the lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(object=self, **kwargs)

    # Test it output
    def test(self, data):
        self.lexer.input(data)

        while 1:
            tok = self.lexer.token()
            if not tok: break
            self._debug_print_('LEXER', '[%-12s] %s' % (self.lexer.lexstate, tok))








################################
# DEBUG

    _DEBUG = {
        'INPUT': False,
        'LEXER': False,
        'PARSER': False,
        'OUTPUT': False,
    }

    def _debug_print_(self, part, s):
        if self._DEBUG[part]:
            print s


# Customization
class SyntaxError(Exception):
    pass
