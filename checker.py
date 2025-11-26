# checker.py
from rich    import print
from typing  import Union, List

from errors  import error, errors_detected
from model   import *
from symtab  import SymbolTable
from typesys import check_binop, check_unaryop

class SemanticAnalyzer(Visitor):
    @classmethod
    def checker(cls, program_node: Program):
        analyzer = cls()
        # Inicializar tabla de simbolos global
        global_symbols = SymbolTable('global')
        # Registrar funciones built-in
        analyzer._register_builtins(global_symbols)
        # Procesar todas las declaraciones del programa
        analyzer.visit(program_node, global_symbols)
        return global_symbols
    
    def _register_builtins(self, symbol_table: SymbolTable):
        """Registra las funciones built-in en la tabla de simbolos"""
        # read_integer: function integer () = {}
        read_integer_decl = FuncDecl(
            name='read_integer',
            type=SimpleType('integer'),
            params=[],
            body=None
        )
        read_integer_decl.sym_type = 'integer'
        symbol_table.symbols['read_integer'] = read_integer_decl
        
        # read_string: function string () = {}
        read_string_decl = FuncDecl(
            name='read_string',
            type=SimpleType('string'),
            params=[],
            body=None
        )
        read_string_decl.sym_type = 'string'
        symbol_table.symbols['read_string'] = read_string_decl
        
        # sqrt: function float (x: float) = {}
        sqrt_decl = FuncDecl(
            name='sqrt',
            type=SimpleType('float'),
            params=[Param('x', SimpleType('float'))],
            body=None
        )
        sqrt_decl.sym_type = 'float'
        symbol_table.symbols['sqrt'] = sqrt_decl
        
        # abs: function float (x: float) = {}
        abs_decl = FuncDecl(
            name='abs',
            type=SimpleType('float'),
            params=[Param('x', SimpleType('float'))],
            body=None
        )
        abs_decl.sym_type = 'float'
        symbol_table.symbols['abs'] = abs_decl
        
        # max: function float (a: float, b: float) = {}
        max_decl = FuncDecl(
            name='max',
            type=SimpleType('float'),
            params=[Param('a', SimpleType('float')), Param('b', SimpleType('float'))],
            body=None
        )
        max_decl.sym_type = 'float'
        symbol_table.symbols['max'] = max_decl
        
        # min: function float (a: float, b: float) = {}
        min_decl = FuncDecl(
            name='min',
            type=SimpleType('float'),
            params=[Param('a', SimpleType('float')), Param('b', SimpleType('float'))],
            body=None
        )
        min_decl.sym_type = 'float'
        symbol_table.symbols['min'] = min_decl
        
        # length: function integer (arr: array [] integer) = {}
        # Nota: length acepta arrays o strings, pero para el checker usamos array como base
        length_decl = FuncDecl(
            name='length',
            type=SimpleType('integer'),
            params=[Param('arr', ArrayType(SimpleType('integer')))],
            body=None
        )
        length_decl.sym_type = 'integer'
        symbol_table.symbols['length'] = length_decl

    # =====================================================================
    # Procesamiento de Programa y Bloques
    # =====================================================================
    def visit(self, program_node: Program, symbol_table: SymbolTable):
        for declaration in program_node.body:
            declaration.accept(self, symbol_table)

    def visit(self, block_node: BlockStmt, symbol_table: SymbolTable):
        local_symbols = SymbolTable('block', parent_table=symbol_table)
        for statement in block_node.statements:
            statement.accept(self, local_symbols)

    # =====================================================================
    # Declaraciones
    # =====================================================================
    
    def visit(self, n: VarDecl, env: SymbolTable):
        # Asignar el tipo PRIMERO
        n.sym_type = n.type.name
        
        if n.value:
            n.value.accept(self, env)
            if n.sym_type != n.value.type:
                error(f'Error de tipo en declaración. Se esperaba {n.sym_type} pero se obtuvo {n.value.type}', n.lineno)

        try:
            env.add(n.name, n)
        except SymbolTable.DuplicateSymbolError:
            error(f"La Variable '{n.name}' ya ha sido definida en este alcance", n.lineno)
        except SymbolTable.TypeConflictError:
            error(f"Conflicto de tipos: La Variable '{n.name}' ya existe con un tipo diferente", n.lineno)

    def visit(self, n: ArrayDecl, env: SymbolTable):
        # El tipo del array ya está en n.type (que es un ArrayType)
        n.sym_type = n.type

        # Validar recursivamente todos los tamaños de arrays anidados
        self._check_array_sizes(n.type, env, n.lineno)

        if n.size:
            n.size.accept(self, env)
            if n.size.type != 'integer':
                error(f"El tamaño del array debe ser 'integer', no '{n.size.type}'", n.lineno)

        if n.value:
            for val in n.value:
                val.accept(self, env)
                # Obtener el tipo del elemento (puede ser SimpleType o ArrayType)
                expected_type = self._get_element_type_name(n.type.element_type)
                if expected_type != val.type:
                    error(f'Error de tipo en inicializador de array. Se esperaba {expected_type} pero se obtuvo {val.type}', n.lineno)

        try:
            env.add(n.name, n)
        except SymbolTable.DuplicateSymbolError:
            error(f"El Array '{n.name}' ya ha sido definido en este alcance", n.lineno)

    def _check_array_sizes(self, array_type, env, lineno):
        """Valida recursivamente todos los tamaños de arrays anidados"""
        if not isinstance(array_type, ArrayType):
            return
        
        # Validar el tamaño de este nivel si existe
        if array_type.size:
            array_type.size.accept(self, env)
            if array_type.size.type != 'integer':
                error(f"El tamaño del array debe ser 'integer', no '{array_type.size.type}'", lineno)
        
        # Recursivamente validar el tipo de elemento si es otro array
        if isinstance(array_type.element_type, ArrayType):
            self._check_array_sizes(array_type.element_type, env, lineno)
    
    def _get_element_type_name(self, typ):
        """Obtiene el nombre del tipo (maneja SimpleType y ArrayType)"""
        if isinstance(typ, SimpleType):
            return typ.name
        elif isinstance(typ, ArrayType):
            return typ
        return str(typ)

    def visit(self, n: FuncDecl, env: SymbolTable):
        # Asignar el tipo de retorno de la función
        n.sym_type = n.type.name
        
        try:
            env.add(n.name, n)
        except SymbolTable.DuplicateSymbolError:
            error(f"La Función '{n.name}' ya ha sido definida", n.lineno)
            return  # No continuar si hay error de redefinición

        # Crear entorno local para la función
        func_env = SymbolTable(n.name, parent_table=env)
        func_env.add('$func', n)
        
        # Procesar parámetros
        for p in n.params:
            p.accept(self, func_env)
        
        # Procesar cuerpo
        if n.body:
            n.body.accept(self, func_env)

    def visit(self, n: Param, env: SymbolTable):
        # Determinar el tipo del parámetro
        if isinstance(n.type, SimpleType):
            n.sym_type = n.type.name
        elif isinstance(n.type, ArrayType):
            n.sym_type = n.type
            # Validar tamaños de arrays en parámetros
            self._check_array_sizes(n.type, env, n.lineno)
        
        try:
            env.add(n.name, n)
        except SymbolTable.DuplicateSymbolError:
            error(f"El Parámetro '{n.name}' ya está definido", n.lineno)

    # =====================================================================
    # Sentencias
    # =====================================================================
    
    def visit(self, n: PrintStmt, env: SymbolTable):
        for value in n.values:
            value.accept(self, env)

    def visit(self, n: ReturnStmt, env: SymbolTable):
        func_decl = env.get('$func')
        if not func_decl:
            error("'return' utilizado por fuera de una función", n.lineno)
            return
        
        expected_type = func_decl.sym_type
        
        if n.value:
            n.value.accept(self, env)
            if expected_type == 'void':
                error(f"La función '{func_decl.name}' no debería retornar un valor", n.lineno)
            elif expected_type != n.value.type:
                error(f"Error de tipo. Se esperaba un retorno de tipo '{expected_type}' pero se obtuvo '{n.value.type}'", n.lineno)
        else:
            if expected_type != 'void':
                error(f"La función '{func_decl.name}' debe retornar un valor de tipo '{expected_type}'", n.lineno)

    def visit(self, n: IfStmt, env: SymbolTable):
        n.condition.accept(self, env)
        if n.condition.type != 'boolean':
            error(f"La condición en IF debe ser 'boolean', no '{n.condition.type}'", n.lineno)
        
        n.true_body.accept(self, env)
        if n.false_body:
            n.false_body.accept(self, env)

    def visit(self, n: ForStmt, env: SymbolTable):
        loop_env = SymbolTable('for_loop', parent_table=env)
        loop_env.add('$loop', True)
        
        if n.init: 
            n.init.accept(self, loop_env)
        
        if n.condition:
            n.condition.accept(self, loop_env)
            if n.condition.type != 'boolean':
                error(f"La condición en FOR debe ser 'boolean', no '{n.condition.type}'", n.lineno)
        
        if n.update: 
            n.update.accept(self, loop_env)
        
        n.body.accept(self, loop_env)
    
    def visit(self, n: WhileStmt, env: SymbolTable):
        n.condition.accept(self, env)
        if n.condition.type != 'boolean':
            error(f"La condición en WHILE debe ser 'boolean', no '{n.condition.type}'", n.lineno)
        
        loop_env = SymbolTable('while_loop', parent_table=env)
        loop_env.add('$loop', True)
        n.body.accept(self, loop_env)

    def visit(self, n: DoWhileStmt, env: SymbolTable):
        loop_env = SymbolTable('dowhile_loop', parent_table=env)
        loop_env.add('$loop', True)
        n.body.accept(self, loop_env)
        
        n.condition.accept(self, loop_env)
        if n.condition.type != 'boolean':
            error(f"La condición en DO-WHILE debe ser 'boolean', no '{n.condition.type}'", n.lineno)

    # =====================================================================
    # Expresiones
    # =====================================================================
    
    def visit(self, n: Assignment, env: SymbolTable):
        n.location.accept(self, env)
        n.value.accept(self, env)

        if n.location.type != n.value.type:
            error(f'Error de tipo en asignación. No se puede asignar {n.value.type} a {n.location.type}', n.lineno)
        
        if not getattr(n.location, 'mutable', False):
            error(f"El destino de la asignación no es modificable", n.lineno)

    def visit(self, n: BinOper, env: SymbolTable):
        n.left.accept(self, env)
        n.right.accept(self, env)
        
        n.type = check_binop(n.op, n.left.type, n.right.type) 
        if not n.type:
            error(f'Operación inválida: {n.left.type} {n.op} {n.right.type}', n.lineno)
            n.type = 'error'

    def visit(self, n: UnaryOper, env: SymbolTable):
        n.expr.accept(self, env)
        
        # Operadores unarios normales (-, !, +)
        if n.__class__ is UnaryOper:
            n.type = check_unaryop(n.op, n.expr.type)
            if not n.type:
                error(f'Operación unaria inválida: {n.op} {n.expr.type}', n.lineno)
                n.type = 'error'
        # Operadores de incremento/decremento (++, --)
        else:
            if n.expr.type not in ('integer', 'float'):
                error(f"Operador '{n.op}' solo aplicable a 'integer' o 'float', no a '{n.expr.type}'", n.lineno)
            if not getattr(n.expr, 'mutable', False):
                error(f"El operando de '{n.op}' debe ser una ubicación modificable", n.lineno)
            n.type = n.expr.type

    def visit(self, n: Literal, env: SymbolTable):
        if isinstance(n, Integer): 
            n.type = 'integer'
        elif isinstance(n, Float): 
            n.type = 'float'
        elif isinstance(n, Boolean): 
            n.type = 'boolean'
        elif isinstance(n, Char): 
            n.type = 'char'
        elif isinstance(n, String): 
            n.type = 'string'

    def visit(self, n: VarLocation, env: SymbolTable):
        decl = env.get(n.name)
        if not decl:
            error(f"Nombre no definido '{n.name}'", n.lineno)
            n.type = 'error'
            n.mutable = False
        else:
            n.type = decl.sym_type
            # Las funciones no son mutables, las variables sí
            n.mutable = not isinstance(decl, FuncDecl)
    
    def visit(self, n: ArraySubscript, env: SymbolTable):
        n.location.accept(self, env)
        n.index.accept(self, env)

        # Verificar que location es un array
        if not isinstance(n.location.type, ArrayType):
            error("El operador de subíndice '[]' solo se puede usar en arrays", n.lineno)
            n.type = 'error'
            n.mutable = False
            return

        # Verificar que el índice es entero
        if n.index.type != 'integer':
            error(f"El índice del array debe ser 'integer', no '{n.index.type}'", n.lineno)
        
        # El tipo del resultado es el tipo de elemento del array
        # Puede ser SimpleType o ArrayType (para arrays anidados)
        element_type = n.location.type.element_type
        if isinstance(element_type, SimpleType):
            n.type = element_type.name
        elif isinstance(element_type, ArrayType):
            n.type = element_type  # Array anidado
        else:
            n.type = element_type
        
        n.mutable = True

    def visit(self, n: FuncCall, env: SymbolTable):
        func_decl = env.get(n.name)
        if not func_decl:
            error(f"Función '{n.name}' no definida", n.lineno)
            n.type = 'error'
            return
        
        if not isinstance(func_decl, FuncDecl):
            error(f"'{n.name}' no es una función, no se puede llamar", n.lineno)
            n.type = 'error'
            return

        # Verificar número de argumentos
        if len(n.args) != len(func_decl.params):
            error(f"La función '{n.name}' esperaba {len(func_decl.params)} argumentos, pero se recibieron {len(n.args)}", n.lineno)
        
        # Verificar tipo de cada argumento
        for i, (arg, param) in enumerate(zip(n.args, func_decl.params)):
            arg.accept(self, env)
            
            # Obtener el tipo esperado del parámetro
            if isinstance(param.type, SimpleType):
                expected_type = param.type.name
            elif isinstance(param.type, ArrayType):
                expected_type = param.type
            
            # Comparar tipos
            if isinstance(expected_type, str):
                # Tipo simple
                if arg.type != expected_type:
                    error(f"Error de tipo en argumento {i+1} de '{n.name}'. Se esperaba '{expected_type}' pero se obtuvo '{arg.type}'", n.lineno)
            elif isinstance(expected_type, ArrayType):
                # Tipo array
                if not isinstance(arg.type, ArrayType):
                    error(f"Error de tipo en argumento {i+1} de '{n.name}'. Se esperaba un array pero se obtuvo '{arg.type}'", n.lineno)
                elif arg.type.element_type.name != expected_type.element_type.name:
                    error(f"Error de tipo en argumento {i+1} de '{n.name}'. Se esperaba array[{expected_type.element_type.name}] pero se obtuvo array[{arg.type.element_type.name}]", n.lineno)

        # El tipo de la expresión es el tipo de retorno de la función
        n.type = func_decl.sym_type