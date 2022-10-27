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

'''

starter -> funcion
        | definicion
funcion -> fun_type ID(params) {}
params -> INT ID parametros
        | epsilon
parametros -> , INT ID parametros
            | epsilon

fun_type -> VOID
          -> type
definicion -> variable ; definicion
          | call ; definicion
          | assignment ; definicion
          | epsilon

call -> ID(args)
args -> assign resto
    | epsilon
resto -> , assign resto
    | epsilon
    
variable -> tipo {list.h = tipo.s} list

list -> {assignment.h = list.h} assignment {assignments.h = assignment.h} assignments
assignments -> , {assignment.h = assignments.h} assignment {assignments1.h = assignment.h} assignments1
            | epsilon
            
assignment -> ID '=' expr {map[ID.lexval] = expr.s}

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
        self.map = {'global': {}}
        self.env = 'global'
    
    def printMap(self):
        # print(self.map)
        for key, val in self.map.items():
            print(f'-> Environment {key}')
            
            for key1, val2 in val.items():
                print(f'{key1} = {val2.get()}, env = {val2.env}')
                
            print('--------')

    @_('fun_type ID "(" params ")" emptyEnv "{" definition "}"')
    def function(self, p):
        # TODO nodo_funcion
        self.env = 'global' # restore environment
        
    @_('')
    def emptyEnv(self, p):
        self.map[p[-4]] = {}
        self.env = p[-4]
    
    @_('INT ID parameters')
    def params(self, p):
        pass
    
    @_('', 'VOID')
    def params(self, p):
        pass
    
    @_('"," INT ID parameters')
    def parameters(self, p):
        pass

    @_('')
    def parameters(self, p):
        pass
    
    @_('INT', 'VOID') 
    def fun_type(self, p):
        p[0]

    @_('declare ";" definition', 
       'assign ";" definition', 
       'PRINTF "(" content values ")" ";" definition', '')
    def definition(self, p):
        pass
    
    @_('STRING')
    def content(self, p):
        pass
    
    @_(', ID values')
    def values(self, p):
        pass
    
    @_('')
    def values(self, p):
        pass
    
    @_('ID "=" expr')
    def assign(self, p):
        if p.ID not in self.map[self.env]:
            raise SystemExit(f'Variable <{p.ID}> not defined')
            
        self.map[self.env][p.ID] = p.expr
        
    @_('expr')
    def assign(self, p):
        return p.expr
    
    @_('INT list')
    def declare(self, p): # we do not need to know its type because they are all integers for now
        pass #return p.type
    
    # @_('empty8 assignment empty9 assignments')
    @_('assignment assignments')
    def list(self, p):
       pass # return p[-2]
        
    # @_('')
    # def empty8(self, p):
    #     return p[-1]
    
    # @_('')
    # def empty9(self, p):
    #     return p[-3]
    
    # @_('"," empty10 assignment empty11 assignments', '')
    @_('"," assignment assignments', '')
    def assignments(self, p):
        pass # return

    # @_('')
    # def empty10(self, p):
    #     return p[-2]

    # @_('')
    # def empty11(self, p):
    #     return p[-4]   

    @_('ID "=" expr')
    def assignment(self, p):
        if p.ID not in self.map[self.env]:
            idNode = IdNode(p.ID, p.expr, self.env)
            self.map[self.env][p.ID] = idNode
        else:
            raise SystemExit(f'Variable <{p.ID}> already defined!')

    @_('ID')
    def assignment(self, p):
        if p.ID not in self.map[self.env]:
            self.map[self.env][p.ID] = IdNode(p.ID, 0, self.env)
        else:
            raise SystemExit(f'Variable <{p.ID}> already defined!')

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
        # return int(p[-3] or p[-1])
        return OperationNode('or', p[-3], p[-1])

    @_('')
    def empty2(self, p):
        # return int(p[-3] and p[-1])
        return OperationNode('and', p[-3], p[-1])

    @_('')
    def exprP(self, p):
        return p[-1]
    
    @_('"!" exprNOT')
    def exprNOT(self, p):
        # return int(not p.exprNOT)
        return OperationNode('not', p.exprNOT)

    @_('comp')
    def exprNOT(self, p):
        return p.comp 
    
    @_('sum compP')
    def comp(self, p):
        return p.compP
    
    @_('EQ sum empty3')
    def compP(self, p):
        return OperationNode('==', p.empty3, p.sum)#int(p.empty3 == p.sum)

    @_('NEQ sum empty3')
    def compP(self, p):
        return OperationNode('!=', p.empty3, p.sum)
    
    @_('LEQ sum empty3')
    def compP(self, p):
        return OperationNode('<=', p.empty3, p.sum)
    @_('GEQ sum empty3')
    def compP(self, p):
        return OperationNode('>=', p.empty3, p.sum)
    
    @_('"<" sum empty3')
    def compP(self, p):
        return OperationNode('<', p.empty3, p.sum)
    
    @_('">" sum empty3')
    def compP(self, p):
        return OperationNode('>', p.empty3, p.sum)

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
        # return p[-3] + p[-1]
        return OperationNode('+', p[-3], p[-1])
    
    @_('')
    def empty5(self, p):
        # return p[-3] - p[-1]
        return OperationNode('-', p[-3], p[-1])
    
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
        # return p[-3] * p[-1]
        return OperationNode('*', p[-3], p[-1])

    @_('')    
    def empty7(self, p):
        # return p[-3] // p[-1]
        return OperationNode('/', p[-3], p[-1])
        
    @_('NUM')
    def fact(self, p):
        return NumNode(p.NUM)
        # return p.NUM

    @_('ID')
    def fact(self, p):
        return self.map[self.env][p.ID]
        # return self.map[p.ID]

    @_('"-" fact')
    def fact(self, p):
        return UniqueNode('-', p.fact.get())
        # return -1 * p.fact
       
    @_('"(" expr ")"')
    def fact(self, p):
        return p.expr

    @_('call')
    def fact(self, p):
        return p.call

    @_('ID "(" fun_param fun_params ")"')
    def call(self, p):
        pass

    @_('expr')
    def fun_param(self, p):
        pass

    @_('')
    def fun_param(self, p):
        pass

    @_(', expr fun_params')
    def fun_params(self, p):
        pass

    @_('')
    def fun_params(self, p):
        pass

class OperationNode:
    def __init__(self, operator, param1, param2):
        self.operator = operator
        self.param1 = param1
        self.param2 = param2
        
    def get(self):
 
        return eval(f'int(self.param1.get() {self.operator} self.param2.get())')
        
    def write(self):
        return f'{self.param1.write()} {self.operator} {self.param2.write()}'
class UniqueNode:
    def __init__(self, operator, param):   
        self.param = param
        self.operator = operator
    def get(self):
        return eval(f'int({self.operator} self.param.get())')

    def write(self):
        return f'{self.operator} {self.param.write()}'    
class FunctionNode:
    def __init__(self, name, returnType, numParam):
        self.name = name
        self.returnType = returnType
        self.numParam = numParam

class IdNode:
    def __init__(self, id, val, env = None):
        self.id = id
        self.val = val
        self.env = env
    def get(self):
        return self.val.get()
        
    def write(self, p):
        return f'{self.id}, {self.val}, {self.env}'
    
class NumNode:
    def __init__(self, num):
        self.num = num
    
    def get(self):
        return self.num

    def write(self):
        return f'{self.num}'

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
        
#         text = '''int main(void) { int a = 2, c = 3; } 
# int foo(void) { int a = 3, c = 4; } 
#         '''

        if text:
            tokenList = lexer.tokenize(text)
            parser.parse(tokenList)