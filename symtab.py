# symtab.py
from rich.table   import Table
from rich.console import Console
from rich         import print

from model        import Node

class SymbolTable:
	'''
	Estructura de datos para gestionar símbolos del compilador.
	Implementa un diccionario que mapea nombres de símbolos a sus
	correspondientes nodos AST (declaraciones o definiciones).
	Cada contexto de código (función, bloque, etc.) posee su propia
	tabla de símbolos. Las tablas pueden anidarse para reflejar
	la estructura del código, y las búsquedas se propagan hacia
	arriba a través de la jerarquía para implementar el alcance léxico.
	'''
	class DuplicateSymbolError(Exception):
		'''
		Excepción lanzada al intentar insertar un símbolo que ya
		existe en la tabla. 'Definido' se refiere a que ya se ha
		reservado espacio para el símbolo (estilo C), no solo
		declarado.
		'''
		pass
		
	class TypeConflictError(Exception):
		'''
		Excepción lanzada cuando se intenta agregar un símbolo
		con un nombre existente pero con un tipo diferente.
		'''
		pass
		
	def __init__(self, table_name, parent_table=None):
		'''
		Inicializa una tabla de símbolos vacía, opcionalmente
		vinculada a una tabla padre.
		'''
		self.name = table_name
		self.symbols = {}
		self.parent = parent_table
		if self.parent:
			self.parent.children.append(self)
		self.children = []

	def __getitem__(self, symbol_name):
		return self.symbols[symbol_name]

	def __setitem__(self, symbol_name, symbol_value):
		self.symbols[symbol_name] = symbol_value

	def __delitem__(self, symbol_name):
		del self.symbols[symbol_name]

	def __contains__(self, symbol_name):
		if symbol_name in self.symbols:
			return self.symbols[symbol_name]
		return False

	def add(self, symbol_name, symbol_value):
		'''
		Inserta un símbolo en la tabla con el valor especificado.
		El valor normalmente es un nodo AST que representa una
		declaración o definición (variable, función, etc.)
		'''
		if symbol_name in self.symbols:
			# Comparar sym_type si existe, sino comparar type
			existing_type = getattr(self.symbols[symbol_name], 'sym_type', getattr(self.symbols[symbol_name], 'type', None))
			new_type = getattr(symbol_value, 'sym_type', getattr(symbol_value, 'type', None))
			if existing_type != new_type:
				raise SymbolTable.TypeConflictError()
			else:
				raise SymbolTable.DuplicateSymbolError()
		self.symbols[symbol_name] = symbol_value
		
	def get(self, symbol_name):
		'''
		Busca un símbolo por nombre en esta tabla y en las tablas
		padre si no se encuentra localmente, implementando el
		alcance léxico.
		'''
		if symbol_name in self.symbols:
			return self.symbols[symbol_name]
		elif self.parent:
			return self.parent.get(symbol_name)
		return None
		
	def print(self):
		display_table = Table(title = f"Symbol Table: '{self.name}'")
		display_table.add_column('key', style='cyan')
		display_table.add_column('value', style='bright_green')
		
		for key, val in self.symbols.items():
			display_value = f"{val.__class__.__name__}({val.name})" if isinstance(val, Node) else f"{val}"
			display_table.add_row(key, display_value)
		print(display_table, '\n')
		
		for child_table in self.children:
			child_table.print()
