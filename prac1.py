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

# global variables
foo = {}
class CalcParser(Parser):
    tokens = CalcLexer.tokens
    debugfile = 'parser.txt'
    
    def __init__(self):
        self.map = {'global': {}}
        self.env = 'global'
        self.localVar = -4
        self.numParam = 0
        self.checkParam = 0
           
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
        global foo
        # TODO function node
        # store the current localvar value in the function node
        foo[self.env].setLocalParams(abs(self.localVar/4))
        
        # write epilogue
        CToAssembly(foo[self.env].getEpilogue())
        
        # restore values
        self.env = 'global' # restore environment
        self.localVar = -4 # restore localVar value
        
    @_('')
    def emptyEnv(self, p):
        global foo
        # create environment for the function
        self.map[p[-4]] = {}
        self.env = p[-4]
        # create function node
        foo[p[-4]] = FunctionNode(p[-5], p[-4], self.numParam)
        
        # write prologue
        CToAssembly(foo[p[-4]].getPrologue())
    
    
    # elm -> ID DIM | pointer
    # DIM -> eps | dim2
    # pointer-> * pointer
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
    
    @_('declare ";" definition', 
       'assign ";" definition', 
        '')
    def definition(self, p):
        pass

    @_('RETURN expr ";"')
    def definition(self, p):
        global foo
        if foo[self.env].type == 'void':
            SysError(f'void function \'{self.env}\' should not return a value ')        # 
        
        exp = p.expr
        CToAssembly(f'\tpopl %eax # RETURN\n')
    
    @_('funName "(" content values ")" emptyScanfPrintf ";" definition')
    def definition(self, p):
        pass
            
    @_('')
    def emptyScanfPrintf(self, p):
        return callNode(p[-5], [p[-3]] + p[-2])
        
    @_('PRINTF', 'SCANF')
    def funName(self, p):
        return p[0]
  
    @_('STRING')
    def content(self, p):
        global constants
        if p.STRING in constants:
            st = constants.index(p.STRING)
        else:
            st = len(constants)
            constants.append(p.STRING)
        
        CToAssembly(f'.s{st}:\n\t.string {p.STRING}\n', False) # create constant (string)
        string = f'$s{st}'
        return string 
    
    @_('"," ID values')
    def values(self, p):
        l = []
        if p.ID in self.map[self.env]:
            l.append(f'{self.map[self.env][p.ID].pos}(%ebp)')
            # CToAssembly(f'\tpushl {self.map[self.env][p.ID].pos}(%ebp)\n')
        elif p.ID in self.map['global']:
            l.append(p.ID)
            # CToAssembly(f'\tpushl {p.ID}\n')
        else:
            SysError(f'Variable \'{p.ID}\' not defined')
        return l + p.values
    
    @_('')
    def values(self, p):
        return []
    
    @_('ID "=" expr')
    def assign(self, p):
        if p.ID not in self.map[self.env] and p.ID not in self.map['global']:
            SysError(f'Variable <{p.ID}> not defined')
            
        #self.map[self.env][p.ID] = p.expr
        CToAssembly(f'\tpopl %eax\n\tmovl %eax, {self.map[self.env][p.ID].pos}(%ebp)\n')
        
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
            
            CToAssembly(f'\tsubl $4, %esp\n\tpopl %eax\n\tmovl %eax, {self.localVar}(%ebp)\n')
            idNode = IdNode(p.ID, p.expr, self.localVar, self.env)
            self.map[self.env][p.ID] = idNode
            self.localVar -= 4 # increment var count
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

    @_('pointer')
    def assignment(self, p):
        if p.ID not in self.map[self.env]:
            self.map[self.env][p.ID] = IdNode(p.ID, 0, self.localVar, self.env)
            self.localVar -= 4 # increment var count
            
            CToAssembly(f'\tsubl $4, %esp\n')
        else:
            SysError(f'Variable <{p.ID}> already defined!')


    @_('array')
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
        return OperationNode(p[1], p.sum, p.prod)
    
    @_('prod')
    def sum(self, p):
        return p.prod
    
    @_('prod "*" fact', 'prod "/" fact')
    def prod(self, p):
        return OperationNode(p[1], p.prod, p.fact)
        
    @_('fact')
    def prod(self, p):
        return p.fact
     
    @_('NUM')
    def fact(self, p):
        node = NumNode(p.NUM)
        node.write()
        return node

    @_('ID')
    def fact(self, p):
        if p.ID in self.map[self.env]:
            self.map[self.env][p.ID].write()
        return self.map[self.env][p.ID]
    
    # @_('pointer')
    # def fact(self, p):
    #     pass

    @_('"-" fact')
    def fact(self, p):
        return UniqueNode('-', p.fact)
       
    @_('"(" expr ")"')
    def fact(self, p):
        return p.expr

    @_('call')
    def fact(self, p):
        return p.call
    
    @_('array', 'pointer', 'ID')
    def elm(self, p):
        return p[0]
    
    @_('ID "[" NUM "]" dim')
    def array(self, p):
        num_el = p.dim * p.NUM
        
    @_('"*" ID')
    def pointer(self, p):
        pass
    
    @_('"[" NUM "]"')
    def dim(self, p):
        return p.NUM
    
    @_('')
    def dim(self, p):
        return 1   

    @_('ID "(" fun_param ")"')
    def call(self, p):
        return callNode()

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


class callNode:
    def __init__(self, name, params):
        global foo, constants
        if name != 'printf' and name != 'scanf':
            if name not in foo:
                SysError(f'Function <{name}> not defined')
            if foo[name].type == 'void':
                SysError(f'Function <{name}> is void type')
            if len(params) < foo[name].params:
                SysError(f'too few arguments to function {name}')
            elif len(params) > foo[name].params:
                SysError(f'too many arguments to function {name}')
        else:
            
            given = len(params)-1
            needed = constants[int(params[0][2:])].count('%d')
                     
            if given > needed:
                SysError(f' more \'%\' conversions than data arguments')
            elif given < needed:
                SysError(f' less \'%\' conversions than data arguments')
                        
        self.name = name
        self.params = params
        self.write()

    def write(self):
        
        for param in self.params[::-1]:
            CToAssembly(f'\tpushl {param}\n')
        CToAssembly(f'\tcall {self.name}\n\taddl ${len(self.params)*4}, %esp\n')

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
        return f'\tmovl %ebp, %esp\n\tpopl %ebp\n\tret\n\n\n'
        
class OperationNode:
    def __init__(self, operator, param1, param2):
        self.operator = operator
        self.param1 = param1
        self.param2 = param2
        self.write()
        
    def get(self):
        return ''
      
    def write(self):
        
        # self.param1.write()
        # self.param2.write()
        string = '\tpopl %ebx\n\tpopl %eax\n'
        # string = ''
        
        # if isinstance(self.param2, IdNode):
        #     string = '\tmovl ' + self.param2.write() + ', %ebx\n'
        #     p2str = '%ebx'
        # elif isinstance(self.param2, NumNode): # if it is a number store get its content
        #     string = f'\tmovl ${self.param2.write()}, %ebx\n'
        #     p2str = "$" + self.param2.write()
        # else:
        #     string = '\tpopl %ebx\n'
        #     p2str = '%ebx'

        # if isinstance(self.param1, IdNode):
        #     string+= f'\tmovl {self.param1.write()}, %eax\n'
        # elif isinstance(self.param1, NumNode):
        #     string += '\tmovl $' + str(self.param1.write()) + ', %eax\n'
        # else:
        #     string += '\tpopl %eax\n'

        if self.operator == '+':
            string +='\taddl %ebx, %eax\n'
            string +='\tpushl %eax\n'
        elif self.operator == '-':
            string +='\tsubl %ebx, %eax\n'
            string +='\tpushl %eax\n'
        elif self.operator == '*':
            string +='\timull %ebx, %eax\n'
            string +='\tpushl %eax\n'
        elif self.operator == '/':
            string +='\tcdq\n'
            string +='\tidivl %ebx\n'
            string +='\tpushl %eax\n'
            

        CToAssembly(string)
        return ''
            
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
        self.flag = 0
    def get(self):
        return self.val.get()
        
    def write(self):
        if not self.flag:
            CToAssembly(f'\tpushl {self.pos}(%ebp) # pushl id node\n')
        else:
            self.flag = 1
        #return f'{self.pos}(%ebp)'
        #return f'{self.id}, {self.val}, {self.env}'
    
class NumNode:
    def __init__(self, num):
        self.num = num
        
    def get(self):
        return self.num

    def write(self):
        # return f'{self.num}'
        CToAssembly(f'\tpushl ${self.num} # pushl num node\n')

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
            # text = input('> ')
            text = 'int main(void) { int a = 2; printf("%d", a); }'
            # text = 'int a(void) { int a = 0; int b = 2; int c = 3; c = a * b; return 2*c/4; }'
            # text = 'int main(void) { int a = 2*3*4; int b = a - 2 - 1; return a; }'
            if text == 'clear':
                os.system('clear')
                continue
            if text == 'exit':
                break

        except EOFError:
            break

        if text:
            tokenList = lexer.tokenize(text)
            parser.parse(tokenList)
            
            writeToFile()
            break
            