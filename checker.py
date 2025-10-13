# checker.py
'''
Este archivo contendrá la parte de verificación/validación de tipos
del compilador.  Hay varios aspectos que deben gestionarse para
que esto funcione. Primero, debe tener una noción de "tipo" en su compilador.
Segundo, debe administrar los entornos y el alcance para manejar los
nombres de las definiciones (variables, funciones, etc.).

Una clave para esta parte del proyecto es realizar pruebas adecuadas.
A medida que agregue código, piense en cómo podría probarlo.
'''
from rich    import print
from typing  import Union, List

from errors  import error, errors_detected
from model   import *
from symtab  import Symtab
from typesys import typenames, check_binop, check_unaryop, CheckError

	
class Check(Visitor):
	@classmethod
	def checker(cls, n: Program):
		checker = cls()
		
		# Crear una nueva tabla de simbolos
		env = Symtab('global')
		
		# Visitar todas las declaraciones
		for decl in n.body:
			decl.accept(checker, env)
		return env

	# --- Statements
	
	def visit(self, n: Assignment, env: Symtab):
		# Validar n.loc (location) y n.expr
		n.loc.accept(self, env)
		n.expr.accept(self, env)

		# Type inference on memory locations
		if n.loc.type == '<infer>':
			n.loc.type = n.expr.type

		if n.loc.type != n.expr.type:
			error(f'Error de tipo. {n.loc.type} != {n.expr.type}', n.lineno)
			return

		# ¿Qué pasa con la mutabilidad? ¿Quién es responsable? Yo.
		if not n.loc.mutable:
			error(f"No se puede asignar a una 'loc' inmutable", n.lineno)
		
		n.loc.usage = 'store'
		
	def visit(self, n: PrintStmt, env: Symtab):
		# visitar n.exprs
		for expr in n.exprs:
			expr.accept(self, env)
			if expr.type == '<infer>':
				error("No se puede inferir el tipo de expresión en Print", n.lineno)
	
	def visit(self, n: IfStmt, env: Symtab):
		# Visitar n.cond (validar tipos)
		n.cond.accept(self, env)
		if n.cond.type == '<infer>':
			n.test.type = 'boolean'
		if n.cond.type != 'boolean':
			error(f"cond en IF debe ser 'boolean'. Se obtuvo {n.cond.type}", n.lineno)
		
		# Visitar n.cons (consecuente)
		for stmt in n.cons:
			stmt.accept(self, env)
			
		# Visitar n.alt (alterno)
		if n.alt:
			for stmt in n.alt:
				stmt.accept(self, env)

	def visit(self, n: ForStmt, env: Symtab):
		# Visitar n.init
		if n.init: n.init.accept(self, env)
		if n.cond:
			n.cond.accept(self, env)
			if n.cond.type == '<infer>':
				n.cond.type = 'boolean'
			if n.cond.type != 'boolean':
				error(f"test en ForStmt debe ser 'boolean'. Se obtuvo {n.cond.type}", n.lineno)
		
		
	def visit(self, n: WhileStmt, env: Symtab):
		# Visitar n.cond (validar tipos)
		n.cond.accept(self, env)
		if n.cond.type == '<infer>':
			n.cond.type = 'bool'
		if n.cond.type != 'bool':
			error(f"test en While debe ser 'bool'. Se obtuvo {n.cond.type}", n.lineno)
	
		# Marcar que se esta dentro de un While
		env['$loop'] = True
		
		# Visitar n.body
		for b in n.body:
			b.accept(self, env)
		
		# Deshabilitar marca del While
		env['$loop'] = False

	'''
	def visit(self, n: Union[Break, Continue], env: Symtab):
		# Verificar que esta dentro de un ciclo while
		name = n.__class__.__name__.lower()
		if '$loop' not in env:
			error(f"'{name}' por fuera de un loop", n.lineno)
	'''

	def visit(self, n: ReturnStmt, env: Symtab):
		# Visitar n.expr y obtene tipo
		n.expr.accept(self, env)
		
		# Obtener la funcion
		if '$func' not in env:
			error("'Return' usado por fuera de una funcion", n.lineno)
		else:
			func = env.get('$func')
			if func.type == 'void':
				pass
			elif func.type != n.expr.type:
				error(f"Error de tipo. return {func.type} != {n.expr.type}", n.lineno)

	# --- Declaration
	
	def visit(self, n: Declaration, env: Symtab):
		self.check(n, env)
		
		# Todas las definiciones tienen nombre. Tras la 
		# comprobación, el nombre debe formar parte del 
		# entorno (de ahí el propósito de definirlo).
		assert n.name in env
	
		if '$func' in env:
			n.scope = 'local'
		else:
			n.scope = 'global'

	def check(self, n: VarDecl, env: Symtab):
		if n.value:
			n.value.accept(self, env)
			# If there is no type set, copy it from the value
			if not n.type:
				n.type = n.value.type
			
			if n.value.type == '<infer>':
				n.value.type == n.type
				
			if n.value.type == '<infer>':
				error(f"No se puede inferir tipo de {n.name}", n.lineno)
			
			# Verify types match up if a value was provided.
			# Could have:  var x int = 3.4;    // Error.
			if n.type != n.value.type:
				error(f'Error de tipo en declaración. {n.type} != {n.value.type}', n.lineno)

		# Agregar n.name a symtab
		try:
			env.add(n.name, n)
		except Symtab.SymbolConflictError as ex:
			error(f"La Variable '{n.name}' ya definida y con tipo de dato diferente", n.lineno)
		except Symtab.SymbolDefinedError as exññ:
			error(f"La Variable '{n.name}' ya definida", n.lineno)


	def check(self, n:ArrayDecl, env:Symtab):
		...

	def check(self, n:FuncDecl, env:Symtab):
		# Guardar la función en symtab actual
		try:
			env.add(n.name, n)
		except Symtab.SymbolConflictError as ex:
			error(f"La Función '{n.name}' ya definida y con tipo de dato diferente", n.lineno)
		except Symtab.SymbolDefinedError as exññ:
			error(f"La Función '{n.name}' ya definida", n.lineno)
		
		# Crear una nueva symtab (local) para Function
		env = Symtab(n.name, env)
		
		# Magic variable that references the current function
		env['$func'] = n
		
		# Agregar todos los n.params dentro de symtab
		for p in n.parms:
			p.accept(self, env)
			
		# Visitar n.stmts
		if n.body:
			for stmt in n.body:
				stmt.accept(self, env)
		
		env['$func'] = None


	def check(self, n:VarParm, env:Symtab):
		# Guardar Parameter (name, type) en symtab
		try:
			env.add(n.name, n)
		except Symtab.SymbolConflictError as ex:
			error(f"El Parámetro '{n.name}' ya definido y con tipo de dato diferente", n.lineno)
		except Symtab.SymbolDefinedError as exññ:
			error(f"El Parámetro '{n.name}' ya definido", n.lineno)

	def check(self, n:VarParm, env:Symtab):
		...

	# --- Expressions
	
	def visit(self, n:Literal, env:Symtab):
		# No hay nada que hacer. Los literales son
		# primitivos básicos. Ya tienen un tipo
		# definido en el archivo model.py.
		pass
		
	def visit(self, n:BinOp, env:Symtab):
		# Visitar n.left y n.right
		n.left.accept(self, env)
		n.right.accept(self, env)
		
		# Handle type-inference of memory locations
		if n.left.type == '<infer>':
			n.left.type = n.right.type
		
		if n.right.type == '<infer>':
			n.right.type = n.left.type
		
		# Verificar compatibilidad de tipos
		n.type = check_binop(n.oper, n.left.type, n.right.type) 
		if not n.type and (n.left.type and n.right.type):
			# Question: How are errors reported?
			error(f'Error de tipo: {n.left.type} {n.oper} {n.right.type}', n.lineno)

	def visit(self, n:UnaryOp, env:Symtab):
		# Visitar n.expr (operando)
		n.expr.accept(self, env)
		
		# Validar si es un operador unario valido
		n.type = check_unaryop(n.oper, n.expr.type)
		if not n.type and n.expr.type:
			error(f'Error de tipo: {n.oper} {n.expr.type}', n.lineno)

	'''
	def visit(self, n:TypeCast, env:Symtab):
		# Visitar n.expr para validar
		n.expr.accept(self, env)
		
		# Ya se tiene un tipo establecido (el objetivo de
		# la conversión).  Se debe comprobar si la 
		# expresión asociada se puede convertir a ese 
		# tipo.
		# x = int(3.4);
		
		# retornar el tipo del cast n.type
		if n.expr.type == '<infer>':
			n.expr.type = n.type
	'''
	
	def visit(self, n:FuncCall, env:Symtab):
		# Validar si n.name existe
		func = env.get(n.name)
		if func is None:
			error(f"Function {n.name} no definida", n.lineno)
			return
		
		# La funcion debe ser una Function
		if not isinstance(func, Function):
			error(f'{n.name} no es función', n.lineno)
			# Si no es una función, no es posible realizar más comprobaciones
			return
		
		# El número de argumentos de la función debe coincidir con los parámetros
		if len(n.args) != len(func.parms):
			error(f'Se esperaban {len(func.parms)} argumentos. Se obtubieron {len(node.args)}.', n.lineno)

		# Los tipos de argumentos de la función deben coincidir con los tipos de parámetros
		for pos, (parm, arg) in enumerate(zip(func.parms, n.args), 1):
			arg.accept(self, env)
			if parm.type != arg.type:
				error(f"Error de tipo en el argumento {pos}. {parm.type} != {arg.type}", parm.lineno)
		
		# El tipo de resultado es el tipo de retorno de la función
		n.type = func.type

	def visit(self, n:Location, env:Symtab):
		self.check(n, env)
		
		# Las ubicaciones deben tener mutabilidad indicada (para la asignación)
		assert hasattr(n, 'mutable')

	def check(self, n:VarLoc, env:Symtab):
		# Verificar si n.name existe symtab
		decl = env.get(n.name)
		
		if not decl:
			error(f"Nombre no definido {n.name!r}", n.lineno)
			return
		
		elif isinstance(decl, FuncDecl):
			error("Function no es first-class", n.lineno)
			return 
		
		# Propaga informacion sobre tipo
		n.type = decl.type
		
		#n.mutable = not isinstance(decl, Union[Constant, FuncDecl])
		n.mutable = not isinstance(decl, FuncDecl)
		
		
	'''
	def check(self, n:MemoryLocation, env:Symtab):
		# Visitar n.address (expression) para validar
		n.address.accept(self, env)
		if n.address.type != 'int':
			error(f"Dirección de Memoria debe ser 'integer'", n.lineno)
		
		# Retornar el tipo de datos
		n.type = '<infer>'
		n.mutable = True
	'''
		
if __name__ == '__main__':
	import sys
	
	if sys.platform != 'ios':
		
		if len(sys.argv) != 2:
			raise SystemExit("Usage: python gcheck.py <filename>")
		
		filename = sys.argv[1]
		
	else:
		from File_Picker import file_picker_dialog
	
		filename = file_picker_dialog(
			title='Seleccionar una archivo',
			root_dir='./test',
			file_pattern='^.*[.]bminor'
		)

	if filename:
		from parser import parse
		
		txt = open(filename, encoding='utf-8').read()
		top = parse(txt)
		env = Check.checker(top)
		
		if not errors_detected():
			env.print()
