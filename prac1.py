from sly import Lexer, Parser

class CalcLexer(Lexer):
    tokens = {INT,ID, NUM, EQ, LEQ, GEQ, NEQ, OR, AND}
    literals = {'=', '!', '<', '>', '(', ')', ';', '+', '-', '*', '/'}
    
    ignore = ' \t'
    ignore_newline = r'\n+'

    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['int'] = INT

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


'''
definicion -> linea ; definicion
          | epsilon

linea -> ID '=' exprOR {map[ID.lexval] = exprOR.s}


exprOR -> exprAND {exprORP.h = exprAND.s} exprORP {exprOR.s = exprORP.s}
exprORP -> OR exprAND {exprORP.h = exprOR.h || exprAND.s } exprORP {exprOR.s = exprORP.s}
      | epsilon {exprORP.s = exprORP.s}}
      
exprAND -> exprNOT exprANDP
exprANDP -> AND exprNOT exprANDP
      | epsilon
      
      
exprNOT -> NOT exprNOT
     | '(' expr ')'
     | comp
 
    
comp -> sum compP
compP -> '==' sum
      | '!=' sum 
      | '<=' sum
      | '>=' sum
      | '<' sum
      | '>' sum
      | epsilon
      
sum -> sum '+' prod
sum -> sum '-' prod
sum -> prod

prod -> prod '*' fact
prod -> prod '/' fact
prod -> fact

fact -> ID
     | NUM
     | '(' sum ')'
'''

class CalcParser(Parser):
    tokens = CalcLexer.tokens
    
    def __init__(self, p):
        self.map = {}
    
    @_('line ";" definition')
    def definition(self, p):
        pass

    @_('')
    def definition(self, p):
        pass
    
    @_('ID "=" exprOR')
    def exprOR(self, p):
        self.map[p.ID] = p.exprOR
        
    @_('')
    def 