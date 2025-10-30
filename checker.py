# checker.py
from rich    import print
from typing  import Union, List

from errors  import error, errors_detected
from model   import *
from symtab  import TablaSimbolos
from typesys import check_binop, check_unaryop

class AnalizadorSemantico(Visitor):
    @classmethod
    def ejecutar_analisis(cls, programa: Program):
        instancia_analizador = cls()
        # Crear una nueva tabla de simbolos global
        entorno = TablaSimbolos('global')
        # Visitar todas las declaraciones del programa
        instancia_analizador.visit(programa, entorno)
        return entorno

    # =====================================================================
    # Nodos del Programa y Bloques
    # =====================================================================
    def visit(self, programa: Program, entorno: TablaSimbolos):
        for declaracion in programa.body:
            declaracion.accept(self, entorno)

    def visit(self, bloque: BlockStmt, entorno: TablaSimbolos):
        entorno_bloque = TablaSimbolos('block', padre=entorno)
        for sentencia in bloque.statements:
            sentencia.accept(self, entorno_bloque)

    # =====================================================================
    # Declaraciones
    # =====================================================================
    
    def visit(self, declaracion_variable: VarDecl, entorno: TablaSimbolos):
        # Asignar el tipo PRIMERO
        declaracion_variable.sym_type = declaracion_variable.type.name
        # No se permiten variables de tipo void
        if declaracion_variable.sym_type == 'void':
            error("No se permite declarar variables de tipo 'void'", declaracion_variable.lineno)
        
        if declaracion_variable.value:
            declaracion_variable.value.accept(self, entorno)
            if declaracion_variable.sym_type != declaracion_variable.value.type:
                error(f'Error de tipo en declaración. Se esperaba {declaracion_variable.sym_type} pero se obtuvo {declaracion_variable.value.type}', declaracion_variable.lineno)

        try:
            entorno.agregar(declaracion_variable.name, declaracion_variable)
        except TablaSimbolos.ErrorSimboloDefinido:
            error(f"La Variable '{declaracion_variable.name}' ya ha sido definida en este alcance", declaracion_variable.lineno)

    def visit(self, declaracion_array: ArrayDecl, entorno: TablaSimbolos):
        # El tipo del array ya está en declaracion_array.type (que es un ArrayType)
        declaracion_array.sym_type = declaracion_array.type

        # Los arrays no pueden tener elementos de tipo void (en ninguna profundidad)
        if self._contiene_void(declaracion_array.type):
            error("Los arrays no pueden tener elementos de tipo 'void'", declaracion_array.lineno)

        # Validar recursivamente todos los tamaños de arrays anidados
        self._validar_tamanos_array(declaracion_array.type, entorno, declaracion_array.lineno)

        if declaracion_array.size:
            declaracion_array.size.accept(self, entorno)
            if declaracion_array.size.type != 'integer':
                error(f"El tamaño del array debe ser 'integer', no '{declaracion_array.size.type}'", declaracion_array.lineno)

        if declaracion_array.value:
            for valor in declaracion_array.value:
                valor.accept(self, entorno)
                # Obtener el tipo del elemento (puede ser SimpleType o ArrayType)
                tipo_esperado = self._obtener_nombre_tipo_elemento(declaracion_array.type.element_type)
                if tipo_esperado != valor.type:
                    error(f'Error de tipo en inicializador de array. Se esperaba {tipo_esperado} pero se obtuvo {valor.type}', declaracion_array.lineno)

        try:
            entorno.agregar(declaracion_array.name, declaracion_array)
        except TablaSimbolos.ErrorSimboloDefinido:
            error(f"El Array '{declaracion_array.name}' ya ha sido definido en este alcance", declaracion_array.lineno)

    def _validar_tamanos_array(self, tipo_array, entorno, numero_linea):
        """Valida recursivamente todos los tamaños de arrays anidados"""
        if not isinstance(tipo_array, ArrayType):
            return
        
        # Validar el tamaño de este nivel si existe
        if tipo_array.size:
            tipo_array.size.accept(self, entorno)
            if tipo_array.size.type != 'integer':
                error(f"El tamaño del array debe ser 'integer', no '{tipo_array.size.type}'", numero_linea)
        
        # Recursivamente validar el tipo de elemento si es otro array
        if isinstance(tipo_array.element_type, ArrayType):
            self._validar_tamanos_array(tipo_array.element_type, entorno, numero_linea)
    
    def _obtener_nombre_tipo_elemento(self, tipo):
        """Obtiene el nombre del tipo (maneja SimpleType y ArrayType)"""
        if isinstance(tipo, SimpleType):
            return tipo.name
        elif isinstance(tipo, ArrayType):
            return tipo
        return str(tipo)

    def _contiene_void(self, tipo):
        """Devuelve True si el tipo (simple o anidado) contiene 'void' como base."""
        if isinstance(tipo, SimpleType):
            return tipo.name == 'void'
        if isinstance(tipo, ArrayType):
            return self._contiene_void(tipo.element_type)
        return False

    def visit(self, declaracion_funcion: FuncDecl, entorno: TablaSimbolos):
        # Asignar el tipo de retorno de la función
        declaracion_funcion.sym_type = declaracion_funcion.type.name
        
        try:
            entorno.agregar(declaracion_funcion.name, declaracion_funcion)
        except TablaSimbolos.ErrorSimboloDefinido:
            error(f"La Función '{declaracion_funcion.name}' ya ha sido definida", declaracion_funcion.lineno)
            return  # No continuar si hay error de redefinición

        # Crear entorno local para la función
        entorno_funcion = TablaSimbolos(declaracion_funcion.name, padre=entorno)
        entorno_funcion.agregar('$func', declaracion_funcion)
        
        # Procesar parámetros
        for parametro in declaracion_funcion.params:
            parametro.accept(self, entorno_funcion)
        
        # Procesar cuerpo
        if declaracion_funcion.body:
            declaracion_funcion.body.accept(self, entorno_funcion)

    def visit(self, parametro: Param, entorno: TablaSimbolos):
        # Determinar el tipo del parámetro
        if isinstance(parametro.type, SimpleType):
            parametro.sym_type = parametro.type.name
        elif isinstance(parametro.type, ArrayType):
            parametro.sym_type = parametro.type
            # Validar tamaños de arrays en parámetros
            self._validar_tamanos_array(parametro.type, entorno, parametro.lineno)
        
        try:
            entorno.agregar(parametro.name, parametro)
        except TablaSimbolos.ErrorSimboloDefinido:
            error(f"El Parámetro '{parametro.name}' ya está definido", parametro.lineno)

    # =====================================================================
    # Sentencias
    # =====================================================================
    
    def visit(self, sentencia_print: PrintStmt, entorno: TablaSimbolos):
        for valor in sentencia_print.values:
            valor.accept(self, entorno)

    def visit(self, sentencia_return: ReturnStmt, entorno: TablaSimbolos):
        declaracion_funcion = entorno.obtener('$func')
        if not declaracion_funcion:
            error("'return' utilizado por fuera de una función", sentencia_return.lineno)
            return
        
        tipo_esperado = declaracion_funcion.sym_type
        
        if sentencia_return.value:
            sentencia_return.value.accept(self, entorno)
            if tipo_esperado == 'void':
                error(f"La función '{declaracion_funcion.name}' no debería retornar un valor", sentencia_return.lineno)
            elif tipo_esperado != sentencia_return.value.type:
                error(f"Error de tipo. Se esperaba un retorno de tipo '{tipo_esperado}' pero se obtuvo '{sentencia_return.value.type}'", sentencia_return.lineno)
        else:
            if tipo_esperado != 'void':
                error(f"La función '{declaracion_funcion.name}' debe retornar un valor de tipo '{tipo_esperado}'", sentencia_return.lineno)

    def visit(self, sentencia_if: IfStmt, entorno: TablaSimbolos):
        sentencia_if.condition.accept(self, entorno)
        if sentencia_if.condition.type != 'boolean':
            error(f"La condición en IF debe ser 'boolean', no '{sentencia_if.condition.type}'", sentencia_if.lineno)
        
        sentencia_if.true_body.accept(self, entorno)
        if sentencia_if.false_body:
            sentencia_if.false_body.accept(self, entorno)

    def visit(self, sentencia_for: ForStmt, entorno: TablaSimbolos):
        entorno_bucle = TablaSimbolos('for_loop', padre=entorno)
        entorno_bucle.agregar('$loop', True)
        
        if sentencia_for.init: 
            sentencia_for.init.accept(self, entorno_bucle)
        
        if sentencia_for.condition:
            sentencia_for.condition.accept(self, entorno_bucle)
            if sentencia_for.condition.type != 'boolean':
                error(f"La condición en FOR debe ser 'boolean', no '{sentencia_for.condition.type}'", sentencia_for.lineno)
        
        if sentencia_for.update: 
            sentencia_for.update.accept(self, entorno_bucle)
        
        sentencia_for.body.accept(self, entorno_bucle)
    
    def visit(self, sentencia_while: WhileStmt, entorno: TablaSimbolos):
        sentencia_while.condition.accept(self, entorno)
        if sentencia_while.condition.type != 'boolean':
            error(f"La condición en WHILE debe ser 'boolean', no '{sentencia_while.condition.type}'", sentencia_while.lineno)
        
        entorno_bucle = TablaSimbolos('while_loop', padre=entorno)
        entorno_bucle.agregar('$loop', True)
        sentencia_while.body.accept(self, entorno_bucle)

    def visit(self, sentencia_dowhile: DoWhileStmt, entorno: TablaSimbolos):
        entorno_bucle = TablaSimbolos('dowhile_loop', padre=entorno)
        entorno_bucle.agregar('$loop', True)
        sentencia_dowhile.body.accept(self, entorno_bucle)
        
        sentencia_dowhile.condition.accept(self, entorno_bucle)
        if sentencia_dowhile.condition.type != 'boolean':
            error(f"La condición en DO-WHILE debe ser 'boolean', no '{sentencia_dowhile.condition.type}'", sentencia_dowhile.lineno)

    # =====================================================================
    # Expresiones
    # =====================================================================
    
    def visit(self, asignacion: Assignment, entorno: TablaSimbolos):
        asignacion.location.accept(self, entorno)
        asignacion.value.accept(self, entorno)

        if asignacion.location.type != asignacion.value.type:
            error(f'Error de tipo en asignación. No se puede asignar {asignacion.value.type} a {asignacion.location.type}', asignacion.lineno)
        
        if not getattr(asignacion.location, 'mutable', False):
            error(f"El destino de la asignación no es modificable", asignacion.lineno)

    def visit(self, operacion_binaria: BinOper, entorno: TablaSimbolos):
        operacion_binaria.left.accept(self, entorno)
        operacion_binaria.right.accept(self, entorno)
        
        operacion_binaria.type = check_binop(operacion_binaria.op, operacion_binaria.left.type, operacion_binaria.right.type) 
        if not operacion_binaria.type:
            error(f'Operación inválida: {operacion_binaria.left.type} {operacion_binaria.op} {operacion_binaria.right.type}', operacion_binaria.lineno)
            operacion_binaria.type = 'error'

    def visit(self, operacion_unaria: UnaryOper, entorno: TablaSimbolos):
        operacion_unaria.expr.accept(self, entorno)
        
        # Operadores unarios normales (-, !, +)
        if operacion_unaria.__class__ is UnaryOper:
            operacion_unaria.type = check_unaryop(operacion_unaria.op, operacion_unaria.expr.type)
            if not operacion_unaria.type:
                error(f'Operación unaria inválida: {operacion_unaria.op} {operacion_unaria.expr.type}', operacion_unaria.lineno)
                operacion_unaria.type = 'error'
        # Operadores de incremento/decremento (++, --)
        else:
            if operacion_unaria.expr.type not in ('integer', 'float'):
                error(f"Operador '{operacion_unaria.op}' solo aplicable a 'integer' o 'float', no a '{operacion_unaria.expr.type}'", operacion_unaria.lineno)
            if not getattr(operacion_unaria.expr, 'mutable', False):
                error(f"El operando de '{operacion_unaria.op}' debe ser una ubicación modificable", operacion_unaria.lineno)
            operacion_unaria.type = operacion_unaria.expr.type

    def visit(self, literal: Literal, entorno: TablaSimbolos):
        if isinstance(literal, Integer): 
            literal.type = 'integer'
        elif isinstance(literal, Float): 
            literal.type = 'float'
        elif isinstance(literal, Boolean): 
            literal.type = 'boolean'
        elif isinstance(literal, Char): 
            literal.type = 'char'
        elif isinstance(literal, String): 
            literal.type = 'string'

    def visit(self, ubicacion_variable: VarLocation, entorno: TablaSimbolos):
        declaracion = entorno.obtener(ubicacion_variable.name)
        if not declaracion:
            error(f"Nombre no definido '{ubicacion_variable.name}'", ubicacion_variable.lineno)
            ubicacion_variable.type = 'error'
            ubicacion_variable.mutable = False
        else:
            ubicacion_variable.type = declaracion.sym_type
            # Las funciones no son mutables, las variables sí
            ubicacion_variable.mutable = not isinstance(declaracion, FuncDecl)
    
    def visit(self, subindice_array: ArraySubscript, entorno: TablaSimbolos):
        subindice_array.location.accept(self, entorno)
        subindice_array.index.accept(self, entorno)

        # Verificar que location es un array
        if not isinstance(subindice_array.location.type, ArrayType):
            error("El operador de subíndice '[]' solo se puede usar en arrays", subindice_array.lineno)
            subindice_array.type = 'error'
            subindice_array.mutable = False
            return

        # Verificar que el índice es entero
        if subindice_array.index.type != 'integer':
            error(f"El índice del array debe ser 'integer', no '{subindice_array.index.type}'", subindice_array.lineno)
        
        # El tipo del resultado es el tipo de elemento del array
        # Puede ser SimpleType o ArrayType (para arrays anidados)
        tipo_elemento = subindice_array.location.type.element_type
        if isinstance(tipo_elemento, SimpleType):
            subindice_array.type = tipo_elemento.name
        elif isinstance(tipo_elemento, ArrayType):
            subindice_array.type = tipo_elemento  # Array anidado
        else:
            subindice_array.type = tipo_elemento
        
        subindice_array.mutable = True

    def visit(self, llamada_funcion: FuncCall, entorno: TablaSimbolos):
        declaracion_funcion = entorno.obtener(llamada_funcion.name)
        if not declaracion_funcion:
            error(f"Función '{llamada_funcion.name}' no definida", llamada_funcion.lineno)
            llamada_funcion.type = 'error'
            return
        
        if not isinstance(declaracion_funcion, FuncDecl):
            error(f"'{llamada_funcion.name}' no es una función, no se puede llamar", llamada_funcion.lineno)
            llamada_funcion.type = 'error'
            return

        # Verificar número de argumentos
        if len(llamada_funcion.args) != len(declaracion_funcion.params):
            error(f"La función '{llamada_funcion.name}' esperaba {len(declaracion_funcion.params)} argumentos, pero se recibieron {len(llamada_funcion.args)}", llamada_funcion.lineno)
        
        # Verificar tipo de cada argumento
        for i, (argumento, parametro) in enumerate(zip(llamada_funcion.args, declaracion_funcion.params)):
            argumento.accept(self, entorno)
            
            # Obtener el tipo esperado del parámetro
            if isinstance(parametro.type, SimpleType):
                tipo_esperado = parametro.type.name
            elif isinstance(parametro.type, ArrayType):
                tipo_esperado = parametro.type
            
            # Comparar tipos
            if isinstance(tipo_esperado, str):
                # Tipo simple
                if argumento.type != tipo_esperado:
                    error(f"Error de tipo en argumento {i+1} de '{llamada_funcion.name}'. Se esperaba '{tipo_esperado}' pero se obtuvo '{argumento.type}'", llamada_funcion.lineno)
            elif isinstance(tipo_esperado, ArrayType):
                # Tipo array
                if not isinstance(argumento.type, ArrayType):
                    error(f"Error de tipo en argumento {i+1} de '{llamada_funcion.name}'. Se esperaba un array pero se obtuvo '{argumento.type}'", llamada_funcion.lineno)
                elif argumento.type.element_type.name != tipo_esperado.element_type.name:
                    error(f"Error de tipo en argumento {i+1} de '{llamada_funcion.name}'. Se esperaba array[{tipo_esperado.element_type.name}] pero se obtuvo array[{argumento.type.element_type.name}]", llamada_funcion.lineno)

        # El tipo de la expresión es el tipo de retorno de la función
        llamada_funcion.type = declaracion_funcion.sym_type