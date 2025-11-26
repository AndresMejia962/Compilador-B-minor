# interp.py

'''
Tree-walking interpreter
'''

from collections import ChainMap
from rich import print

from model import *
from checker import SemanticAnalyzer
from typesys import check_unaryop

# Importar sistemas de debugging y profiling
try:
    from debugger import Debugger, Profiler, RuntimeValidator, ErrorHandler
except ImportError:
    # Si debugger.py no existe, crear clases dummy
    class Debugger:
        def __init__(self, enabled=False): pass
        def check_breakpoint(self, *args): return False
        def trace_execution(self, *args): pass
    class Profiler:
        def __init__(self, enabled=False): pass
        def start(self): pass
        def end(self): pass
        def enter_function(self, *args): return None
        def exit_function(self, *args): pass
        def get_report(self): return ""
    class RuntimeValidator:
        def __init__(self, enabled=True): pass
        def validate_division_by_zero(self, *args): pass
        def validate_array_index(self, *args): pass
        def validate_type(self, *args): pass
    class ErrorHandler:
        def __init__(self): self.call_stack = []
        def push_context(self, *args): pass
        def pop_context(self): pass
        def format_error(self, *args): return str(args[0])

# Importar desde nuestro módulo builtins (usando importlib para evitar conflicto con builtins estándar)
import importlib.util
import os

# Obtener la ruta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))
builtins_path = os.path.join(current_dir, "builtins.py")

spec = importlib.util.spec_from_file_location("bminor_builtins", builtins_path)
bminor_builtins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bminor_builtins)

builtins = bminor_builtins.builtins
consts = bminor_builtins.consts
CallError = bminor_builtins.CallError

# Veracidad en bminor

def _is_truthy(value):
  if isinstance(value, bool):
    return value
  elif value is None:
    return False
  else:
    return True


class ReturnException(Exception):
  def __init__(self, value):
    self.value = value


class BreakException(Exception):
  pass


class ContinueException(Exception):
  pass


class BminorExit(BaseException):
  pass


class AttributeError(Exception):
  pass


class Context:
  """Contexto para manejo de errores"""
  def __init__(self):
    self.errors = []
    self.source_lines = {}
    
  def error(self, position, message):
    """Reporta un error"""
    lineno = getattr(position, 'lineno', 0)
    self.errors.append((lineno, message))
    print(f"[red]Error en línea {lineno}: {message}[/red]")
    
  @property
  def have_errors(self):
    return len(self.errors) > 0
    
  def find_source(self, node):
    """Encuentra el código fuente de un nodo"""
    return getattr(node, 'name', str(node))


class Function:
  def __init__(self, node, env):
    self.node = node
    self.env = env

  @property
  def arity(self) -> int:
    return len(self.node.params)

  def __call__(self, interp, *args):
    newenv = self.env.new_child()
    for name, arg in zip(self.node.params, args):
      newenv[name.name] = arg

    oldenv = interp.env
    interp.env = newenv
    try:
      self.node.body.accept(interp)
      result = None
    except ReturnException as e:
      result = e.value
    finally:
      interp.env = oldenv
    return result

  def bind(self, instance):
    env = self.env.new_child()
    env['this'] = instance
    return Function(self.node, env)


class Interpreter(Visitor):
  def __init__(self, ctxt=None, debug=False, profile=False):
    self.ctxt = ctxt or Context()
    self.env = ChainMap()
    self.check_env = ChainMap()
    self.localmap = {}
    
    # Sistemas de debugging y profiling
    self.debugger = Debugger(enabled=debug)
    self.profiler = Profiler(enabled=profile)
    self.validator = RuntimeValidator(enabled=True)
    self.error_handler = ErrorHandler()
    
    if profile:
      self.profiler.start()

  def _validate_numeric_operands(self, node, left, right=None):
    """Valida que los operandos sean numéricos (int o float)."""
    if not isinstance(left, (int, float)):
      self.error(node, f"Operando izquierdo en '{node.op}' debe ser numérico, se obtuvo {type(left).__name__}")
    
    if right is not None and not isinstance(right, (int, float)):
      self.error(node, f"Operando derecho en '{node.op}' debe ser numérico, se obtuvo {type(right).__name__}")
    return True

  def _handle_inc_dec(self, node, delta, return_original=False):
    """Maneja la lógica común para incremento y decremento (++ y --)."""
    value = node.expr.accept(self)
    self._validate_numeric_operands(node, value)
    
    new_value = value + delta
    
    # Asignar el nuevo valor
    if isinstance(node.expr, VarLocation):
      self.env[node.expr.name] = new_value
    elif isinstance(node.expr, ArraySubscript):
      # Obtener el array del entorno
      if isinstance(node.expr.location, VarLocation):
        arr_name = node.expr.location.name
        arr = self.env[arr_name]
        idx = node.expr.index.accept(self)
        
        # Validaciones extra para arrays
        if not isinstance(arr, list):
           self.error(node, f"'{arr_name}' no es un array")
        if not isinstance(idx, int):
           self.error(node, f"El índice debe ser un entero")
        if idx < 0 or idx >= len(arr):
           self.error(node, f"Índice fuera de rango: {idx}")
           
        arr[idx] = new_value
        # No es estrictamente necesario reasignar arr a self.env si es mutable (lista),
        # pero es más seguro si la implementación cambia.
        self.env[arr_name] = arr
      else:
        self.error(node, "Solo se soportan incrementos/decrementos en variables o arrays simples")
    else:
      self.error(node, "El operando de incremento/decremento debe ser un lvalue (variable o elemento de array)")
      
    return value if return_original else new_value

  def error(self, position, message):
    """Manejo mejorado de errores con stack trace"""
    error_msg = self.error_handler.format_error(
      Exception(message), 
      position
    )
    self.ctxt.error(position, message)
    print(error_msg)
    raise BminorExit()

  # Punto de entrada alto-nivel
  def interpret(self, node):
    for name, cval in consts.items():
      self.check_env[name] = cval
      self.env[name] = cval

    for name, func in builtins.items():
      self.check_env[name] = func
      self.env[name] = func

    try:
      SemanticAnalyzer.checker(node)
      if not self.ctxt.have_errors:
        # Ejecutar todas las declaraciones
        node.accept(self)
        # Buscar y ejecutar main si existe
        if 'main' in self.env:
          main_func = self.env['main']
          if callable(main_func) and hasattr(main_func, 'arity'):
            # Profiling: registrar main
            main_start = None
            if self.profiler.enabled:
              main_start = self.profiler.enter_function('main')
              self.error_handler.push_context('main', 0)
            
            try:
              main_func(self)
            finally:
              if self.profiler.enabled:
                self.profiler.exit_function('main', main_start)
                self.error_handler.pop_context()
        
        # Finalizar profiling
        if self.profiler.enabled:
          self.profiler.end()
          self.profiler.get_report()
    except BminorExit as e:
      if self.profiler.enabled:
        self.profiler.end()
      pass

  # Declarations
  def visit(self, node: FuncDecl):
    func = Function(node, self.env)
    self.env[node.name] = func
    
    # Debugging
    if self.debugger.enabled:
      self.debugger.trace_execution(node.lineno, 'FuncDecl', self.env)

  def visit(self, node: VarDecl):
    if node.value:
      expr = node.value.accept(self)
    else:
      expr = None
    self.env[node.name] = expr

  def visit(self, node: ArrayDecl):
    if node.value:
      values = [val.accept(self) for val in node.value]
    else:
      values = []
    self.env[node.name] = values

  def visit(self, node: Program):
    for stmt in node.body:
      stmt.accept(self)

  def visit(self, node: BlockStmt):
    # Crear un nuevo entorno hijo que hereda del actual
    newenv = self.env.new_child()
    oldenv = self.env
    self.env = newenv
    try:
      for stmt in node.statements:
        stmt.accept(self)
    finally:
      # Restaurar el entorno anterior
      # Las variables del bloque se mantienen en newenv que es hijo de oldenv
      self.env = oldenv

  # Statements
  def visit(self, node: PrintStmt):
    for expr in node.values:
      value = expr.accept(self)
      if isinstance(value, str):
        value = value.replace('\\n', '\n')
        value = value.replace('\\t', '\t')
      print(value, end='')
    print()  # Nueva línea al final

  def visit(self, node: WhileStmt):
    while _is_truthy(node.condition.accept(self)):
      try:
        node.body.accept(self)
      except BreakException:
        break
      except ContinueException:
        continue

  def visit(self, node: DoWhileStmt):
    while True:
      try:
        node.body.accept(self)
      except BreakException:
        break
      except ContinueException:
        pass
      if not _is_truthy(node.condition.accept(self)):
        break

  def visit(self, node: ForStmt):
    if node.init:
      node.init.accept(self)
    while _is_truthy(node.condition.accept(self)):
      try:
        node.body.accept(self)
      except BreakException:
        break
      except ContinueException:
        pass
      if node.update:
        node.update.accept(self)

  def visit(self, node: IfStmt):
    expr = node.condition.accept(self)
    if _is_truthy(expr):
      node.true_body.accept(self)
    elif node.false_body:
      node.false_body.accept(self)

  def visit(self, node: ReturnStmt):
    # Ojo: node.value es opcional
    value = None if not node.value else node.value.accept(self)
    raise ReturnException(value)

  # Expressions
  def visit(self, node: BinOper):
    left = node.left.accept(self)
    right = node.right.accept(self)

    if node.op == '+':
      if isinstance(left, str) and isinstance(right, str):
        return left + right
      self._validate_numeric_operands(node, left, right)
      return left + right

    elif node.op == '-':
      self._validate_numeric_operands(node, left, right)
      return left - right

    elif node.op == '*':
      self._validate_numeric_operands(node, left, right)
      return left * right

    elif node.op == '/':
      self._validate_numeric_operands(node, left, right)
      # Validacion en tiempo de ejecucion
      self.validator.validate_division_by_zero(node, right)
      if isinstance(left, int) and isinstance(right, int):
        return left // right
      return left / right

    elif node.op == '%':
      self._validate_numeric_operands(node, left, right)
      # Validacion en tiempo de ejecucion
      self.validator.validate_division_by_zero(node, right)
      return left % right

    elif node.op == '^':
      self._validate_numeric_operands(node, left, right)
      return left ** right

    elif node.op == '==':
      return left == right

    elif node.op == '!=':
      return left != right

    elif node.op == '<':
      self._validate_numeric_operands(node, left, right)
      return left < right

    elif node.op == '>':
      self._validate_numeric_operands(node, left, right)
      return left > right

    elif node.op == '<=':
      self._validate_numeric_operands(node, left, right)
      return left <= right

    elif node.op == '>=':
      self._validate_numeric_operands(node, left, right)
      return left >= right

    elif node.op == '||':
      # Evaluación cortocircuitada: si left es verdadero, retorna left, sino evalúa right
      if _is_truthy(left):
        return left
      return node.right.accept(self)

    elif node.op == '&&':
      # Evaluación cortocircuitada: si left es falso, retorna left, sino evalúa right
      if not _is_truthy(left):
        return left
      return node.right.accept(self)

    else:
      raise NotImplementedError(f"Mal operador {node.op}")


  def visit(self, node: UnaryOper):
    expr_value = node.expr.accept(self)
    
    if node.op == '-':
      self._validate_numeric_operands(node, expr_value)
      return -expr_value
    elif node.op == '+':
      self._validate_numeric_operands(node, expr_value)
      return expr_value
    elif node.op == '!':
      return not _is_truthy(expr_value)
    else:
      raise NotImplementedError(f"Operador unario '{node.op}' no implementado")

  def visit(self, node: PreInc):
    # Pre-incremento: ++x
    return self._handle_inc_dec(node, 1, return_original=False)

  def visit(self, node: PreDec):
    # Pre-decremento: --x
    return self._handle_inc_dec(node, -1, return_original=False)

  def visit(self, node: PostInc):
    # Post-incremento: x++
    return self._handle_inc_dec(node, 1, return_original=True)

  def visit(self, node: PostDec):
    # Post-decremento: x--
    return self._handle_inc_dec(node, -1, return_original=True)

  def visit(self, node: Assignment):
    # Debugging
    if self.debugger.enabled:
      self.debugger.check_breakpoint(node.lineno, self.env)
      self.debugger.trace_execution(node.lineno, 'Assignment', self.env)
    value = node.value.accept(self)
    
    # Asignar a variable
    if isinstance(node.location, VarLocation):
      var_name = node.location.name
      # ChainMap busca automáticamente en los padres, pero para actualizar
      # necesitamos actualizar el mapa más cercano donde existe la variable
      # o crear la variable en el mapa actual si no existe
      if var_name in self.env:
        # Actualizar en el mapa más cercano donde existe
        for m in self.env.maps:
          if var_name in m:
            m[var_name] = value
            break
      else:
        # Crear en el mapa actual (el primero de la cadena)
        self.env.maps[0][var_name] = value
      return value
    
    # Asignar a elemento de array
    elif isinstance(node.location, ArraySubscript):
      # Obtener el array del entorno
      if isinstance(node.location.location, VarLocation):
        arr_name = node.location.location.name
        arr = self.env[arr_name]
        idx = node.location.index.accept(self)
        if not isinstance(arr, list):
          self.error(node, f"'{arr_name}' no es un array")
        if not isinstance(idx, int):
          self.error(node, f"El índice debe ser un entero")
        if idx < 0 or idx >= len(arr):
          self.error(node, f"Índice fuera de rango: {idx}")
        arr[idx] = value
        self.env[arr_name] = arr
        return value
      else:
        self.error(node, f"Asignación a array anidado no soportada")
    
    else:
      raise NotImplementedError(f"Tipo de asignación no soportado: {type(node.location)}")

  def visit(self, node: FuncCall):
    # Buscar la funcion en el entorno
    if node.name not in self.env:
      self.error(node, f"Funcion '{node.name}' no definida")
    
    callee = self.env[node.name]
    
    if not callable(callee):
      self.error(node, f'{node.name!r} no es invocable')

    args = [arg.accept(self) for arg in node.args]

    if hasattr(callee, 'arity') and callee.arity != -1 and len(args) != callee.arity:
      self.error(node, f"Esperado {callee.arity} argumentos, se recibieron {len(args)}")

    # Profiling: registrar llamada a funcion
    func_start_time = None
    if self.profiler.enabled and hasattr(callee, 'arity'):
      func_start_time = self.profiler.enter_function(node.name)
      self.error_handler.push_context(node.name, node.lineno)
    
    # Debugging
    if self.debugger.enabled:
      self.debugger.check_breakpoint(node.lineno, self.env)
      self.debugger.trace_execution(node.lineno, 'FuncCall', self.env)

    try:
      if hasattr(callee, '__call__') and hasattr(callee, 'arity'):
        result = callee(self, *args)
      else:
        result = callee(*args)
      
      # Profiling: registrar salida
      if self.profiler.enabled and hasattr(callee, 'arity'):
        self.profiler.exit_function(node.name, func_start_time)
        self.error_handler.pop_context()
      
      return result
    except CallError as err:
      if self.profiler.enabled:
        self.error_handler.pop_context()
      self.error(node, str(err))
    except Exception as e:
      if self.profiler.enabled:
        self.profiler.exit_function(node.name, func_start_time)
        self.error_handler.pop_context()
      raise

  def visit(self, node: VarLocation):
    if node.name not in self.env:
      self.error(node, f"Variable '{node.name}' no definida")
    return self.env[node.name]

  def visit(self, node: ArraySubscript):
    # Obtener el array del entorno
    if isinstance(node.location, VarLocation):
      arr_name = node.location.name
      if arr_name not in self.env:
        self.error(node, f"Array '{arr_name}' no definido")
      arr = self.env[arr_name]
    else:
      arr = node.location.accept(self)
    
    idx = node.index.accept(self)
    
    # Validacion en tiempo de ejecucion
    self.validator.validate_array_index(node, arr, idx)
    
    # Debugging
    if self.debugger.enabled:
      self.debugger.check_breakpoint(node.lineno, self.env)
      self.debugger.trace_execution(node.lineno, 'ArraySubscript', self.env)
    
    return arr[idx]

  # Literales
  def visit(self, node: Integer):
    return node.value

  def visit(self, node: Float):
    return node.value

  def visit(self, node: Boolean):
    return node.value

  def visit(self, node: Char):
    return node.value

  def visit(self, node: String):
    return node.value

