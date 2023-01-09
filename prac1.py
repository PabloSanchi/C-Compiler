import os
from sly import Parser
from lexer import CalcLexer
from functools import reduce

environment = [[]]
var_globales = []
instructions = []
constants = []
label = 0

def searchTopLocalVar():
    global environment

    top = -4
    
    # loop through the environment array in reverse order
    for env in environment[len(environment)-1:0:-1]:
        if env:
            for var in env.values():
                top = min(top, var.pos)

            return top - 4
    
    return top


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
    if id in environment[-1]:
        SysError(f'Variable \'{id}\' already defined')
    # for env in environment[len(environment)-1:0:-1]:
    #     if id in env:
    #         SysError(f'Variable \'{id}\' already defined')

    

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
        params = p[-2]
        environment.append({})
        if params:
            pos = 8
            for param in params:
                if param[0] == '*':
                    environment[-1][param[1:]] = PointerNode(param[1:], pos, p[-4])
                else:
                    environment[-1][param] = IdNode(param, 0, pos)
                pos += 4
        # create function node
        foo[p[-4]] = FunctionNode(p[-5], p[-4], len(params))
        self.env = p[-4] # change environment
        # write prologue
        CToAssembly(foo[p[-4]].getPrologue())
    
        
    @_('INT ID parameters')
    def params(self, p):
        return [p.ID] +  p.parameters
        
    @_('INT pointer parameters')
    def params(self, p):
        return ['*'+p.pointer] +  p.parameters

    @_('', 'VOID')
    def params(self, p):
        return []
    
    @_('"," INT ID parameters')
    def parameters(self, p):
        return [p.ID] + p.parameters

    @_('"," INT pointer parameters')
    def parameters(self, p):
        return ['*'+p.pointer] + p.parameters

    @_('')
    def parameters(self, p):
        return []
    
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
    
    @_('IF "(" expr ")" emptyIf "{" definition "}" otherwise')
    def definition(self, p):    
        pass
        
    @_('')
    def emptyIf(self, p):
        global environment, label
        # create environment
        environment.append({})
        CToAssembly(f'\tpopl %eax\n\tcmpl $0, %eax\n\tje label{label} # if label\n')
        label += 1
        return label-1
    
    @_('emptyEndIf definition')
    def otherwise(self, p):
        pass

    @_('')
    def emptyEndIf(self, p):
        # destroy environment
        global environment
        environment.pop()
        CToAssembly(f'label{p[-4]}:\n')
        self.localVar = searchTopLocalVar()
        # print(self.localVar)

    @_('ELSE emptyElse "{" definition "}" emptyEndElse definition')
    def otherwise(self, p):
        pass
    
    @_('')
    def emptyElse(self, p):
        global label, environment
        environment.pop()
        self.localVar = searchTopLocalVar()
        environment.append({})
        CToAssembly(f'\tjmp label{label}\n')
        CToAssembly(f'label{p[-5]}:\n')
        label += 1
        return label-1

    @_('')
    def emptyEndElse(self, p):
        global environment
        environment.pop()
        CToAssembly(f'label{p[-4]}:\n')
        self.localVar = searchTopLocalVar()
        print(self.localVar)
        
    
    @_('WHILE emptySetLabelWhile "(" expr ")" emptyWhile "{" definition "}" emptyEndWhile definition')
    def definition(self, p):
        pass
    
    
    @_('')
    def emptySetLabelWhile(self, p):
        global label
        
        CToAssembly(f'label{label}: # while init label\n') # first while label
        label += 1
        return label-1
    
    @_('')
    def emptyWhile(self, p):
        global environment, label
        # create environment
        environment.append({})
        CToAssembly(f'\tpopl %eax\n\tcmpl $0, %eax\n\tje label{label} # while exit label\n') # exit while label
        label += 1
        return label-1 # return first while label
        
    @_('')
    def emptyEndWhile(self, p):
        global environment
        environment.pop()
        jumpTo = p[-8] # get label of while first label
        exitLabel = p[-4]
        # p[-6].write() # write while condition
        CToAssembly(f'\tjmp label{jumpTo} # goto while init label\n') # jump to while first label
        CToAssembly(f'label{exitLabel}: # exit label\n') # exit while label
        self.localVar = searchTopLocalVar() # restore localVar value
        print(self.localVar)
     
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
        string = f'pushl $s{st}'
        return string 
    
    @_('"," elm values')
    def values(self, p):
        global environment
        l = []
        
        if(len(p.elm) > 1): # ARRAY, or pointer without *
            id, dim = p.elm 
            environ = searchVariable(id)
            if environ != 0:
                if isinstance(environment[environ][id], PointerNode):
                    l.append(f'pushl {environment[environ][id].pos}(%ebp)')
                else:
                    l.append(f'pushl {environment[environ][id].pos - 4*environment[environ][id].map(dim)}(%ebp)')
            else:
                l.append(f'pushl {id}')
        else: # POINTER with *
            id = p.elm
            environ = searchVariable(id)
            l.append(f'movl {environment[environ][id].pos}(%ebp), %eax\n\tmovl [%eax], %eax\n\tpushl %eax')

        return l + p.values

    @_('"," "&" elm values')
    def values(self, p):
        global environment
        l = []
        
        if(len(p.elm) > 1): # ARRAY, or pointer without *
            id, dim = p.elm 
            environ = searchVariable(id)
            if environ != 0:
                if isinstance(environment[environ][id], PointerNode):
                    l.append(f'leal {environment[environ][id].pos}(%ebp), %eax\n\tpushl %eax')
                else:
                    l.append(f'leal {environment[environ][id].pos - 4*environment[environ][id].map(dim)}(%ebp), %eax\n\tpushl %eax')
            else:
                l.append(f'pushl ${id}')
        else: # ref to POINTER (&*), &*a == a (a is a pointer)
            id = p.elm
            environ = searchVariable(id)
            l.append(f'pushl {environment[environ][id].pos}(%ebp)')
        
        return l + p.values
    
    @_('')
    def values(self, p):
        return []

    @_('pointer "=" expr')
    def assign(self, p):
        global environment, foo
        ID = p.pointer
        expr = p.expr
        environ = searchVariable(ID) # if does not exists it will give an error

        if isinstance(expr, callNode) and foo[expr.name] == 'void':
            SysError(f'a value of type "void" cannot be used to assign/initialize an entity of type "int"')
            
        if isinstance(environment[environ][ID], PointerNode):
            CToAssembly(f'\tmovl {environment[environ][ID].pos}(%ebp), %ebx\n\tpopl %eax\n\tmovl %eax, [%ebx]\n')
        else:
            SysError('operand of "*" must be a pointer but has type "int"')
   

    @_('array "=" expr')
    def assign(self, p):
        global environment, foo
        ID, dim = p.array
        expr = p.expr
        environ = searchVariable(ID) # if does not exists it will give an error
        
        if isinstance(expr, callNode) and foo[expr.name] == 'void': 
            SysError(f'a value of type "void" cannot be used to assign/initialize an entity of type "int"')
            
        if environ != 0 and len(environment[environ][ID].dim) != len(dim) and len(dim) != 0:
            SysError(f'The dimension does not match the original defined variable dimension')
        
        if isinstance(p.expr, PointerNode): 
            CToAssembly(f'\tpopl %eax\n\tmovl [%eax], %eax\n\tpushl %eax\n')
        
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

        if environl != 0 and len(environment[environl][IDl].dim) != len(diml) and len(diml) != 0:
            SysError(f'The dimension does not match the original defined variable dimension')
        
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
        CToAssembly(f'\tpopl %eax\n')
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
        global environment, foo
        id, dim = p.array # id, dims
        expr = p.expr
        searchNotVariable(id) # if exists it will give an error
        
        if isinstance(expr, callNode) and foo[expr.name] == 'void': 
            SysError(f'a value of type "void" cannot be used to assign/initialize an entity of type "int"')
            
        if isinstance(p.expr, PointerNode): 
            CToAssembly(f'\tpopl %eax\n\tmovl [%eax], %eax\n\tpushl %eax\n')
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
        
        if len(environment[environ][rid].dim) < len(dim) and len(dim) != 0:
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
                
        if environ != 0 and len(environment[environ][rid].dim) != len(dim) and len(dim) != 0:
            SysError(f'The dimension does not match the original defined variable dimension')
            
        if environ != 0:
            CToAssembly(f'\tsubl $4, %esp\n\tmovl {environment[environ][rid].pos - 4*environment[environ][rid].map(dim)}(%ebp), {self.localVar}(%ebp)\n')
        else:
            CToAssembly(f'\tsubl $4, %esp\n\tmovl {rid}, {self.localVar}(%ebp)\n')
          
        environment[-1][lid] = PointerNode(lid, self.localVar, self.env)
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
            id, dim = p.elm 
        else: # POINTER
            id = p.elm
        
        environ = searchVariable(id)
        
        if environ == 0: # GLOBAL
            CToAssembly(f'\tpushl {id}\n')
        elif isinstance(environment[environ][id], IdNode): # LOCAL
            pos = environment[environ][id].map(dim)
            environment[environ][id].write(pos)
        else: # POINTER
            environment[environ][id].write()
        
        return environment[environ][id] if environ > 0 else id

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
        # print(f'param: {p.fun_param}')
        return callNode(p.ID, p.fun_param)

    @_('elm fun_params')
    def fun_param(self, p):
        global environment
        l = []
        
        if(len(p.elm) > 1): # ARRAY, or pointer without *
            id, dim = p.elm 
            environ = searchVariable(id)
            if environ != 0:
                if isinstance(environment[environ][id], PointerNode):
                    l.append(f'pushl {environment[environ][id].pos}(%ebp)')
                else:
                    if len(environment[environ][id].dim) != len(dim):
                        SysError(f'The dimension does not match the original defined variable dimension')
                    else:
                        l.append(f'pushl {environment[environ][id].pos - 4*environment[environ][id].map(dim)}(%ebp)')
            else:
                l.append(f'pushl {id}')
        else: # POINTER with *
            id = p.elm
            environ = searchVariable(id)
            l.append(f'movl {environment[environ][id].pos}(%ebp), %eax\n\tmovl [%eax], %eax\n\tpushl %eax')

        return l + p.fun_params

    @_('"&" elm fun_params')
    def fun_param(self, p):
        global environment
        l = []
        
        if(len(p.elm) > 1): # ARRAY, or pointer without *
            id, dim = p.elm 
            environ = searchVariable(id)
            
            if environ != 0:
                if isinstance(environment[environ][id], PointerNode):
                    l.append(f'leal {environment[environ][id].pos}(%ebp), %eax\n\tpushl %eax')
                else:
                    if len(environment[environ][id].dim) != len(dim):
                        SysError(f'The dimension does not match the original defined variable dimension')
                    else:
                        l.append(f'leal {environment[environ][id].pos - 4*environment[environ][id].map(dim)}(%ebp), %eax\n\tpushl %eax')
            else:
                l.append(f'pushl ${id}')
                
        else: # ref to POINTER (&*), &*a == a (a is a pointer)
            id = p.elm
            environ = searchVariable(id)
            l.append(f'pushl {environment[environ][id].pos}(%ebp)')
        
        return l + p.fun_params

    @_('')
    def fun_param(self, p):
        return []

    @_('"," elm fun_params')
    def fun_params(self, p):
        global environment
        l = []
        
        if(len(p.elm) > 1): # ARRAY, or pointer without *
            id, dim = p.elm 
            environ = searchVariable(id)
            if environ != 0:
                if isinstance(environment[environ][id], PointerNode):
                    l.append(f'pushl {environment[environ][id].pos}(%ebp)')
                else:
                    if len(environment[environ][id].dim) != len(dim):
                        SysError(f'The dimension does not match the original defined variable dimension')
                    else:
                        l.append(f'pushl {environment[environ][id].pos - 4*environment[environ][id].map(dim)}(%ebp)')
            else:
                l.append(f'pushl {id}')
        else: # POINTER with *
            id = p.elm
            environ = searchVariable(id)
            l.append(f'movl {environment[environ][id].pos}(%ebp), %eax\n\tmovl [%eax], %eax\n\tpushl %eax')

        return l + p.fun_params

    @_('"," "&" elm fun_params')
    def fun_params(self, p):
        global environment
        l = []
        
        if(len(p.elm) > 1): # ARRAY, or pointer without *
            id, dim = p.elm 
            environ = searchVariable(id)
            if environ != 0:
                if isinstance(environment[environ][id], PointerNode):
                    l.append(f'leal {environment[environ][id].pos}(%ebp), %eax\n\tpushl %eax')
                else:
                    if len(environment[environ][id].dim) != len(dim):
                        SysError(f'The dimension does not match the original defined variable dimension')
                    else:
                        l.append(f'leal {environment[environ][id].pos - 4*environment[environ][id].map(dim)}(%ebp), %eax\n\tpushl %eax')
            else:
                l.append(f'pushl ${id}')
        else: # ref to POINTER (&*), &*a == a (a is a pointer)
            id = p.elm
            environ = searchVariable(id)
            l.append(f'pushl {environment[environ][id].pos}(%ebp)')
        
        return l + p.fun_params
    
    @_('')
    def fun_params(self, p):
        return []


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
        else: # PRINTF or SCANF
            given = len(params)-1
            needed = constants[int(params[0][8:])].count('%d')
            if given > needed:
                SysError(f' more \'%\' conversions than data arguments')
            elif given < needed:
                SysError(f' less \'%\' conversions than data arguments')
                        
        self.name = name
        self.params = params
        self.write()

    def write(self):
        
        for param in self.params[::-1]:
            print(param)
            if param != '':
                CToAssembly(f'\t{param}\n')
        
        if(len(self.params) > 0):
            CToAssembly(f'\tcall {self.name}\n\taddl ${len(self.params)*4}, %esp\n')
        else:
            CToAssembly(f'\tcall {self.name}\n')

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
        global foo
        
        if isinstance(param1, callNode) and foo[param1.name].type == 'void':
            SysError(f'a value of type "void" cannot be used to assign/initialize an entity of type "int"')
        
        if isinstance(param2, callNode) and foo[param2.name].type == 'void':
            SysError(f'a value of type "void" cannot be used to assign/initialize an entity of type "int"')
        
        self.operator = operator
        self.param1 = param1
        self.param2 = param2
        self.write()
        
    def get(self):
        return ''
      
    def write(self):
        global label
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
        elif self.operator == '>':
            string += '\tcmpl %ebx, %eax\n'
            string += f'\tjg label{label}\n'
            string += f'\tpushl $0\n\tjmp label{label+1}\n'
            string += f'label{label}:\n'
            string += f'\tpushl $1\n'
            string += f'label{label+1}:\n'
            label += 2
        elif self.operator == '<':
            string += '\tcmpl %ebx, %eax\n'
            string += f'\tjl label{label}\n'
            string += f'\tpushl $0\n\tjmp label{label+1}\n'
            string += f'label{label}:\n'
            string += f'\tpushl $1\n'
            string += f'label{label+1}:\n'
            label += 2
        elif self.operator == '<=':
            string += '\tcmpl %ebx, %eax\n'
            string += f'\tjle label{label}\n'
            string += f'\tpushl $0\n\tjmp label{label+1}\n'
            string += f'label{label}:\n'
            string += f'\tpushl $1\n'
            string += f'label{label+1}:\n'
            label += 2
        elif self.operator == '>=':
            string += '\tcmpl %ebx, %eax\n'
            string += f'\tjge label{label}\n'
            string += f'\tpushl $0\n\tjmp label{label+1}\n'
            string += f'label{label}:\n'
            string += f'\tpushl $1\n'
            string += f'label{label+1}:\n'
            label += 2
        elif self.operator == "==":
            string += '\tcmpl %ebx, %eax\n'
            string += f'\tje label{label}\n'
            string += f'\tpushl $0\n\tjmp label{label+1}\n'
            string += f'label{label}:\n'
            string += f'\tpushl $1\n'
            string += f'label{label+1}:\n'
            label += 2
        elif self.operator == '!=':
            string += '\tcmpl %ebx, %eax\n'
            string += f'\tjne label{label}\n'
            string += f'\tpushl $0\n\tjmp label{label+1}\n'
            string += f'label{label}:\n'
            string += f'\tpushl $1\n'
            string += f'label{label+1}:\n'
            label += 2
        elif self.operator == 'and':
            
            # first check        
            string += '\tcmpl $0, %eax\t # E1 AND\n'
            string += f'\tje label{label}\n' # final label
            # second check
            string += '\tcmpl $0, %ebx # E2 AND\n'
            string += f'\tje label{label}\n' # final label
            string += '\tpushl $1\n'
            string += f'\tjmp label{label+1}\n' # exit label              
            # results
            string += f'label{label}:\n'
            string += '\tpushl $0\n'
            string += f'label{label+1}:\n'
            
            label += 2
        elif self.operator == 'or':
            # first check        
            string += '\tcmpl $0, %eax\t# E1 OR\n'
            string += f'\tjne label{label}\n' # final label
            # second check
            string += '\tcmpl $0, %ebx\t# E2 OR\n'
            string += f'\tjne label{label}\n' # final label
            string += '\tpushl $0\n'
            string += f'\tjmp label{label+1}\n' # exit label             
            # results
            string += f'label{label}:\n'
            string += '\tpushl $1\n'
            string += f'label{label+1}:\n'
            
            label +=2
        CToAssembly(string)
        return ''            
class UniqueNode:
    def __init__(self, operator, param):   
        
        if isinstance(param, callNode) and foo[param.name].type == 'void':
            SysError(f'a value of type "void" cannot be used to assign/initialize an entity of type "int"')
            
        self.param = param
        self.operator = operator
        self.write()

    def write(self):
        global label
        if self.operator == '-':
            string = '\tpopl %eax\n'
            string += '\tmovl $-1, %ebx\n'
            string +='\timull %ebx, %eax\n'
            string +='\tpushl %eax\n'
        elif self.operator == 'not':
            string = f'\tpopl %eax # not\n'
            string += f'\tcmpl $0, %eax\n'
            string += f'\tje label{label}\n'
            string += f'\tpushl $0\n'
            string += f'\tjmp label{label+1}\n'
            string += f'label{label}:\n'
            string += f'\tpushl $1\n'
            string += f'label{label+1}:\n'
            label += 2
        
        CToAssembly(string)   
        return ''


class PointerNode:
    def __init__(self, name, localVar, env, id = None):
        self.name = name
        self.pos = localVar
        self.env = env
        self.id = id
        self.flag = 0
        # self.write()
        
    def write(self):
        if not self.flag:
            CToAssembly(f'\tpushl {self.pos}(%ebp) # pushl pointer dir node\n')
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
        # 0 padding left in arr to match dim
        arr = [0]*(len(self.dim) - len(arr)) + arr
        print(arr)
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
    
    print(text)
    
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
            text = 'int main(void) { printf("Hello world!"); }'
            # text = 'int a; int main() {c = 2;} int c; void a() {c = 2;}' # should and must fail
            # text = 'int a; int main() {int a = 2;} int c; void a() {c = 2;}'
            # text = 'int k; int main() { int *a = k; }'
            # text = 'int main(void) { if(1) { int a,b; } else { int a = 2; } return 0; }'
            # text = 'int main() {int a[2][2]; int b; b = &a[1];}'
            # text = 'int main(void) { int a = 2; printf("%d", a); }'
            # text = 'int main(void) { int *a; printf("%d", a);}'
            # text = 'int k;  int media(int a, int b) { return 2;} int main(void) { int *a; k = 4; *a = media(a, k);}'
            # text = 'int main(){int *a, *b; scanf("%d%d", &a, &b);}'
            # text = 'int k; int media(int *a, int* b) { return (*a+*b)/2;} int main(void) { int a; k = 4; *a = 2; *a = media(&a, &k);}'
            # text = 'int main(void) { int *a; scanf("%d", &*a); }'
            # text = 'int a(void) { int a = 0; int b = 2; int c = 3; c = a * b; return 2*c/4; }'
            # text = 'int main(void) { int a = 2*3*4; int b = a - 2 - 1; return a; }'
            # text = 'int main(void) { int a[3][2]; a[2][1] = 25; int *b = &a[1]; } '
            # text = 'int main(void) { int a[2][2]; int *b; int c; int d; b = &a[0][0]; c = *b; a[0][0] = *b;  } '
            # text = 'int x; int k, y; int main(void) { int a[2][2]; int *b; a[0][1] = *b; } '
            # text = 'int main(void) { int a[3][2]; int b = a[1][1] + 1; } '
            # text = 'int main() {int a = 3 < 2 || 1; int b = 4 && 4 > 3;}'
            # text = 'int main() {int b = 4 && 4 > 3;}'
            # text = 'int main() {int a = 2; if(1) { int a = 2; } else { int b = 3; } }'
            # text = 'int main() {int a; int b; while(a > 0) { a = a - 1; int b; } int c = 2; }'
            # text = 'int main() {int a; int b; while(a > 0) { a = a - 1; if (1) {int a; int b;} } int c = 10; }'
            # text = 'int main() { if(!1) { printf("HOLA"); } }'
            # text = 'int main() { int a[2][2]; int b = -a[0][1]; }'
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