import os
from sly import Parser
from lexer import CalcLexer


instructions = []
constants = []

def CToAssembly(string, append = True):
    global instructions
    # print("NUEVO NODO")
    instructions.append(string) if append else instructions.insert(0, string)
    # with open('output.s', 'a') as file:
    #     file.write(string)

def writeToFile():
    global instructions
    string = ''.join(instructions)
    with open('output.s', 'a') as file:
        file.write(string)
        
    instructions = []

class CalcParser(Parser):
    tokens = CalcLexer.tokens
    debugfile = 'parser.txt'
    
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
           
    @_('id_global', '')
    def line(self, p):
        pass
    
    @_('VOID ID function line')
    def id_global(self, p):
        pass
    
    @_('INT ID corpus line')
    def id_global(self, p):
        pass
    
    @_('function')
    def corpus(self, p):
        pass
    
    @_('empty1 assignments ";"', 'empty1 "=" expr assignments ";"')
    def corpus(self, p):
        pass      
            
    @_('')
    def empty1(self, p):
        pass # create node id
        
        

    @_('"(" params ")" emptyEnv "{" definition "}"')
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

    @_('RETURN expr ";"')
    def definition(self, p):
        if self.foo[self.env].type == 'void':
            SysError(f'void function \'{self.env}\' should not return a value ')        # 
        
        exp = p.expr
        
        if isinstance(exp, IdNode):
            if exp.env == 'global':
                CToAssembly(f'\tmovl {exp.id}, %eax\n')
            else:
                CToAssembly(f'\tmovl {exp.pos}(%ebp), %eax\n')
                
        elif isinstance(exp, NumNode):
            CToAssembly(f'\tmovl ${exp.get()}, %eax\n')
        else:
            CToAssembly(f'\tpopl %eax\n')
    
    @_('PRINTF "(" content values ")" emptyScanfPrintf ";" definition')
    def definition(self, p):
        given, string = p.content
        needed = p.values
        if given > needed:
            SysError(f' more \'%\' conversions than data arguments')
        elif given < needed:
            SysError(f' less \'%\' conversions than data arguments')
        
        # CToAssembly(string)    
            
    @_('')
    def emptyScanfPrintf(self, p):
        CToAssembly(f'{p[-3][1]}\tcall {p[-5]}\n\taddl ${4 + p[-2]*4}, %esp\n')
       
    @_('SCANF "(" content mem_values ")" emptyScanfPrintf ";" definition')
    def definition(self, p):
        given, string = p.content
        needed = p.mem_values
        
        if given > needed:
            SysError(f' more \'%\' conversions than data arguments')
        elif given < needed:
            SysError(f' less \'%\' conversions than data arguments')
            
        # CToAssembly(string)
            
    @_('STRING')
    def content(self, p):
        global constants
        if p.STRING in constants:
            st = constants.index(p.STRING)
        else:
            st = len(constants)
            constants.append(p.STRING)
        
        CToAssembly(f'.s{st}:\n\t.string "{p.STRING}"\n', False) # create constant (string)
        string = f'\tpushl $s{st}\n' # push string into the stack
        return p.STRING.count('%d'), string 
    
    @_('"," "&" ID mem_values')
    def mem_values(self, p):
        if p.ID in self.map[self.env]:
            CToAssembly(f'\tleal {self.map[self.env][p.ID].pos}(%ebp), %eax\n\tpushl %eax\n')
        elif p.ID in self.map['global']:
            CToAssembly(f'\tpushl ${p.ID}\n')
        else:
            SysError(f'Variable \'{p.ID}\' not defined')
        return 1 + p.mem_values

        # if p.ID not in self.map[self.env] and p.ID not in self.map['global']:
        #     SysError(f'Variable \'{p.ID}\' not defined')
        # return 1 + p.mem_values

    @_('')
    def mem_values(self, p):
        return 0
    
    @_('"," ID values')
    def values(self, p):
        # if p.ID not in self.map[self.env] and p.ID not in self.map['global']:
        #     SysError(f'Variable \'{p.ID}\' not defined')
        
        if p.ID in self.map[self.env]:
            CToAssembly(f'\tpushl {self.map[self.env][p.ID].pos}(%ebp)\n')
        elif p.ID in self.map['global']:
            CToAssembly(f'\tpushl {p.ID}\n')
        else:
            SysError(f'Variable \'{p.ID}\' not defined')
        return 1 + p.values
    
    @_('')
    def values(self, p):
        return 0
    
    @_('ID "=" expr')
    def assign(self, p):
        if p.ID not in self.map[self.env] and p.ID not in self.map['global']:
            SysError(f'Variable <{p.ID}> not defined')
            
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
            self.localVar -= 4 # increment var count
            CToAssembly(f'\tsubl $4, %esp\n\tpopl %eax\n\tmovl %eax, {idNode.pos}(%ebp)\n')
        else:
            SysError(f'Variable <{p.ID}> already defined!')

    # variable declaration without assignment, default value 0
    @_('ID')
    def assignment(self, p):
        if p.ID not in self.map[self.env]:
            self.map[self.env][p.ID] = IdNode(p.ID, 0, self.localVar, self.env)
            self.localVar -= 4 # increment var count
            
            CToAssembly(f'\tsubl $4, %esp\n')
        else:
            SysError(f'Variable <{p.ID}> already defined!')

    @_('expr AND exprNOT', 'expr OR exprNOT')
    def expr(self, p):
        if p[1] == '&&':
            return OperationNode('and', p.expr, p.exprNOT)
        else:
            return OperationNode('or', p.expr, p.exprNOT)
        
    @_('exprNOT')
    def expr(self, p):
        return p.exprNOT
    
    @_('"!" exprNOT')
    def exprNOT(self, p):
        return UniqueNode('not', p.exprNOT)

    @_('comp')
    def exprNOT(self, p):
        return p.comp 
    
    @_('comp EQ sum',
       'comp NEQ sum',
       'comp GEQ sum',
       'comp LEQ sum',
       'comp ">" sum',
       'comp "<" sum')
    def comp(self, p):
        return OperationNode(p[1], p.comp, p.sum)
    
    
    @_('sum')
    def comp(self, p):
        return p.sum
    
    @_('sum "+" prod', 'sum "-" prod')
    def sum(self, p):
        OperationNode(p[1], p.sum, p.prod)
    
    @_('prod')
    def sum(self, p):
        return p.prod
    
    @_('prod "*" fact', 'prod "/" fact')
    def prod(self, p):
        OperationNode(p[1], p.prod, p.fact)
        
    @_('fact')
    def prod(self, p):
        return p.fact
     
    @_('NUM')
    def fact(self, p):
        return NumNode(p.NUM)

    @_('ID')
    def fact(self, p):
        return self.map[self.env][p.ID]

    @_('"-" fact')
    def fact(self, p):
        return UniqueNode('-', p.fact.get())
       
    @_('"(" expr ")"')
    def fact(self, p):
        return p.expr

    @_('call')
    def fact(self, p):
        return p.call
    
    @_('"[" NUM "]" dim2', '')
    def dim(self, p):
        pass
    
    @_('"[" NUM "]"', '')
    def dim2(self, p):
        pass        


    @_('ID "(" fun_param ")"')
    def call(self, p):
        if p.ID not in self.foo:
            SysError(f'Function <{p.ID}> not defined')
        
        if self.checkParam < self.foo[p.ID].params:
            SysError(f'too few arguments to function {p.ID}')
        elif self.checkParam > self.foo[p.ID].params:
            SysError(f'too many arguments to function {p.ID}')

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

def SysError(msg):
    with open('output.s', 'w') as file:
        file.write('')
    
    raise SystemExit(msg)


def main(text):
    with open('output.s', 'w') as file:
        file.write('')

    lexer = CalcLexer()
    parser = CalcParser()
    
    tokenList = lexer.tokenize(text)
    parser.parse(tokenList)
    writeToFile()

    
if __name__ == '__main__':
    
    with open('output.s', 'w') as file:
        file.write('')
        
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
            
            writeToFile()
            