import os
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

linea -> ID '=' exprOR {map[ID.lexval] = exprOR.s}


exprOR -> exprAND {exprORP.h = exprAND.s} exprORP {exprOR.s = exprORP.s}
exprORP -> OR exprAND {exprORP1.h = exprORP.h || exprAND.s } exprORP {exprOR.s = exprORP.s}
      | epsilon {exprORP.s = exprORP.s}}
      
exprAND -> exprNOT {exprANDP.h = exprNOT.s} exprANDP {exprAND.s = exprANDP.h}
exprANDP -> AND exprNOT {exprANDP1.h = exprANDP.h && exprNOT.s} exprANDP
      | epsilon {exprANDP.s = exprANDP.h}
      
      
exprNOT -> NOT exprNOT {exprNOT.s = not exprNOT}
     | '(' exprOR ')' {exprNOT.s = exprOR.s}
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
     | '(' sum ')' {fact.s = sum.s}
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
    
    @_('ID "=" exprOR')
    def line(self, p):
        self.map[p.ID] = p.exprOR
        
    @_('exprAND exprORP')
    def exprOR(self, p):
        return p.exprORP

    @_('OR exprAND empty1 exprORP')
    def exprORP(self, p):
        return int(p.empty1 or p.exprAND)

    @_('')
    def empty1(self, p):
        return p[-3]

    @_('')
    def exprORP(self, p):
        return p[-1]

    @_('exprNOT exprANDP')
    def exprAND(self, p):
        return p.exprANDP

    @_('AND exprNOT empty2 exprANDP')
    def exprANDP(self, p):
        return int(p.empty2 and p.exprNOT)

    @_('')
    def empty2(self, p):
        return p[-3]
    
    @_('')
    def exprANDP(self, p):
        return p[-1]

    @_('"!" exprNOT')
    def exprNOT(self, p):
        return int(not p.exprNOT)

    # @_('"(" exprOR ")"')
    # def exprNOT(self, p):
    #     return p.exprOR

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
        return p.empty4 + p.prod
        
    @_('"-" prod empty4 sumP')
    def sumP(self, p):
        return p.empty4 - p.prod

    @_('')
    def sumP(self, p):
        return p[-1]

    @_('')
    def empty4(self, p):
        return p[-3]
    
    @_('fact prodP')
    def prod(self, p):
        return p.prodP

    @_('"*" fact empty5 prodP')
    def prodP(self, p):
        return p.empty5 * p.fact

    @_('"/"  empty5 prodP')
    def prodP(self, p):
        return p.empty5 / p.fact

    @_('')
    def prodP(self, p):
        return p[-1]
        
    @_('')    
    def empty5(self, p):
        return p[-3]

    @_('NUM')
    def fact(self, p):
        return p.NUM

    @_('ID')
    def fact(self, p):
        return self.map[p.ID]

    @_('"-" fact')
    def fact(self, p):
        return -1 * p.fact
       
    @_('"(" exprOR ")"')
    def fact(self, p):
        return p.exprOR


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