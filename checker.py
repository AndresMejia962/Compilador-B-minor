# checker.py
from rich    import print
from typing  import Union, List

from errors  import error, errors_detected
from model   import *
from symtab  import Symtab
from typesys import check_binop, check_unaryop

class Check(Visitor):
    @classmethod
    def checker(cls, n: Program):
        checker_instance = cls()
        # Crear una nueva tabla de simbolos global
        env = Symtab('global')
        # Visitar todas las declaraciones del programa
        checker_instance.visit(n, env)
        return env

    # =====================================================================
    # Nodos del Programa y Bloques
    # =====================================================================
    def visit(self, n: Program, env: Symtab):
        for decl in n.body:
            decl.accept(self, env)

    def visit(self, n: BlockStmt, env: Symtab):
        block_env = Symtab('block', parent=env)
        for stmt in n.statements:
            stmt.accept(self, block_env)

    # =====================================================================
    # Declaraciones
    # =====================================================================
    
    def visit(self, n: VarDecl, env: Symtab):
        if n.value:
            n.value.accept(self, env)
            if n.type.name != n.value.type:
                error(f'Error de tipo en declaración. Se esperaba {n.type.name} pero se obtuvo {n.value.type}', n.lineno)

        try:
            n.sym_type = n.type.name
            env.add(n.name, n)
        except Symtab.SymbolDefinedError:
            error(f"La Variable '{n.name}' ya ha sido definida en este alcance", n.lineno)

    def visit(self, n: ArrayDecl, env: Symtab):
        # El tipo del array es el tipo de sus elementos
        n.sym_type = ArrayType(element_type=n.type.element_type)

        if n.size:
            n.size.accept(self, env)
            if n.size.type != 'integer':
                error(f"El tamaño del array debe ser 'integer', no '{n.size.type}'", n.lineno)

        if n.value:
            for val in n.value:
                val.accept(self, env)
                if n.type.element_type.name != val.type:
                    error(f'Error de tipo en inicializador de array. Se esperaba {n.type.element_type.name} pero se obtuvo {val.type}', n.lineno)

        try:
            env.add(n.name, n)
        except Symtab.SymbolDefinedError:
            error(f"El Array '{n.name}' ya ha sido definido en este alcance", n.lineno)

    def visit(self, n: FuncDecl, env: Symtab):
        try:
            n.sym_type = n.type.name
            env.add(n.name, n)
        except Symtab.SymbolDefinedError:
            error(f"La Función '{n.name}' ya ha sido definida", n.lineno)

        func_env = Symtab(n.name, parent=env)
        func_env.add('$func', n)
        
        for p in n.params:
            p.accept(self, func_env)
        
        if n.body:
            n.body.accept(self, func_env)

    def visit(self, n: Param, env: Symtab):
        try:
            if isinstance(n.type, SimpleType):
                n.sym_type = n.type.name
            elif isinstance(n.type, ArrayType):
                n.sym_type = n.type
            env.add(n.name, n)
        except Symtab.SymbolDefinedError:
            error(f"El Parámetro '{n.name}' ya está definido", n.lineno)

    # =====================================================================
    # Sentencias
    # =====================================================================
    
    def visit(self, n: PrintStmt, env: Symtab):
        for value in n.values:
            value.accept(self, env)

    def visit(self, n: ReturnStmt, env: Symtab):
        func_decl = env.get('$func')
        if not func_decl:
            error("'return' utilizado por fuera de una función", n.lineno)
            return
        
        expected_type = func_decl.sym_type
        
        if n.value:
            n.value.accept(self, env)
            if expected_type == 'void':
                error(f"La función '{func_decl.name}' no debería retornar un valor", n.lineno)
            elif expected_type != n.value.type:
                error(f"Error de tipo. Se esperaba un retorno de tipo '{expected_type}' pero se obtuvo '{n.value.type}'", n.lineno)
        else:
            if expected_type != 'void':
                error(f"La función '{func_decl.name}' debe retornar un valor de tipo '{expected_type}'", n.lineno)

    def visit(self, n: IfStmt, env: Symtab):
        n.condition.accept(self, env)
        if n.condition.type != 'boolean':
            error(f"La condición en IF debe ser 'boolean', no '{n.condition.type}'", n.lineno)
        
        n.true_body.accept(self, env)
        if n.false_body:
            n.false_body.accept(self, env)

    def visit(self, n: ForStmt, env: Symtab):
        loop_env = Symtab('for_loop', parent=env)
        loop_env.add('$loop', True)
        
        if n.init: n.init.accept(self, loop_env)
        
        if n.condition:
            n.condition.accept(self, loop_env)
            if n.condition.type != 'boolean':
                error(f"La condición en FOR debe ser 'boolean', no '{n.condition.type}'", n.lineno)
        
        if n.update: n.update.accept(self, loop_env)
        
        n.body.accept(self, loop_env)
    
    def visit(self, n: WhileStmt, env: Symtab):
        n.condition.accept(self, env)
        if n.condition.type != 'boolean':
            error(f"La condición en WHILE debe ser 'boolean', no '{n.condition.type}'", n.lineno)
        
        loop_env = Symtab('while_loop', parent=env)
        loop_env.add('$loop', True)
        n.body.accept(self, loop_env)

    def visit(self, n: DoWhileStmt, env: Symtab):
        loop_env = Symtab('dowhile_loop', parent=env)
        loop_env.add('$loop', True)
        n.body.accept(self, loop_env)
        
        n.condition.accept(self, loop_env)
        if n.condition.type != 'boolean':
            error(f"La condición en DO-WHILE debe ser 'boolean', no '{n.condition.type}'", n.lineno)

    # =====================================================================
    # Expresiones
    # =====================================================================
    
    def visit(self, n: Assignment, env: Symtab):
        n.location.accept(self, env)
        n.value.accept(self, env)

        if n.location.type != n.value.type:
            error(f'Error de tipo en asignación. No se puede asignar {n.value.type} a {n.location.type}', n.lineno)
        
        if not getattr(n.location, 'mutable', False):
            error(f"El destino de la asignación no es modificable", n.lineno)

    def visit(self, n: BinOper, env: Symtab):
        n.left.accept(self, env)
        n.right.accept(self, env)
        
        n.type = check_binop(n.op, n.left.type, n.right.type) 
        if not n.type:
            error(f'Operación inválida: {n.left.type} {n.op} {n.right.type}', n.lineno)
            n.type = 'error'

    def visit(self, n: UnaryOper, env: Symtab):
        n.expr.accept(self, env)
        if n.__class__ is UnaryOper:
            n.type = check_unaryop(n.op, n.expr.type)
            if not n.type:
                error(f'Operación unaria inválida: {n.op} {n.expr.type}', n.lineno)
                n.type = 'error'
        else:
            if n.expr.type not in ('integer', 'float'):
                error(f"Operador '{n.op}' solo aplicable a 'integer' o 'float', no a '{n.expr.type}'", n.lineno)
            if not getattr(n.expr, 'mutable', False):
                 error(f"El operando de '{n.op}' debe ser una ubicación modificable", n.lineno)
            n.type = n.expr.type

    def visit(self, n: Literal, env: Symtab):
        if isinstance(n, Integer): n.type = 'integer'
        elif isinstance(n, Float): n.type = 'float'
        elif isinstance(n, Boolean): n.type = 'boolean'
        elif isinstance(n, Char): n.type = 'char'
        elif isinstance(n, String): n.type = 'string'

    def visit(self, n: VarLocation, env: Symtab):
        decl = env.get(n.name)
        if not decl:
            error(f"Nombre no definido '{n.name}'", n.lineno)
            n.type = 'error'
        else:
            n.type = decl.sym_type
            n.mutable = not isinstance(decl, FuncDecl)
    
    def visit(self, n: ArraySubscript, env: Symtab):
        n.location.accept(self, env)
        n.index.accept(self, env)

        if not isinstance(n.location.type, ArrayType):
            error("El operador de subíndice '[]' solo se puede usar en arrays", n.lineno)
            n.type = 'error'
            return

        if n.index.type != 'integer':
            error(f"El índice del array debe ser 'integer', no '{n.index.type}'", n.lineno)
        
        n.type = n.location.type.element_type.name
        n.mutable = True

    def visit(self, n: FuncCall, env: Symtab):
        func_decl = env.get(n.name)
        if not func_decl:
            error(f"Función '{n.name}' no definida", n.lineno)
            n.type = 'error'
            return
        
        if not isinstance(func_decl, FuncDecl):
            error(f"'{n.name}' no es una función, no se puede llamar", n.lineno)
            n.type = 'error'
            return

        if len(n.args) != len(func_decl.params):
            error(f"La función '{n.name}' esperaba {len(func_decl.params)} argumentos, pero se recibieron {len(n.args)}", n.lineno)
        
        for i, (arg, param) in enumerate(zip(n.args, func_decl.params)):
            arg.accept(self, env)
            expected_type = param.type.name if isinstance(param.type, SimpleType) else param.type
            
            if type(arg.type) != type(expected_type) or (isinstance(arg.type, str) and arg.type != expected_type):
                 error(f"Error de tipo en argumento {i+1} de '{n.name}'. Se esperaba '{expected_type.name if hasattr(expected_type,'name') else 'array'}' pero se obtuvo '{arg.type}'", n.lineno)

        n.type = func_decl.sym_type