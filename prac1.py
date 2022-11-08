import os
from sly import Parser
from lexer import CalcLexer

def CToAssembly(string):
    # print("NUEVO NODO")
    with open('output.s', 'a') as file:
        file.write(string)

class CalcParser(Parser):
    tokens = CalcLexer.tokens
    # debugfile = 'parser.txt'
    
    def __init__(self):
        self.foo = {}
        self.map = {'global': {}}
        self.env = 'global'
        self.localVar = -4
        self.numParam = 0
        self.checkParam = 0
    
    def printMap(self):
        print(self.map)
        for key, val in self.map.items():
            print(f'-> Environment {key}')
            
            for key1, val2 in val.items():
                print(f'{key1} = {val2.get()}, env = {val2.env}')
                
            print('--------')
        
    @_('fun_type ID "(" params ")" emptyEnv "{" definition "}"')
    def function(self, p):
        # TODO function node
        # store the current localvar value in the function node
        self.foo[self.env].setLocalParams(abs(self.localVar/4))
        
        
        # write epilogue
        CToAssembly(self.foo[self.env].getEpilogue())
        
        # restore values
        self.env = 'global' # restore environment
        self.localVar = -4 # restore localVar value
        
    @_('')
    def emptyEnv(self, p):
        # create environment for the function
        self.map[p[-4]] = {}
        self.env = p[-4]
        # create function node
        self.foo[p[-4]] = FunctionNode(p[-5], p[-4], self.numParam)
        
        # write prologue
        CToAssembly(self.foo[p[-4]].getPrologue())
        
        
    
    @_('INT ID parameters')
    def params(self, p):
        self.numParam = 1
        
    # e.g. int name() || int name(void)
    @_('', 'VOID')
    def params(self, p):
        self.numParam = 0
    
    @_('"," INT ID parameters')
    def parameters(self, p):
        self.numParam += 1

    @_('')
    def parameters(self, p):
        pass
    
    @_('INT', 'VOID') 
    def fun_type(self, p):
        p[0]

    @_('declare ";" definition', 
       'assign ";" definition', 
        '')
    def definition(self, p):
        pass

    @_('RETURN expr ";" definition')
    def definition(self, p):
        if self.foo[self.env].type == 'void':
            raise SystemExit(f'void function \'{self.env}\' should not return a value ')        # 
        CToAssembly(f'\tpopl %eax\n')
    
    # @_('RETURN ID ";" definition')
    # def definition(self, p):
    #     CToAssembly(f'\tmovl {self.map[self.env][p.ID].pos}(%ebp), %eax\n')
        
    # @_('RETURN NUM ";" definition')
    # def definition(self, p):
    #     CToAssembly(f'\tmovl ${p.NUM}, %eax\n')

    @_('PRINTF "(" content values ")" ";" definition')
    def definition(self, p):
        given = p.content
        needed = p.values
        if given > needed:
            raise SystemExit(f' more \'%\' conversions than data arguments')
        elif given < needed:
            raise SystemExit(f' less \'%\' conversions than data arguments')

    @_('SCANF "(" content mem_values ")" ";" definition')
    def definition(self, p):
        given = p.content
        needed = p.mem_values
        if given > needed:
            raise SystemExit(f' more \'%\' conversions than data arguments')
        elif given < needed:
            raise SystemExit(f' less \'%\' conversions than data arguments')

    @_('STRING')
    def content(self, p):
        return p.STRING.count('%d')
    
    @_('"," "&" ID mem_values')
    def mem_values(self, p):
        if p.ID not in self.map[self.env]:
            raise SystemExit(f'Variable \'{p.ID}\' not defined')
        return 1 + p.mem_values

    @_('')
    def mem_values(self, p):
        return 0
    
    @_('"," ID values')
    def values(self, p):
        if p.ID not in self.map[self.env]:
            raise SystemExit(f'Variable \'{p.ID}\' not defined')
        return 1 + p.values
    
    @_('')
    def values(self, p):
        return 0
    
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
    
    # @_('"," empty10 assignment empty11 assignments', '')
    @_('"," assignment assignments', '')
    def assignments(self, p):
        pass # return

    # variable declaration with assignment
    @_('ID "=" expr')
    def assignment(self, p):
        if p.ID not in self.map[self.env]:
            idNode = IdNode(p.ID, p.expr, self.localVar, self.env)
            self.map[self.env][p.ID] = idNode
            self.localVar -= -4 # increment var count
            CToAssembly(f'\tsubl $4, %esp\n\tpopl %eax\n\tmovl %eax, {idNode.pos}(%ebp)\n')
        else:
            raise SystemExit(f'Variable <{p.ID}> already defined!')

    # variable declaration without assignment, default value 0
    @_('ID')
    def assignment(self, p):
        if p.ID not in self.map[self.env]:
            self.map[self.env][p.ID] = IdNode(p.ID, 0, self.localVar, self.env)
            self.localVar -= -4 # increment var count
            
            CToAssembly(f'\tsubl $4, %esp\n')
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
        OperationNode('+', p[-3], p[-1])
    
    @_('')
    def empty5(self, p):
        # return p[-3] - p[-1]
        OperationNode('-', p[-3], p[-1])
    
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



    @_('ID "(" fun_param ")"')
    def call(self, p):
        if p.ID not in self.foo:
            raise SystemExit(f'Function <{p.ID}> not defined')
        
        if self.checkParam < self.foo[p.ID].params:
            raise SystemError(f'too few arguments to function {p.ID}')
        elif self.checkParam > self.foo[p.ID].params:
            raise SystemError(f'too many arguments to function {p.ID}')

    @_('expr fun_params')
    def fun_param(self, p):
        self.checkParam = 1

    @_('')
    def fun_param(self, p):
        self.checkParam = 0

    @_('"," expr fun_params')
    def fun_params(self, p):
        self.checkParam += 1

    @_('')
    def fun_params(self, p):
        pass


class FunctionNode:
    def __init__(self, type, name, params, localParams = 0):
        self.type = type
        self.name = name
        self.params = params
        self.localParams = localParams
        
    def setLocalParams(self, params):
        self.localParams = params
        
    def getPrologue(self):
        a = f'.text\n.globl {self.name}\n.type {self.name}, @function\n{self.name}:\n\n'
        b = f'\tpushl %ebp\n\tmovl %esp, %ebp\n'
        # c = f'\tsubl ${self.localParams}, %esp\n' # if self.localParams > 0 else '\n'
        return a + b 
        
        
    def getEpilogue(self):
        return f'\tmovl %ebp, %esp\n\tpop %ebp\n\tret\n\n\n'
        
class OperationNode:
    def __init__(self, operator, param1, param2):
        self.operator = operator
        self.param1 = param1
        self.param2 = param2
        self.write()
        
    def get(self):
        return eval(f'int(self.param1.get() {self.operator} self.param2.get())')
      
    def write(self):
        string = ''
        if isinstance(self.param2, IdNode):
            string = '\tmovl ' + self.param2.write() + ', %ebx\n'
            p2str = '%ebx'
        elif isinstance(self.param2, NumNode): # if it is a number store get its content
            p2str = "$" + self.param2.write()
        else:
            string = '\tpopl %ebx\n'
            p2str = '%ebx'

        if isinstance(self.param1, IdNode):
            string+= f'\tmovl {self.param1.write()}, %eax\n'
        elif isinstance(self.param1, NumNode):
            string += '\tmovl $' + str(self.param1.write()) + ', %eax\n'
        else:
            string += '\tpopl %eax\n'

        if self.operator == '+':
            string +='\taddl ' + p2str + ', %eax\n'
            string +='\tpushl %eax\n'
        elif self.operator == '-':
            string +='\tsubl ' + p2str + ', %eax\n'
            string +='\tpushl %eax\n'
        elif self.operator == '*':
            string +='\timull ' + p2str + ', %eax\n'
            string +='\tpushl %eax\n'
        elif self.operator == '/':
            string +='\tcdq\n'
            string +='\tidivl ' + p2str + '\n'
            string +='\tpushl %eax\n'
            

        CToAssembly(string)
        return string
            
class UniqueNode:
    def __init__(self, operator, param):   
        self.param = param
        self.operator = operator
    def get(self):
        return eval(f'int({self.operator} self.param.get())')

    def write(self):
        return f'{self.operator} {self.param.write()}'    

class IdNode:
    def __init__(self, id, val, pos, env = None):
        self.id = id
        self.val = val
        self.env = env
        self.pos = pos
        
    def get(self):
        return self.val.get()
        
    def write(self):
        return f'{self.pos}(%ebp)'
        #return f'{self.id}, {self.val}, {self.env}'
    
class NumNode:
    def __init__(self, num):
        self.num = num
    
    def get(self):
        return self.num

    def write(self):
        return f'{self.num}'


def main(text):
    with open('output.s', 'w') as file:
        file.write('')

    lexer = CalcLexer()
    parser = CalcParser()
    
    tokenList = lexer.tokenize(text)
    parser.parse(tokenList)

    
# if __name__ == '__main__':
    
#     with open('output.s', 'w') as file:
#         file.write('')
        
#     lexer = CalcLexer()
#     parser = CalcParser()

#     while True:
#         try:
#             text = input('> ')
#             if text == 'clear':
#                 os.system('clear')
#                 continue
#             if text == 'exit':
#                 break
            
#             if text == 'print':
#                 parser.printMap()
#                 continue

#         except EOFError:
#             break

#         if text:
#             tokenList = lexer.tokenize(text)
#             parser.parse(tokenList)
            