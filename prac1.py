import os
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

linea -> ID '=' expr {map[ID.lexval] = expr.s}

expr

expr -> exprNOT {exprORP.h = expr.s} exprP {expr.s = exprP.s}
exprP -> OR exrpNOT {exprP1.h = exprP.h || exrpNOT.s } exprP {exprP.s = exprP1.s}
exprP -> AND exrpNOT {exprP1.h = exprP.h && exprNOT.s} exprP {exprP.s = exprP1.s}
      | epsilon {exprP.s = exprP.h}
            
exprNOT -> NOT exprNOT {exprNOT.s = not exprNOT}
     | comp {exprNOT.s = comp.s}
 
    
comp -> sum {compP.h = sum.s} compP {comp.s == compP.s}
compP -> '==' sum {compP.s = compP.h == sum.s}
      | '!=' sum  {compP.s = compP.h != sum.s}
      | '<=' sum  {compP.s = compP.h <= sum.s}
      | '>=' sum  {compP.s = compP.h >= sum.s}
      | '<' sum   {compP.s = compP.h < sum.s}
      | '>' sum   {compP.s = compP.h > sum.s}
      | epsilon   {compP.s = compP.h}
      

sum -> prod {sumP.h = prod.s} sumP {sum.s = sumP.s}
sumP -> '+' prod {sumP1.h = sumP.h + prod.s} sumP {sumP.s = sumP1.s}
     |  '-' prod {sumP1.h = sumP.h - prod.s} sumP {sumP.s = sumP1.s}
     |  epsilon {sumP.s = sumP.h}

prod -> fact {prod.h = fact.s} prodP {prod.s = prodP.s}
prodP -> '*' fact {prodP1.h = prodP.h * fact.s} prodP {prodP.s = prodP1.s}
      |  '/' fact {prodP1.h = prodP.h / fact.s} prodP {prodP.s = prodP1.s}
      | epsilon {prodP.s = prodP.h}

fact -> ID {fact.s = ID.lexval}
     | NUM {fact.s = NUM.lexval}
     | '(' expr ')' {fact.s = expr.s}
'''

class CalcParser(Parser):
    tokens = CalcLexer.tokens
    debugfile = 'parser.txt'
    
    def __init__(self):
        self.map = {}
    
    def printMap(self):
        print(self.map)

    @_('line ";" definition', '')
    def definition(self, p):
        pass
    
    @_('ID "=" expr')
    def line(self, p):
        self.map[p.ID] = p.expr
        

    @_('exprNOT exprP')
    def expr(self, p):
        return p.exprP

    @_('OR exprNOT empty1 exprP')
    def exprP(self, p):
        return p.exprP

    @_('AND exprNOT empty2 exprP')
    def exprP(self, p):
        return p.exprP

    @_('')
    def empty1(self, p):
        return int(p[-3] or p[-1])

    @_('')
    def empty2(self, p):
        return int(p[-3] and p[-1])

    @_('')
    def exprP(self, p):
        return p[-1]
    

    @_('"!" exprNOT')
    def exprNOT(self, p):
        return int(not p.exprNOT)

    @_('comp')
    def exprNOT(self, p):
        return p.comp 
    
    @_('sum compP')
    def comp(self, p):
        return p.compP
    
    @_('EQ sum empty3')
    def compP(self, p):
        return int(p.empty3 == p.sum)

    @_('NEQ sum empty3')
    def compP(self, p):
        return int(p.empty3 != p.sum)
    
    @_('LEQ sum empty3')
    def compP(self, p):
        return int(p.empty3 <= p.sum)
    @_('GEQ sum empty3')
    def compP(self, p):
        return int(p.empty3 >= p.sum)
    
    @_('"<" sum empty3')
    def compP(self, p):
        return int(p.empty3 < p.sum)
    
    @_('">" sum empty3')
    def compP(self, p):
        return int(p.empty3 > p.sum)

    @_('')
    def compP(self, p):
        return p[-1]

    @_('')
    def empty3(self, p):
        return p[-3]

    @_('prod sumP')
    def sum(self, p):
        return p.sumP

    @_('"+" prod empty4 sumP')
    def sumP(self, p):
        return p.sumP
        
    @_('"-" prod empty5 sumP')
    def sumP(self, p):
        return p.sumP

    @_('')
    def sumP(self, p):
        return p[-1]

    @_('')
    def empty4(self, p):
        return p[-3] + p[-1]
    
    @_('')
    def empty5(self, p):
        return p[-3] - p[-1]
    
    @_('fact prodP')
    def prod(self, p):
        return p.prodP

    @_('"*" fact empty6 prodP')
    def prodP(self, p):
        return p.prodP

    @_('"/" fact empty7 prodP')
    def prodP(self, p):
        return p.prodP

    @_('')
    def prodP(self, p):
        return p[-1]
        
    @_('')    
    def empty6(self, p):
        return p[-3] * p[-1]

    @_('')    
    def empty7(self, p):
        return p[-3] // p[-1]

    @_('NUM')
    def fact(self, p):
        return p.NUM

    @_('ID')
    def fact(self, p):
        return self.map[p.ID]

    @_('"-" fact')
    def fact(self, p):
        return -1 * p.fact
       
    @_('"(" expr ")"')
    def fact(self, p):
        return p.expr


# 2 * (2 / (2))

if __name__ == '__main__':
    lexer = CalcLexer()
    parser = CalcParser()

    while True:
        try:
            text = input('> ')
            if text == 'clear':
                os.system('clear')
                continue
            if text == 'exit':
                break
            
            if text == 'print':
                parser.printMap()
                continue

        except EOFError:
            break
    
        if text:
            tokenList = lexer.tokenize(text)
            parser.parse(tokenList)