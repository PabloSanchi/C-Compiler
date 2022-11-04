import os
from sly import Lexer, Parser

class CalcLexer(Lexer):
    tokens = {STRING, PRINTF, PERC_D, SCANF, VOID, INT, ID, NUM, EQ, LEQ, GEQ, NEQ, OR, AND}
    literals = {'=', '!', '<', '>', '(', ')', ';', '+', '-', '*', '/', ',', '{', '}'}
    
    ignore = ' \t'

    STRING = r'".*"'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['int'] = INT
    ID['void'] = VOID
    ID['printf'] = PRINTF 
    ID['%d'] = PERC_D 
    ID['scanf'] = SCANF
    
    EQ = r'=='
    LEQ = r'<='
    GEQ = r'>='
    NEQ = r'!='
    OR = r'\|\|'
    AND = r'&&'
    
    @_(r'\d+')
    def NUM(self, t):
        t.value = int(t.value)
        return t

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')
    
    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1
        contador = -1
