# codegen.py
# ----------------------------------------------------------------------
# Generador de Código LLVM
#
# Este visitante recorre el AST (que ya ha sido anotado por
# checker.py) y genera el Código Intermedio (IR) de LLVM
# usando llvmlite.
# ----------------------------------------------------------------------

from llvmlite import ir
from model import *
from model import Visitor  

class LLVMCodeGenerator(Visitor):
    '''
    Clase visitante para generar el IR de LLVM.
    Hereda de tu 'model.Visitor'.
    '''
    def __init__(self):
        # Módulo principal de LLVM
        self.module = ir.Module(name='bminor')

        # Definición de tipos LLVM
        self.int_type = ir.IntType(32)
        self.bool_type = ir.IntType(1)
        self.void_type = ir.VoidType()

        # Mapa de tipos: de nombre de tipo de bminor (string) a tipo LLVM
        self.typemap = {
            'integer': self.int_type,
            'boolean': self.bool_type,
        }

        # --- Configuración de la función 'main' ---
        # B-minor se compilará a una única función 'main'
        main_func_type = ir.FunctionType(self.void_type, [])
        self.function = ir.Function(self.module, main_func_type, name='main')
        
        # Bloque de entrada (entry) para 'main'
        entry_block = self.function.append_basic_block(name='entry')
        
        # Constructor de IR (IRBuilder). Apunta al final del bloque 'entry'.
        self.builder = ir.IRBuilder(entry_block)

        # --- Tabla de Símbolos de LLVM ---
        # Esto mapea nombres de variables de bminor (str) a sus 
        # punteros 'alloca' (ir.AllocaInstr) en el stack.
        self.vars = {}

        # --- Declarar Funciones de Runtime ---
        # Declara las funciones que el JIT buscará (ej. _printi).
        # El JIT las conectará a las funciones de Python.
        self._declare_runtime_functions()

    def _declare_runtime_functions(self):
        # void _printi(int)
        printi_type = ir.FunctionType(self.void_type, [self.int_type])
        self._printi = ir.Function(self.module, printi_type, name='_printi')
        
        # void _printb(bool)
        printb_type = ir.FunctionType(self.void_type, [self.bool_type])
        self._printb = ir.Function(self.module, printb_type, name='_printb')

    # =====================================================================
    # Nodos de Programa y Bloques
    # =====================================================================

    def visit(self, n: Program):
        '''
        Punto de entrada. Visita todas las sentencias del programa.
        '''
        for stmt in n.body:
            self.visit(stmt)
        
        # Terminar la función 'main' con un 'ret void'
        self.builder.ret_void()

    def visit(self, n: BlockStmt):
        '''
        Visita una secuencia de sentencias dentro de un bloque.
        '''
        for stmt in n.statements:
            self.visit(stmt)

    # =====================================================================
    # Nodos de Sentencias (Declaración, Asignación, Print)
    # =====================================================================

    def visit(self, n: VarDecl):
        '''
        Genera código para una declaración de variable.
        Ej: x: integer = 5;
        '''
        var_name = n.name
        
        # Usar el tipo anotado por el 'checker'
        var_type_bminor = n.sym_type 
        var_type_llvm = self.typemap[var_type_bminor]

        # --- Patrón 'alloca' ---
        # 1. Reservar espacio en el stack (alloca)
        #    Siempre se hace en el bloque 'entry' para optimización.
        with self.builder.goto_entry_block():
            var_ptr = self.builder.alloca(var_type_llvm, name=var_name)
        
        # 2. Guardar el puntero en nuestra tabla de símbolos de LLVM
        self.vars[var_name] = var_ptr

        # 3. Si hay un valor inicial (ej. x = 5), generar 'store'
        if n.value:
            # Visita la expresión para obtener el valor LLVM
            init_val = self.visit(n.value)
            # Almacena (store) el valor en el puntero
            self.builder.store(init_val, var_ptr)

    def visit(self, n: Assignment):
        '''
        Genera código para una asignación.
        Ej: x = 10;
        '''
        # 1. Visita la parte derecha (RHS) para obtener el valor LLVM
        value_llvm = self.visit(n.value)

        # 2. Busca el puntero de la variable (LHS)
        #    (Asumimos VarLocation para este subconjunto)
        var_name = n.location.name
        var_ptr = self.vars[var_name]

        # 3. Almacena (store) el valor en el puntero
        self.builder.store(value_llvm, var_ptr)

    def visit(self, n: PrintStmt):
        '''
        Genera código para print.
        Ej: print(x, 10, true);
        '''
        for value_node in n.values:
            # 1. Visita la expresión para obtener el valor LLVM
            value_llvm = self.visit(value_node)
            
            # 2. Lee el tipo anotado por el 'checker'
            node_type = value_node.type 

            # 3. Llama a la función de runtime correcta
            if node_type == 'integer':
                self.builder.call(self._printi, [value_llvm])
            elif node_type == 'boolean':
                self.builder.call(self._printb, [value_llvm])
            # (Agregar más 'elif' cuando soportes más tipos)

    # =====================================================================
    # Nodos de Expresiones (Literales, Variables, Operaciones)
    # =====================================================================

    def visit(self, n: Integer):
        '''
        Genera un literal de entero constante.
        '''
        return ir.Constant(self.int_type, n.value)

    def visit(self, n: Boolean):
        '''
        Genera un literal de booleano constante.
        '''
        return ir.Constant(self.bool_type, n.value)

    def visit(self, n: VarLocation):
        '''
        Genera código para leer (cargar) una variable.
        Ej: ... = x + 5; (esto es el 'x')
        '''
        var_name = n.name
        
        # 1. Busca el puntero de la variable
        var_ptr = self.vars[var_name]
        
        # 2. Carga (load) el valor desde el puntero
        return self.builder.load(var_ptr, name=var_name + "_val")

    def visit(self, n: BinOper):
        '''
        Genera código para operaciones binarias.
        (Solo soporta 'integer' para este subconjunto)
        '''
        # 1. Visita recursivamente los hijos
        left_val = self.visit(n.left)
        right_val = self.visit(n.right)

        # 2. Lee el tipo (anotado por el checker) para saber qué hacer
        op_type = n.left.type 

        if op_type == 'integer':
            # Operaciones aritméticas de enteros
            if n.op == '+':
                return self.builder.add(left_val, right_val, name='add_tmp')
            if n.op == '-':
                return self.builder.sub(left_val, right_val, name='sub_tmp')
            if n.op == '*':
                return self.builder.mul(left_val, right_val, name='mul_tmp')
            if n.op == '/':
                return self.builder.sdiv(left_val, right_val, name='div_tmp')
            if n.op == '%':
                return self.builder.srem(left_val, right_val, name='srem_tmp')
            

    def visit(self, n: UnaryOper):
        '''
        Genera código para operaciones unarias.
        (Solo soporta '+' y '-' para este subconjunto)
        '''
        # 1. Visita recursivamente el operando
        operand_val = self.visit(n.expr)
        
        # 2. Genera la operación
        if n.op == '-':
            # Implementar 'negación' como '0 - valor'
            zero = ir.Constant(self.int_type, 0)
            return self.builder.sub(zero, operand_val, name='neg_tmp')
        if n.op == '+':
            # '+x' es simplemente 'x'
            return operand_val
        
      