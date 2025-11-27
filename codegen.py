import llvmlite.ir as ir
import llvmlite.binding as llvm
from model import *

class IRGenerator(Visitor):
    def __init__(self):
        # Crear módulo
        self.llvm_module = ir.Module(name="bminor_module")
        self.llvm_module.triple = llvm.get_default_triple()
        
        # Tipos básicos
        self.tipo_entero = ir.IntType(64)
        self.tipo_flotante = ir.DoubleType()
        self.tipo_booleano = ir.IntType(1)
        self.tipo_caracter = ir.IntType(8)
        self.tipo_void = ir.VoidType()
        
        # Estado
        self.builder = None
        self.constructor_ir = None  # IRBuilder - se inicializa cuando se visita una función
        self.funcion_actual = None
        self.variables = {} # Mapa de nombre -> puntero (alloca) para variables locales
        self.global_variables = {} # Mapa de nombre -> ir.GlobalVariable para variables globales
        self.funciones_llvm = {} # Mapa de nombre -> ir.Function
        self.static_array_sizes = {} # Mapa de nombre -> tamaño constante para arrays estáticos
        self.contador_cadenas = 0
        
        # Mapeo de tipos B-Minor a LLVM
        self.mapeo_tipos = {
            'integer': self.tipo_entero,
            'float': self.tipo_flotante,
            'boolean': self.tipo_booleano,
            'char': self.tipo_caracter,
            'void': self.tipo_void,
            'string': ir.PointerType(self.tipo_caracter)
        }

        # Declarar funciones externas (runtime)
        self._declarar_runtime()

    def _declarar_runtime(self):
        # Funciones de impresión
        # void print_integer(integer)
        f_type = ir.FunctionType(self.tipo_void, [self.tipo_entero])
        self._print_integer = ir.Function(self.llvm_module, f_type, name="print_integer")
        
        # void print_float(float)
        f_type = ir.FunctionType(self.tipo_void, [self.tipo_flotante])
        self._print_float = ir.Function(self.llvm_module, f_type, name="print_float")
        
        # void print_boolean(boolean)
        f_type = ir.FunctionType(self.tipo_void, [self.tipo_booleano])
        self._print_boolean = ir.Function(self.llvm_module, f_type, name="print_boolean")
        
        # void print_char(char)
        f_type = ir.FunctionType(self.tipo_void, [self.tipo_caracter])
        self._print_char = ir.Function(self.llvm_module, f_type, name="print_char")
        
        # void print_string(string)
        f_type = ir.FunctionType(self.tipo_void, [ir.PointerType(self.tipo_caracter)])
        self._print_string = ir.Function(self.llvm_module, f_type, name="print_string")
        
        # Funciones de entrada
        # long long read_integer()
        f_type = ir.FunctionType(self.tipo_entero, [])
        self._read_integer = ir.Function(self.llvm_module, f_type, name="read_integer")
        
        # double read_float()
        f_type = ir.FunctionType(self.tipo_flotante, [])
        self._read_float = ir.Function(self.llvm_module, f_type, name="read_float")
        
        # void read_string(char* buffer, int max_size)
        # Nota: Esta función requiere un buffer pre-asignado
        # Para B-Minor, read_string() retorna string, pero en runtime necesita buffer
        f_type = ir.FunctionType(self.tipo_void, [ir.PointerType(self.tipo_caracter), ir.IntType(32)])
        self._read_string = ir.Function(self.llvm_module, f_type, name="read_string")
        
        # Funciones matemáticas
        # double sqrt_func(double)
        f_type = ir.FunctionType(self.tipo_flotante, [self.tipo_flotante])
        self._sqrt_func = ir.Function(self.llvm_module, f_type, name="sqrt_func")
        
        # double abs_func(double)
        f_type = ir.FunctionType(self.tipo_flotante, [self.tipo_flotante])
        self._abs_func = ir.Function(self.llvm_module, f_type, name="abs_func")
        
        # double max_func(double, double)
        f_type = ir.FunctionType(self.tipo_flotante, [self.tipo_flotante, self.tipo_flotante])
        self._max_func = ir.Function(self.llvm_module, f_type, name="max_func")
        
        # double min_func(double, double)
        f_type = ir.FunctionType(self.tipo_flotante, [self.tipo_flotante, self.tipo_flotante])
        self._min_func = ir.Function(self.llvm_module, f_type, name="min_func")
        
        # int string_length(const char*)
        f_type = ir.FunctionType(ir.IntType(32), [ir.PointerType(self.tipo_caracter)])
        self._string_length = ir.Function(self.llvm_module, f_type, name="string_length")
        
        # Funciones para arrays dinámicos con tamaño almacenado
        # long long* array_new_integer(int n)
        f_type = ir.FunctionType(ir.PointerType(self.tipo_entero), [ir.IntType(32)])
        self._array_new_integer = ir.Function(self.llvm_module, f_type, name="array_new_integer")
        
        # long long array_length_integer(long long* arr)
        f_type = ir.FunctionType(self.tipo_entero, [ir.PointerType(self.tipo_entero)])
        self._array_length_integer = ir.Function(self.llvm_module, f_type, name="array_length_integer")
        
        # double* array_new_float(int n)
        f_type = ir.FunctionType(ir.PointerType(self.tipo_flotante), [ir.IntType(32)])
        self._array_new_float = ir.Function(self.llvm_module, f_type, name="array_new_float")
        
        # long long array_length_float(double* arr)
        f_type = ir.FunctionType(self.tipo_entero, [ir.PointerType(self.tipo_flotante)])
        self._array_length_float = ir.Function(self.llvm_module, f_type, name="array_length_float")
        
        # bool* array_new_boolean(int n)
        f_type = ir.FunctionType(ir.PointerType(self.tipo_booleano), [ir.IntType(32)])
        self._array_new_boolean = ir.Function(self.llvm_module, f_type, name="array_new_boolean")
        
        # long long array_length_boolean(bool* arr)
        f_type = ir.FunctionType(self.tipo_entero, [ir.PointerType(self.tipo_booleano)])
        self._array_length_boolean = ir.Function(self.llvm_module, f_type, name="array_length_boolean")
        
        # double pow(double, double) - para operación de potencia
        f_type = ir.FunctionType(self.tipo_flotante, [self.tipo_flotante, self.tipo_flotante])
        self._llvm_pow = ir.Function(self.llvm_module, f_type, name="llvm.pow.f64")
        self._llvm_pow.attributes.add('readnone')
        
        # Mapeo de nombres B-Minor a funciones runtime
        self.builtin_functions = {
            'read_integer': self._read_integer,
            'read_float': self._read_float,
            'sqrt': self._sqrt_func,
            'abs': self._abs_func,
            'max': self._max_func,
            'min': self._min_func,
            'length': self._string_length,  # Por defecto para strings, se maneja especial para arrays
            'array_length': self._string_length,  # Alias de length para arrays
        }

    def _convertir_tipo_llvm(self, tipo_bminor):
        """Convierte un tipo B-Minor a su equivalente LLVM."""
        if isinstance(tipo_bminor, str):
            return self.mapeo_tipos.get(tipo_bminor, self.tipo_entero)
        elif isinstance(tipo_bminor, ArrayType):
            elem_type = self._convertir_tipo_llvm(tipo_bminor.element_type.name)
            return ir.PointerType(elem_type)
        else:
            return self.tipo_entero  # Fallback

    def _guardar_alcance(self):
        """Guarda el estado actual de las variables (para scopes)"""
        return dict(self.variables)

    def _restaurar_alcance(self, variables_guardadas):
        """Recupera el alcance previo de variables"""
        self.variables = variables_guardadas

    # =====================================================================
    # Nodos de Programa y Bloques
    # =====================================================================

    def visit(self, n: Program):
        '''
        Punto de entrada. Primero declara todas las funciones,
        luego las define.
        '''
        # FASE 0: Procesar variables globales
        for stmt in n.body:
            if isinstance(stmt, VarDecl):
                self._procesar_variable_global(stmt)
            elif isinstance(stmt, ArrayDecl):
                self._procesar_array_global(stmt)
        
        # FASE 1: Declarar todas las funciones (forward declarations)
        for stmt in n.body:
            if isinstance(stmt, FuncDecl):
                self._declarar_funcion(stmt)
        
        # FASE 2: Definir funciones con cuerpo
        for stmt in n.body:
            if isinstance(stmt, FuncDecl):
                if stmt.body:  # Solo si tiene cuerpo
                    self.visit(stmt)

    def _declarar_funcion(self, n: FuncDecl):
        """Declara una función (prototipo) sin definir su cuerpo"""
        func_name = n.name
        
        # Obtener tipo de retorno
        return_type = self._convertir_tipo_llvm(n.sym_type)
        
        # Obtener tipos de parámetros
        param_types = []
        for param in n.params:
            if isinstance(param.type, SimpleType):
                param_types.append(self._convertir_tipo_llvm(param.type.name))
            elif isinstance(param.type, ArrayType):
                # Arrays como parámetros son punteros
                elem_type = self._convertir_tipo_llvm(param.type.element_type.name)
                param_types.append(elem_type.as_pointer())
        
        # Crear tipo de función
        func_type = ir.FunctionType(return_type, param_types)
        
        # Crear función en el módulo
        func = ir.Function(self.llvm_module, func_type, name=func_name)
        
        # Nombrar los argumentos
        for i, param in enumerate(n.params):
            func.args[i].name = param.name
        
        # Guardar en tabla de funciones
        self.funciones_llvm[func_name] = func

    def _procesar_variable_global(self, n: VarDecl):
        '''
        Procesa una variable global. Crea una GlobalVariable en LLVM.
        '''
        var_name = n.name
        var_type_bminor = n.sym_type
        var_type_llvm = self.mapeo_tipos[var_type_bminor]
        
        # Crear variable global
        global_var = ir.GlobalVariable(self.llvm_module, var_type_llvm, name=var_name)
        global_var.linkage = 'internal'
        
        # Inicializar con valor por defecto o el valor proporcionado
        if n.value:
            # Evaluar el valor inicial (necesitamos un builder temporal)
            # Para constantes simples, podemos crear el valor directamente
            if isinstance(n.value, Integer):
                init_val = ir.Constant(self.tipo_entero, n.value.value)
            elif isinstance(n.value, Float):
                init_val = ir.Constant(self.tipo_flotante, n.value.value)
            elif isinstance(n.value, Boolean):
                init_val = ir.Constant(self.tipo_booleano, int(n.value.value))
            elif isinstance(n.value, Char):
                init_val = ir.Constant(self.tipo_caracter, ord(n.value.value))
            else:
                # Para expresiones más complejas, inicializar con 0 y luego asignar
                if var_type_bminor == 'integer':
                    init_val = ir.Constant(self.tipo_entero, 0)
                elif var_type_bminor == 'float':
                    init_val = ir.Constant(self.tipo_flotante, 0.0)
                elif var_type_bminor == 'boolean':
                    init_val = ir.Constant(self.tipo_booleano, 0)
                else:
                    init_val = ir.Constant(var_type_llvm, 0)
        else:
            # Inicializar con valor por defecto
            if var_type_bminor == 'integer':
                init_val = ir.Constant(self.tipo_entero, 0)
            elif var_type_bminor == 'float':
                init_val = ir.Constant(self.tipo_flotante, 0.0)
            elif var_type_bminor == 'boolean':
                init_val = ir.Constant(self.tipo_booleano, 0)
            elif var_type_bminor == 'char':
                init_val = ir.Constant(self.tipo_caracter, 0)
            else:
                init_val = ir.Constant(var_type_llvm, 0)
        
        global_var.initializer = init_val
        self.global_variables[var_name] = global_var
        
        # Si el valor inicial es una expresión compleja, necesitamos asignarlo en main
        # Por ahora, solo manejamos literales simples

    def _procesar_array_global(self, n: ArrayDecl):
        '''
        Procesa un array global. Crea una GlobalVariable de tipo array en LLVM.
        '''
        var_name = n.name
        array_type = n.type
        
        # Calcular el tamaño del array
        if n.size:
            # El tamaño puede ser una constante o expresión
            # Por ahora, asumimos que es una constante
            if isinstance(n.size, Integer):
                array_size = n.size.value
            else:
                # Para expresiones, necesitamos evaluarlas
                # Por simplicidad, asumimos que es una constante conocida
                array_size = 1  # Fallback
        else:
            array_size = 1  # Fallback
        
        # Obtener tipo del elemento
        if isinstance(array_type.element_type, SimpleType):
            elem_type = self.mapeo_tipos[array_type.element_type.name]
        else:
            elem_type = self.tipo_entero  # Fallback
        
        # Crear tipo de array
        array_llvm_type = ir.ArrayType(elem_type, array_size)
        
        # Crear variable global
        global_array = ir.GlobalVariable(self.llvm_module, array_llvm_type, name=var_name)
        global_array.linkage = 'internal'
        
        # Inicializar con ceros - crear un array de ceros
        zero_elem = ir.Constant(elem_type, 0)
        zero_array = ir.Constant(array_llvm_type, [zero_elem] * array_size)
        global_array.initializer = zero_array
        self.global_variables[var_name] = global_array

    def visit(self, n: BlockStmt):
        '''
        Visita una secuencia de sentencias dentro de un bloque.
        '''
        # Guardar scope actual
        variables_guardadas = self._guardar_alcance()
        
        for stmt in n.statements:
            self.visit(stmt)
        
        # Restaurar scope
        self._restaurar_alcance(variables_guardadas)

    # =====================================================================
    # Nodos de Declaraciones
    # =====================================================================

    def visit(self, n: VarDecl):
        '''
        Genera código para una declaración de variable.
        '''
        var_name = n.name
        
        # Usar el tipo anotado por el 'checker'
        var_type_bminor = n.sym_type 
        var_type_llvm = self.mapeo_tipos[var_type_bminor]

        # --- Patrón 'alloca' ---
        # 1. Reservar espacio en el stack (alloca)
        #    'goto_entry_block' se encarga automáticamente de 
        #    posicionar el 'alloca' en el bloque de entrada.   
        with self.constructor_ir.goto_entry_block():
            var_ptr = self.constructor_ir.alloca(var_type_llvm, name=var_name)
        
        # 2. Guardar el puntero en nuestra tabla de símbolos de LLVM
        self.variables[var_name] = var_ptr

        # 3. Si hay un valor inicial, generar 'store'
        if n.value:
            init_val = self.visit(n.value)
            self.constructor_ir.store(init_val, var_ptr)
        else:
            # Inicializar con valor por defecto (0, 0.0, false)
            if var_type_bminor == 'integer':
                default_val = ir.Constant(self.tipo_entero, 0)
            elif var_type_bminor == 'float':
                default_val = ir.Constant(self.tipo_flotante, 0.0)
            elif var_type_bminor == 'boolean':
                default_val = ir.Constant(self.tipo_booleano, 0)
            elif var_type_bminor == 'char':
                default_val = ir.Constant(self.tipo_caracter, 0)
            else:
                default_val = ir.Constant(var_type_llvm, 0)
            self.constructor_ir.store(default_val, var_ptr)

    def visit(self, n: ArrayDecl):
        '''
        Genera código para una declaración de array.
        Ej: arr: array [5] integer;
        Para arrays con tamaño constante, usa alloca.
        Para arrays con tamaño calculado, usa array_new_integer del runtime.
        '''
        var_name = n.name
        
        # Obtener tipo de elemento
        element_type_llvm = self._convertir_tipo_llvm(n.type.element_type.name)
        
        # Evaluar el tamaño (puede ser una expresión)
        if n.type.size:
            size_val = self.visit(n.type.size)
            # Asegurar que es i64
            if size_val.type != self.tipo_entero:
                size_val = self.constructor_ir.sext(size_val, self.tipo_entero)
        else:
            # Si no tiene tamaño, es un error (ya debería haber sido detectado por checker)
            size_val = ir.Constant(self.tipo_entero, 0)
        
        # Verificar si el tamaño es una constante
        is_constant_size = isinstance(n.type.size, Integer) if n.type.size else False
        
        # Usar array_new_integer para todos los arrays (tanto constantes como dinámicos)
        # Esto simplifica el manejo de array_length y permite pasar arrays como parámetros
        # Convertir tamaño a i32 para la función runtime
        if is_constant_size:
            size_i32 = ir.Constant(ir.IntType(32), n.type.size.value)
        else:
            size_i32 = self.constructor_ir.trunc(size_val, ir.IntType(32), name="size_i32")
        
        # Llamar a array_new_integer/float/boolean según el tipo
        if n.type.element_type.name == 'integer':
            array_ptr = self.constructor_ir.call(self._array_new_integer, [size_i32], name=f"{var_name}_new")
        elif n.type.element_type.name == 'float':
            array_ptr = self.constructor_ir.call(self._array_new_float, [size_i32], name=f"{var_name}_new")
        elif n.type.element_type.name == 'boolean':
            array_ptr = self.constructor_ir.call(self._array_new_boolean, [size_i32], name=f"{var_name}_new")
        else:
            # Por defecto, usar integer
            array_ptr = self.constructor_ir.call(self._array_new_integer, [size_i32], name=f"{var_name}_new")
        
        # Guardar puntero
        self.variables[var_name] = array_ptr
        
        # Inicializar si hay valores
        if n.value:
            for i, val_node in enumerate(n.value):
                val = self.visit(val_node)
                # Calcular puntero al elemento
                idx = ir.Constant(self.tipo_entero, i)
                elem_ptr = self.constructor_ir.gep(array_ptr, [idx], inbounds=True)
                self.constructor_ir.store(val, elem_ptr)

    def visit(self, n: FuncDecl):
        '''
        Define una función (genera su cuerpo).
        '''
        func_name = n.name
        func = self.funciones_llvm[func_name]
        
        # Guardar contexto anterior
        funcion_anterior = self.funcion_actual
        constructor_anterior = self.constructor_ir
        variables_anteriores = self.variables
        
        # Nuevo contexto
        self.funcion_actual = func
        self.variables = {}
        
        # Crear bloque de entrada
        entry_block = func.append_basic_block('entry')
        self.constructor_ir = ir.IRBuilder(entry_block)
        
        # Crear allocas para los parámetros y copiar valores
        for i, param in enumerate(n.params):
            param_name = param.name
            
            # Determinar tipo del parámetro
            if isinstance(param.type, SimpleType):
                param_type = self._convertir_tipo_llvm(param.type.name)
            elif isinstance(param.type, ArrayType):
                # Arrays como parámetros son punteros
                elem_type = self._convertir_tipo_llvm(param.type.element_type.name)
                param_type = elem_type.as_pointer()
            
            # Crear alloca
            param_ptr = self.constructor_ir.alloca(param_type, name=param_name)
            self.variables[param_name] = param_ptr
            
            # Copiar argumento al alloca
            self.constructor_ir.store(func.args[i], param_ptr)
        
        # Generar cuerpo de la función
        if n.body:
            self.visit(n.body)
        
        # Asegurar que la función termina con return
        if not self.constructor_ir.block.is_terminated:
            if n.sym_type == 'void':
                self.constructor_ir.ret_void()
            else:
                # Retornar valor por defecto
                return_type = self._convertir_tipo_llvm(n.sym_type)
                if n.sym_type == 'integer':
                    self.constructor_ir.ret(ir.Constant(return_type, 0))
                elif n.sym_type == 'float':
                    self.constructor_ir.ret(ir.Constant(return_type, 0.0))
                elif n.sym_type == 'boolean':
                    self.constructor_ir.ret(ir.Constant(return_type, 0))
                elif n.sym_type == 'char':
                    self.constructor_ir.ret(ir.Constant(return_type, 0))
        
        # Restaurar contexto
        self.funcion_actual = funcion_anterior
        self.constructor_ir = constructor_anterior
        self.variables = variables_anteriores

    # =====================================================================
    # Nodos de Sentencias
    # =====================================================================

    def visit(self, n: Assignment):
        '''
        Genera código para una asignación.
        Ej: x = 10;
        '''
        # Visita la parte derecha (RHS) para obtener el valor LLVM
        value_llvm = self.visit(n.value)

        # Para VarLocation
        if isinstance(n.location, VarLocation):
            var_name = n.location.name
            # Buscar primero en variables globales
            if var_name in self.global_variables:
                var_ptr = self.global_variables[var_name]
            elif var_name in self.variables:
                var_ptr = self.variables[var_name]
            else:
                raise RuntimeError(f"Variable '{var_name}' no encontrada")
            self.constructor_ir.store(value_llvm, var_ptr)
        
        # Para ArraySubscript
        elif isinstance(n.location, ArraySubscript):
            # Obtener puntero base del array
            base_location = n.location.location
            is_global = False
            
            if isinstance(base_location, VarLocation):
                var_name = base_location.name
                # Buscar primero en variables globales
                if var_name in self.global_variables:
                    array_ptr_or_ptr_ptr = self.global_variables[var_name]
                    is_global = True
                elif var_name in self.variables:
                    array_ptr_or_ptr_ptr = self.variables[var_name]
                else:
                    raise RuntimeError(f"Variable '{var_name}' no encontrada")
                
                # Si es un array local (i64*), ese es el puntero base
                if isinstance(array_ptr_or_ptr_ptr.type.pointee, (ir.IntType, ir.DoubleType, ir.IntType, ir.IntType)):
                    array_ptr = array_ptr_or_ptr_ptr
                # Si es un parámetro (i64**), hay que cargar el puntero real
                elif isinstance(array_ptr_or_ptr_ptr.type.pointee, ir.PointerType):
                    array_ptr = self.constructor_ir.load(array_ptr_or_ptr_ptr, name="array_base")
                else:
                    array_ptr = array_ptr_or_ptr_ptr
            else:
                # Arrays anidados: visitar recursivamente
                array_ptr = self.visit(base_location)
            
            # Obtener índice
            index_val = self.visit(n.location.index)
            zero = ir.Constant(self.tipo_entero, 0)
            
            # GEP para obtener puntero al elemento
            # Para arrays globales necesitamos [0, index], para locales solo [index]
            if is_global:
                elem_ptr = self.constructor_ir.gep(array_ptr, [zero, index_val], inbounds=True, name="elem_ptr")
            else:
                elem_ptr = self.constructor_ir.gep(array_ptr, [index_val], inbounds=True, name="elem_ptr")
            
            self.constructor_ir.store(value_llvm, elem_ptr)

    def visit(self, n: PrintStmt):
        '''
        Genera código para print.
        Ej: print x, 10, true, "hello";
        '''
        for value_node in n.values:
            # Visita la expresión para obtener el valor LLVM
            value_llvm = self.visit(value_node)
            
            # Lee el tipo anotado por el 'checker'
            node_type = value_node.type 

            # Llama a la función de runtime correcta
            if node_type == 'integer':
                self.constructor_ir.call(self._print_integer, [value_llvm])
            elif node_type == 'float':
                self.constructor_ir.call(self._print_float, [value_llvm])
            elif node_type == 'boolean':
                self.constructor_ir.call(self._print_boolean, [value_llvm])
            elif node_type == 'char':
                self.constructor_ir.call(self._print_char, [value_llvm])
            elif node_type == 'string':
                self.constructor_ir.call(self._print_string, [value_llvm])

        # Imprimir nueva línea al final (comportamiento de B-Minor)
        newline_char = ir.Constant(self.tipo_caracter, 10) # 10 es \n
        self.constructor_ir.call(self._print_char, [newline_char])

    def visit(self, n: ReturnStmt):
        '''
        Genera código para return.
        '''
        if n.value:
            # Return con valor
            return_val = self.visit(n.value)
            self.constructor_ir.ret(return_val)
        else:
            # Return void
            self.constructor_ir.ret_void()

    def visit(self, n: IfStmt):
        '''
        Genera código para if/else.
        
        Estructura:
            br cond, then_block, else_block
        then_block:
            ...
            br merge_block
        else_block:
            ...
            br merge_block
        merge_block:
            ...
        '''
        # Evaluar condición
        cond_val = self.visit(n.condition)
        
        # Crear bloques
        then_block = self.funcion_actual.append_basic_block('if.then')
        merge_block = self.funcion_actual.append_basic_block('if.end')
        
        if n.false_body:
            else_block = self.funcion_actual.append_basic_block('if.else')
            self.constructor_ir.cbranch(cond_val, then_block, else_block)
        else:
            self.constructor_ir.cbranch(cond_val, then_block, merge_block)
        
        # Generar bloque then
        self.constructor_ir.position_at_end(then_block)
        self.visit(n.true_body)
        if not self.constructor_ir.block.is_terminated:
            self.constructor_ir.branch(merge_block)
        
        # Generar bloque else (si existe)
        if n.false_body:
            self.constructor_ir.position_at_end(else_block)
            self.visit(n.false_body)
            if not self.constructor_ir.block.is_terminated:
                self.constructor_ir.branch(merge_block)
        
        # Continuar en merge_block
        self.constructor_ir.position_at_end(merge_block)

    def visit(self, n: WhileStmt):
        '''
        Genera código para while.
        
        Estructura:
            br cond_block
        cond_block:
            cond = ...
            br cond, body_block, end_block
        body_block:
            ...
            br cond_block
        end_block:
            ...
        '''
        cond_block = self.funcion_actual.append_basic_block('while.cond')
        body_block = self.funcion_actual.append_basic_block('while.body')
        end_block = self.funcion_actual.append_basic_block('while.end')
        
        # Saltar a evaluar condición
        self.constructor_ir.branch(cond_block)
        
        # Generar bloque de condición
        self.constructor_ir.position_at_end(cond_block)
        cond_val = self.visit(n.condition)
        self.constructor_ir.cbranch(cond_val, body_block, end_block)
        
        # Generar cuerpo
        self.constructor_ir.position_at_end(body_block)
        self.visit(n.body)
        if not self.constructor_ir.block.is_terminated:
            self.constructor_ir.branch(cond_block)
        
        # Continuar después del while
        self.constructor_ir.position_at_end(end_block)

    def visit(self, n: DoWhileStmt):
        '''
        Genera código para do-while.
        
        Estructura:
            br body_block
        body_block:
            ...
            br cond_block
        cond_block:
            cond = ...
            br cond, body_block, end_block
        end_block:
            ...
        '''
        body_block = self.funcion_actual.append_basic_block('do.body')
        cond_block = self.funcion_actual.append_basic_block('do.cond')
        end_block = self.funcion_actual.append_basic_block('do.end')
        
        # Saltar al cuerpo
        self.constructor_ir.branch(body_block)
        
        # Generar cuerpo
        self.constructor_ir.position_at_end(body_block)
        self.visit(n.body)
        if not self.constructor_ir.block.is_terminated:
            self.constructor_ir.branch(cond_block)
        
        # Generar bloque de condición
        self.constructor_ir.position_at_end(cond_block)
        cond_val = self.visit(n.condition)
        self.constructor_ir.cbranch(cond_val, body_block, end_block)
        
        # Continuar después del do-while
        self.constructor_ir.position_at_end(end_block)

    def visit(self, n: ForStmt):
        '''
        Genera código para for.
        
        for (init; cond; update) body
        
        Estructura:
            init
            br cond_block
        cond_block:
            cond = ...
            br cond, body_block, end_block
        body_block:
            ...
            br update_block
        update_block:
            update
            br cond_block
        end_block:
            ...
        '''
        # Inicialización
        if n.init:
            self.visit(n.init)
        
        cond_block = self.funcion_actual.append_basic_block('for.cond')
        body_block = self.funcion_actual.append_basic_block('for.body')
        update_block = self.funcion_actual.append_basic_block('for.update')
        end_block = self.funcion_actual.append_basic_block('for.end')
        
        # Saltar a condición
        self.constructor_ir.branch(cond_block)
        
        # Generar bloque de condición
        self.constructor_ir.position_at_end(cond_block)
        if n.condition:
            cond_val = self.visit(n.condition)
            self.constructor_ir.cbranch(cond_val, body_block, end_block)
        else:
            # Sin condición = bucle infinito
            self.constructor_ir.branch(body_block)
        
        # Generar cuerpo
        self.constructor_ir.position_at_end(body_block)
        self.visit(n.body)
        if not self.constructor_ir.block.is_terminated:
            self.constructor_ir.branch(update_block)
        
        # Generar actualización
        self.constructor_ir.position_at_end(update_block)
        if n.update:
            self.visit(n.update)
        self.constructor_ir.branch(cond_block)
        
        # Continuar después del for
        self.constructor_ir.position_at_end(end_block)

    # =====================================================================
    # Nodos de Expresiones - Literales
    # =====================================================================

    def visit(self, n: Integer):
        '''Genera un literal de entero constante (i64)'''
        return ir.Constant(self.tipo_entero, n.value)

    def visit(self, n: Float):
        '''Genera un literal de float constante (double)'''
        return ir.Constant(self.tipo_flotante, n.value)

    def visit(self, n: Boolean):
        '''Genera un literal de booleano constante (i1)'''
        return ir.Constant(self.tipo_booleano, int(n.value))

    def visit(self, n: Char):
        '''Genera un literal de char constante (i8)'''
        return ir.Constant(self.tipo_caracter, ord(n.value))

    def visit(self, n: String):
        '''
        Genera un literal de string constante (i8*).
        Crea una variable global para la cadena.
        '''
        # Crear array de bytes con terminador nulo
        string_bytes = bytearray(n.value.encode('utf-8') + b'\x00')
        string_len = len(string_bytes)
        
        # Tipo del array
        string_array_type = ir.ArrayType(self.tipo_caracter, string_len)
        
        # Crear variable global
        string_name = f'.str.{self.contador_cadenas}'
        self.contador_cadenas += 1
        
        global_string = ir.GlobalVariable(self.llvm_module, string_array_type, name=string_name)
        global_string.linkage = 'internal'
        global_string.global_constant = True
        global_string.initializer = ir.Constant(string_array_type, string_bytes)
        
        # Obtener puntero al primer elemento (i8*)
        zero = ir.Constant(self.tipo_entero, 0)
        string_ptr = self.constructor_ir.gep(global_string, [zero, zero], inbounds=True)
        
        return string_ptr

    # =====================================================================
    # Nodos de Expresiones - Variables y Arrays
    # =====================================================================

    def visit(self, n: VarLocation):
        '''
        Genera código para leer (cargar) una variable.
        Es inteligente: si es un array, pasa el puntero;
        si es un tipo simple, carga el valor.
        Busca primero en variables globales, luego en locales.
        '''
        var_name = n.name
        is_global = False
        
        # Buscar primero en variables globales
        if var_name in self.global_variables:
            var_ptr = self.global_variables[var_name]
            is_global = True
        elif var_name in self.variables:
            var_ptr = self.variables[var_name]
        else:
            raise RuntimeError(f"Variable '{var_name}' no encontrada") 
        
        # El checker (checker.py) anotó el nodo con su tipo B-Minor.
        # n.type será 'integer', 'float', o una instancia de ArrayType.
        
        # Si el tipo del nodo es ArrayType, estamos pasándolo como argumento.
        if isinstance(n.type, ArrayType):
            if is_global:
                # Variable global de tipo array: obtener puntero al primer elemento
                zero = ir.Constant(self.tipo_entero, 0)
                return self.constructor_ir.gep(var_ptr, [zero, zero], inbounds=True, name=f"{var_name}_ptr")
            else:
                # Caso 1: Array local (e.g. numeros: array[5] integer)
                # var_ptr es i64* (puntero al primer elemento)
                if isinstance(var_ptr.type.pointee, (ir.IntType, ir.DoubleType, ir.IntType, ir.IntType)):
                    return var_ptr # Retorna i64* o double*
                
                # Caso 2: Array como parámetro (e.g. arr: array[] integer)
                # var_ptr es i64** (puntero a un puntero)
                elif isinstance(var_ptr.type.pointee, ir.PointerType):
                    return self.constructor_ir.load(var_ptr, name=f"{var_name}_ptr") # Carga para obtener i64*

        # Si no es un array, es un tipo simple. Cargar el valor.
        # Para variables globales, var_ptr es un GlobalVariable (puntero), necesitamos cargar
        # Para variables locales, var_ptr es un alloca (puntero), también necesitamos cargar
        return self.constructor_ir.load(var_ptr, name=var_name + "_val")

    def visit(self, n: ArraySubscript):
        '''
        Genera código para acceder a un elemento de array.
        Ej: arr[5]
        '''
        # Obtener puntero base del array
        base_location = n.location
        is_global = False
        
        if isinstance(base_location, VarLocation):
            var_name = base_location.name
            # Buscar primero en variables globales
            if var_name in self.global_variables:
                array_ptr_or_ptr_ptr = self.global_variables[var_name]
                is_global = True
            elif var_name in self.variables:
                array_ptr_or_ptr_ptr = self.variables[var_name]
            else:
                raise RuntimeError(f"Variable '{var_name}' no encontrada")
            
            # Si es un array local (i64*), ese es el puntero base
            if isinstance(array_ptr_or_ptr_ptr.type.pointee, (ir.IntType, ir.DoubleType, ir.IntType, ir.IntType)):
                array_ptr = array_ptr_or_ptr_ptr
            # Si es un parámetro (i64**), hay que cargar el puntero real
            elif isinstance(array_ptr_or_ptr_ptr.type.pointee, ir.PointerType):
                array_ptr = self.constructor_ir.load(array_ptr_or_ptr_ptr, name="array_base")
            else:
                array_ptr = array_ptr_or_ptr_ptr
        else:
            # Arrays anidados
            array_ptr = self.visit(base_location)
        
        # Obtener índice
        index_val = self.visit(n.index)
        zero = ir.Constant(self.tipo_entero, 0)
        
        # GEP: para arrays globales necesitamos [0, index], para locales solo [index]
        if is_global:
            elem_ptr = self.constructor_ir.gep(array_ptr, [zero, index_val], inbounds=True, name="elem_ptr")
        else:
            elem_ptr = self.constructor_ir.gep(array_ptr, [index_val], inbounds=True, name="elem_ptr")
        
        # Cargar valor
        return self.constructor_ir.load(elem_ptr, name="elem_val")

    def visit(self, n: BinOper):
        '''
        Genera código para operaciones binarias.
        '''
        left_val = self.visit(n.left)
        right_val = self.visit(n.right)
        
        # Asumimos que el checker ya validó tipos.
        # Pero necesitamos saber si es int o float para elegir la instrucción.
        # n.left.type y n.right.type tienen los tipos B-Minor.
        
        is_float = (n.left.type == 'float' or n.right.type == 'float')
        
        if n.op == '+':
            if is_float:
                return self.constructor_ir.fadd(left_val, right_val, name="addtmp")
            else:
                return self.constructor_ir.add(left_val, right_val, name="addtmp")
        
        elif n.op == '-':
            if is_float:
                return self.constructor_ir.fsub(left_val, right_val, name="subtmp")
            else:
                return self.constructor_ir.sub(left_val, right_val, name="subtmp")
        
        elif n.op == '*':
            if is_float:
                return self.constructor_ir.fmul(left_val, right_val, name="multmp")
            else:
                return self.constructor_ir.mul(left_val, right_val, name="multmp")
        
        elif n.op == '/':
            if is_float:
                return self.constructor_ir.fdiv(left_val, right_val, name="divtmp")
            else:
                return self.constructor_ir.sdiv(left_val, right_val, name="divtmp")
        
        elif n.op == '%':
            return self.constructor_ir.srem(left_val, right_val, name="remtmp")
        
        elif n.op == '^':
            # Potencia: llamar a función auxiliar o intrínseco
            # Convertir a float si es necesario
            if not is_float:
                left_val = self.constructor_ir.sitofp(left_val, self.tipo_flotante)
                right_val = self.constructor_ir.sitofp(right_val, self.tipo_flotante)
            
            return self.constructor_ir.call(self._llvm_pow, [left_val, right_val], name="powtmp")

        # Operadores relacionales
        elif n.op in ['<', '<=', '>', '>=', '==', '!=']:
            if is_float:
                return self.constructor_ir.fcmp_ordered(n.op, left_val, right_val, name="cmptmp")
            else:
                return self.constructor_ir.icmp_signed(n.op, left_val, right_val, name="cmptmp")
        
        elif n.op == '&&':
            return self.constructor_ir.and_(left_val, right_val, name="andtmp")
        
        elif n.op == '||':
            return self.constructor_ir.or_(left_val, right_val, name="ortmp")

    def visit(self, n: UnaryOper):
        '''
        Genera código para operaciones unarias.
        '''
        # Manejar operadores de incremento/decremento
        if isinstance(n, (PostInc, PostDec, PreInc, PreDec)):
            return self._visit_increment_decrement(n)
        
        # Operadores unarios normales
        expr_val = self.visit(n.expr)
        
        if n.op == '-':
            if n.expr.type == 'float':
                return self.constructor_ir.fneg(expr_val, name="negtmp")
            else:
                return self.constructor_ir.neg(expr_val, name="negtmp")
        elif n.op == '!':
            # Negación lógica
            return self.constructor_ir.xor(expr_val, ir.Constant(self.tipo_booleano, 1), name="nottmp")
        else:
            raise NotImplementedError(f"Operador unario '{n.op}' no implementado")
    
    def _visit_increment_decrement(self, n):
        '''
        Genera código para operadores de incremento/decremento (++, --).
        PostInc/PostDec: retornan el valor original, luego incrementan/decrementan
        PreInc/PreDec: incrementan/decrementan, luego retornan el nuevo valor
        '''
        # Obtener el puntero a la variable
        if isinstance(n.expr, VarLocation):
            var_name = n.expr.name
            # Buscar primero en variables globales
            if var_name in self.global_variables:
                var_ptr = self.global_variables[var_name]
            elif var_name in self.variables:
                var_ptr = self.variables[var_name]
            else:
                raise RuntimeError(f"Variable '{var_name}' no encontrada")
        else:
            raise RuntimeError("Operadores ++/-- solo aplicables a variables")
        
        # Cargar el valor actual
        current_val = self.constructor_ir.load(var_ptr, name="current_val")
        
        # Crear constante 1 del tipo apropiado
        if n.expr.type == 'float':
            one = ir.Constant(self.tipo_flotante, 1.0)
        else:
            one = ir.Constant(self.tipo_entero, 1)
        
        # Calcular nuevo valor
        if n.op == '++':
            new_val = self.constructor_ir.add(current_val, one, name="inc_val") if n.expr.type != 'float' else \
                      self.constructor_ir.fadd(current_val, one, name="inc_val")
        else:  # '--'
            new_val = self.constructor_ir.sub(current_val, one, name="dec_val") if n.expr.type != 'float' else \
                      self.constructor_ir.fsub(current_val, one, name="dec_val")
        
        # Guardar el nuevo valor
        self.constructor_ir.store(new_val, var_ptr)
        
        # Retornar el valor apropiado según pre/post
        if isinstance(n, (PostInc, PostDec)):
            # Post: retornar el valor original
            return current_val
        else:  # PreInc, PreDec
            # Pre: retornar el nuevo valor
            return new_val

    def visit(self, n: FuncCall):
        '''
        Genera código para llamadas a funciones.
        Maneja tanto funciones definidas por el usuario como funciones built-in del runtime.
        '''
        func_name = n.name
        
        # Verificar si es una función built-in del runtime
        if func_name in self.builtin_functions:
            func = self.builtin_functions[func_name]
            
            # Manejo especial para read_string (requiere buffer)
            if func_name == 'read_string':
                # Para read_string, necesitamos asignar un buffer
                # Por ahora, asignamos un buffer de 1024 caracteres
                buffer_size = 1024
                buffer_type = ir.ArrayType(self.tipo_caracter, buffer_size)
                buffer_ptr = self.constructor_ir.alloca(buffer_type, name="read_string_buffer")
                buffer_ptr_cast = self.constructor_ir.bitcast(buffer_ptr, ir.PointerType(self.tipo_caracter), name="buffer_cast")
                
                # Llamar a read_string con el buffer
                size_const = ir.Constant(ir.IntType(32), buffer_size)
                self.constructor_ir.call(self._read_string, [buffer_ptr_cast, size_const])
                
                # Retornar el puntero al buffer
                return buffer_ptr_cast
            
            # Evaluar argumentos
            args_vals = []
            for i, arg in enumerate(n.args):
                arg_val = self.visit(arg)
                
                # Convertir tipos si es necesario para funciones matemáticas
                # Las funciones matemáticas esperan float, pero pueden recibir integer
                if func_name in ['sqrt', 'abs']:
                    # Convertir integer a float si es necesario
                    if isinstance(arg_val.type, ir.IntType):
                        arg_val = self.constructor_ir.sitofp(arg_val, self.tipo_flotante, name="convtofloat")
                elif func_name in ['max', 'min']:
                    # Convertir integer a float si es necesario para ambos argumentos
                    if isinstance(arg_val.type, ir.IntType):
                        arg_val = self.constructor_ir.sitofp(arg_val, self.tipo_flotante, name="convtofloat")
                
                args_vals.append(arg_val)
            
            # Manejo especial para length y array_length (pueden recibir string o array)
            if func_name in ['length', 'array_length']:
                if len(args_vals) > 0:
                    arg_val = args_vals[0]
                    # Verificar si el argumento es un VarLocation (variable) para arrays estáticos
                    array_name = None
                    if len(n.args) > 0 and isinstance(n.args[0], VarLocation):
                        array_name = n.args[0].name
                        # Si es un array estático, usar el tamaño constante
                        if array_name in self.static_array_sizes:
                            size = self.static_array_sizes[array_name]
                            return ir.Constant(self.tipo_entero, size)
                    
                    # Determinar si es string (char*) o array
                    # Si es un puntero a char, es string
                    # Si es un puntero a otro tipo, es array
                    if isinstance(arg_val.type, ir.PointerType):
                        pointee_type = arg_val.type.pointee
                        if pointee_type == self.tipo_caracter:
                            # Es un string, usar string_length
                            length_result = self.constructor_ir.call(self._string_length, args_vals, name="length_result")
                            # Convertir int32 a int64 (integer de B-Minor)
                            return self.constructor_ir.sext(length_result, self.tipo_entero, name="length_ext")
                        elif pointee_type == self.tipo_entero:
                            # Es un array de enteros, usar array_length_integer
                            length_result = self.constructor_ir.call(self._array_length_integer, args_vals, name="array_length_result")
                            return length_result
                        elif pointee_type == self.tipo_flotante:
                            # Es un array de flotantes, usar array_length_float
                            length_result = self.constructor_ir.call(self._array_length_float, args_vals, name="array_length_result")
                            return length_result
                        elif pointee_type == self.tipo_booleano:
                            # Es un array de booleanos, usar array_length_boolean
                            length_result = self.constructor_ir.call(self._array_length_boolean, args_vals, name="array_length_result")
                            return length_result
                        else:
                            # Array de otro tipo, intentar con integer por defecto
                            length_result = self.constructor_ir.call(self._array_length_integer, args_vals, name="array_length_result")
                            return length_result
                    else:
                        # No es un puntero, error
                        raise RuntimeError("length() requiere un string o array")
            
            # Llamar a la función built-in
            result = self.constructor_ir.call(func, args_vals, name="calltmp")
            
            # Convertir el resultado de float a integer si la función retorna float pero se espera integer
            # (Esto puede pasar si sqrt/abs se usan en contextos donde se espera integer)
            # Por ahora, retornamos el resultado tal cual
            
            return result
        
        # Función definida por el usuario
        if func_name not in self.funciones_llvm:
            raise RuntimeError(f"Función '{func_name}' no encontrada")
        
        func = self.funciones_llvm[func_name]
        
        # Evaluar argumentos
        args_vals = []
        for arg in n.args:
            args_vals.append(self.visit(arg))
        
        return self.constructor_ir.call(func, args_vals, name="calltmp")

def generate_code(node):
    generator = IRGenerator()
    generator.visit(node)
    return str(generator.llvm_module)
