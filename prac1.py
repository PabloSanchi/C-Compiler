import os
from sly import Parser
from lexer import CalcLexer
from functools import reduce

environment = [[]]
var_globales = []
instructions = []
constants = []

def searchVariable(id):
    global environment
    
    index = len(environment)-1
    for env in environment[::-1]:
        if id in env:
            return index
        index -= 1

    SysError(f'Variable \'{id}\' not defined')

def searchNotVariable(id):
    global environment
    for env in environment[len(environment)-1:0:-1]:
        if id in env:
            SysError(f'Variable \'{id}\' already defined')

    

def CToAssembly(string, append = True):
    global instructions
    # print("NUEVO NODO")
    instructions.append(string) if append else instructions.insert(0, string)
    # with open('output.s', 'a') as file:
    #     file.write(string)

def newVarGlobal(name):
    var_globales.append(".comm " + name + ", 4, 4\n")

def writeToFile():
    global instructions, var_globales
    string = ''.join(var_globales) + '\n'
    string += ''.join(instructions)
    with open('output.s', 'a') as file:
        file.write(string)
        
    instructions = []

# global variables
foo = {}
class CalcParser(Parser):
    tokens = CalcLexer.tokens
    debugfile = 'parser.txt'
    
    def __init__(self):
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
    
    @_('empty1 global_assignments ";"')
    def corpus(self, p):
        pass      
            
    @_('')
    def empty1(self, p):
        global environment
        if p[-1] in environment[0]:
            SysError(f'Variable \'{p[-1]}\' already defined')
        newVarGlobal(p[-1])
        environment[0].append(p[-1])
    
    @_('"," ID global_assignments')
    def global_assignments(self, p):
        global var_globales, environment
        if p.ID in environment[0]:
            SysError(f'Variable \'{p.ID}\' already defined')
        newVarGlobal(p.ID)
        environment[0].append(p.ID)
    
    @_('')
    def global_assignments(self, p):
        pass
    
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
        environment.pop() # Remove variables
        self.localVar = -4 # restore localVar value
        
    @_('')
    def emptyEnv(self, p):
        global foo, environment
        # create environment for the function
        environment.append({})
        # create function node
        foo[p[-4]] = FunctionNode(p[-5], p[-4], self.numParam)
        self.env = p[-4] # change environment
        # write prologue
        CToAssembly(foo[p[-4]].getPrologue())
    
        
    @_('INT ID parameters')
    def params(self, p):
        self.numParam = 1
        
    
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
        global environment
        l = []
        environ = searchVariable(p.ID)

        if environ != 0:
            l.append(f'{environment[environ][p.ID].pos}(%ebp)')
        else:
            l.append(p.ID)

        return l + p.values
    
    @_('')
    def values(self, p):
        return []

    @_('pointer "=" expr')
    def assign(self, p):
        global environment
        ID = p.pointer
        environ = searchVariable(p.ID) # if does not exists it will give an error

        CToAssembly(f'\tmovl {environment[environ][ID].pos}(%ebp), %ebx\n\tpopl %eax\n\tmovl %eax, (%ebx)\n')
   

    @_('array "=" expr')
    def assign(self, p):
        global environment
        ID, dim = p.array
        
        environ = searchVariable(ID) # if does not exists it will give an error
        
        if isinstance(p.expr, PointerNode): 
            CToAssembly(f'\tpopl %eax\n\tmovl (%eax), %eax\n\tpushl %eax\n')
        
        if environ == 0: # global variable
            CToAssembly(f'\tpopl %eax\n\tmovl %eax, {ID}\n')
        elif  isinstance(environment[environ][ID], PointerNode): # local pointer
            CToAssembly(f'\tpopl %eax\n\tmovl %eax, {environment[environ][ID].pos}(%ebp)\n')
        else: # local variable  
            CToAssembly(f'\tpopl %eax\n\tmovl %eax, {environment[environ][ID].pos - 4*environment[environ][ID].map(dim)}(%ebp)\n')
    

    @_('array "=" "&" array')
    def assign(self, p):
        global environment
        IDl, diml = p[0]
        IDr, dimr = p[3]
        
        environl = searchVariable(IDl)
        environr = searchVariable(IDr)

        # leal right variable
        if environr != 0:
            if not dimr:
                CToAssembly(f'\tleal {environment[environr][IDr].pos}(%ebp), %eax\n')
            else:
                CToAssembly(f'\tleal {environment[environr][IDr].pos - 4*environment[environr][IDr].map(dimr)}(%ebp), %eax\n')
        else:
            CToAssembly(f'\tleal {IDr}, %eax\n')
        # move local variable 
        if environl != 0:
            # if it a unique variable or pointer
            if not diml:
                CToAssembly(f'\tmovl %eax, {environment[environl][IDl].pos}(%ebp)\n')
            else:
                CToAssembly(f'\tmovl %eax, {environment[environl][IDl].pos - 4*environment[environl][IDl].map(diml)}(%ebp)\n')
        else: # IDl in self.map['global']:
            CToAssembly(f'\tmovl %eax, {IDl}\n')        
            
    @_('expr')
    def assign(self, p):
        return p.expr
    
    @_('INT list')
    def declare(self, p): # we do not need to know its type because they are all integers for now
        pass

    @_('assignment assignments')
    def list(self, p):
       pass
    
    @_('"," assignment assignments', '')
    def assignments(self, p):
        pass

    # variable declaration with assignment
    @_('array "=" expr')
    def assignment(self, p):
        global environment
        id, dim = p.array # id, dims
        
        searchNotVariable(id) # if exists it will give an error
        if isinstance(p.expr, PointerNode): 
            CToAssembly(f'\tpopl %eax\n\tmovl (%eax), %eax\n\tpushl %eax\n')
        if not dim:
            CToAssembly(f'\tsubl $4, %esp\n\tpopl %eax\n\tmovl %eax, {self.localVar}(%ebp)\n')
        else:
            SysError(f'cannot assign an integer to an array')
            
        idNode = IdNode(id, p.expr, self.localVar, self.env)
        
        environment[-1][id] = idNode
        
        self.localVar -= 4 # increment var count

    # variable declaration without assignment, default value 0
    @_('array')
    def assignment(self, p):
        global environment
        id, dim = p.array # id, dims

        sz = reduce((lambda x, y: x * y), dim) if dim else 1
        searchNotVariable(id)
    
        environment[-1][id] = IdNode(id, 0, self.localVar, self.env, dim)
        self.localVar -= 4*sz # increment var count    
        CToAssembly(f'\tsubl ${4*sz}, %esp\n')


    @_('pointer = "&" array')
    def assignment(self, p):
        global environment
        lid = p.pointer
        rid, dim = p.array
        
        environ = searchVariable(rid)
        searchNotVariable(lid)
        
        if len(environment[environ][rid].dim) != len(dim) and len(dim) != 0:
            SysError(f'The dimension does not match the original defined variable dimension')
        
        if environ != 0:   
            CToAssembly(f'\tsubl $4, %esp\n\tleal {environment[environ][rid].pos - 4*environment[environ][rid].map(dim)}(%ebp), {self.localVar}(%ebp)\n')
        else:
            CToAssembly(f'\tsubl $4, %esp\n\tmovl ${rid}, {self.localVar}(%ebp)\n')
        
        environment[-1][lid] = PointerNode(lid, self.localVar, self.env)
        self.localVar -= 4
        
        
    @_('pointer = array')
    def assignment(self, p):
        global environment
        lid = p.pointer
        rid, dim = p.array
        
        environ = searchVariable(rid)
        searchNotVariable(lid)
        
        if len(environment[environ][rid].dim) != len(dim) and len(dim) != 0:
            SysError(f'The dimension does not match the original defined variable dimension')
            
        CToAssembly(f'\tsubl $4, %esp\n\tmovl {environment[environ][rid].pos - 4*environment[environ][rid].map(dim)}(%ebp), {self.localVar}(%ebp)\n')
          
        environ[-1][rid] = PointerNode(lid, self.localVar, self.env)
        self.localVar -= 4
        
          
    @_('pointer')
    def assignment(self, p):
        ID = p.pointer
        
        searchNotVariable(ID)
    
        environment[-1][ID] = PointerNode(ID, self.localVar, self.env)
        self.localVar -= 4 # increment var count
        CToAssembly(f'\tsubl $4, %esp\n')
    


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

    @_('elm')
    def fact(self, p):
        if(len(p.elm) > 1):
            id, arr = p.elm 
        else:
            id = p.elm
        
        environ = searchVariable(id)
        
        if isinstance(environment[environ][id], IdNode):
            pos = environment[environ][id].map(arr)
            environment[environ][id].write(pos)
        else:
            environment[environ][id].write()
        return environment[environ][id]

    @_('"-" fact')
    def fact(self, p):
        return UniqueNode('-', p.fact)
       
    @_('"(" expr ")"')
    def fact(self, p):
        return p.expr

    @_('call')
    def fact(self, p):
        return p.call
    
    @_('array', 'pointer')
    def elm(self, p):
        return p[0]
    
    @_('"*" ID')
    def pointer(self, p):
        return p.ID

    @_('ID dim')
    def array(self, p):
        return p.ID, p.dim
        
    @_('"[" NUM "]" dim')
    def dim(self, p):
        aux = p.dim
        #aux.insert(0, p.NUM)
        aux.append(p.NUM)
        return aux
    
    @_('')
    def dim(self, p):
        return list()

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
        return f'\tmovl %ebp, %esp\t# EPILOGUE\n\tpopl %ebp\n\tret\n\n\n'
        
class OperationNode:
    def __init__(self, operator, param1, param2):
        self.operator = operator
        self.param1 = param1
        self.param2 = param2
        self.write()
        
    def get(self):
        return ''
      
    def write(self):
        string = '\tpopl %ebx\n\tpopl %eax\n'

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


class PointerNode:
    def __init__(self, name, localVar, env, id = None):
        self.name = name
        self.pos = localVar
        self.env = env
        self.id = id
        self.flag = 0
        
    def write(self):
        if not self.flag:
            CToAssembly(f'\tpushl {self.pos}(%ebp) # pushl id node\n')
        else:
            self.flag = 1

class IdNode:
    def __init__(self, id, val, pos, env = None, dim = []):
        self.id = id
        self.val = val
        self.env = env
        self.pos = pos
        self.dim = dim
        self.flag = 0
        
    def get(self):
        return self.val.get()
        
    def write(self, n = 0):
        if not self.flag:
            CToAssembly(f'\tpushl {self.pos - 4 * n}(%ebp) # pushl id node\n')
        else:
            self.flag = 1
        #return f'{self.pos}(%ebp)'
        #return f'{self.id}, {self.val}, {self.env}'

    def map(self, arr):
        offset, sz = 0, 1 
        print(f'map : {arr}')
        
        for i, j in zip(arr, self.dim):
            offset += sz*i
            sz *= j
        return offset
            
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
            # text = 'int a; int main() {int a = 2;} void a() {int a = 2;}'
            
            # text = 'int main(void) { int a = 2; printf("%d", a); }'
            # text = 'int a(void) { int a = 0; int b = 2; int c = 3; c = a * b; return 2*c/4; }'
            # text = 'int main(void) { int a = 2*3*4; int b = a - 2 - 1; return a; }'
            # text = 'int main(void) { int a[3][2]; a[0][0] = 25; } '
            # text = 'int main(void) { int a[2][2]; int *b; int c; int d; b = &a[0][0]; c = *b; a[0][0] = *b;  } '
            text = 'int x; int k, y; int main(void) { int a[2][2]; int *b; a[0][1] = *b; } '
            # text = 'int main(void) { int a[3][2]; int b = a[1][1] + 1; } '
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