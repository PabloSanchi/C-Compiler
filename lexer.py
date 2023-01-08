import os, re
from sly import Lexer, Parser

class CalcLexer(Lexer):
    tokens = {RETURN, STRING, PRINTF, SCANF, VOID, INT, ID, NUM, EQ, LEQ, GEQ, NEQ, OR, AND, IF, WHILE, ELSE}
    literals = {'&', '=', '!', '<', '>', '(', ')', ';', '+', '-', '*', '/', ',', '{', '}', '[', ']'}
    
    ignore = ' \t'
    # ignore C comments (/**/)
    ignore_comment = r'(/\*(.|\n)*?\*/)|(//.*)'
    

    STRING = r'".*"'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['int'] = INT
    ID['void'] = VOID
    ID['printf'] = PRINTF 
    ID['scanf'] = SCANF
    ID['return'] = RETURN
    ID['if'] = IF
    ID['else'] = ELSE
    ID['while'] = WHILE

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
