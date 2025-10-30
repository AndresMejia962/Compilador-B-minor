# symtab.py
from rich.table   import Table
from rich.console import Console
from rich         import print

from model        import Node

class TablaSimbolos:
	'''
	Una tabla de símbolos. Este es un objeto simple que solo
	mantiene una hashtable (dict) de nombres de símbolos y los
	nodos de declaración o definición de funciones a los que se
	refieren.
	Hay una tabla de símbolos separada para cada elemento de
	código que tiene su propio contexto (por ejemplo cada función,
	tendrá su propia tabla de símbolos). Como resultado,
	las tablas de símbolos se pueden anidar si los elementos de
	código están anidados y las búsquedas de las tablas de
	símbolos se repetirán hacia arriba a través de los padres
	para representar las reglas de alcance léxico.
	'''
	class ErrorSimboloDefinido(Exception):
		'''
		Se genera una excepción cuando el código intenta agregar
		un símbolo a una tabla donde el símbolo ya se ha definido.
		Tenga en cuenta que 'definido' se usa aquí en el sentido
		del lenguaje C, es decir, 'se ha asignado espacio para el
		símbolo', en lugar de una declaración.
		'''
		pass
		
	class ErrorConflictoSimbolo(Exception):
		'''
		Se produce una excepción cuando el código intenta agregar
		un símbolo a una tabla donde el símbolo ya existe y su tipo
		difiere del existente previamente.
		'''
		pass
		
	def __init__(self, nombre, padre=None):
		'''
		Crea una tabla de símbolos vacía con la tabla de
		símbolos padre dada.
		'''
		self.nombre = nombre
		self.entradas = {}
		self.padre = padre
		if self.padre:
			self.padre.hijos.append(self)
		self.hijos = []

	def __getitem__(self, nombre):
		return self.entradas[nombre]

	def __setitem__(self, nombre, valor):
		self.entradas[nombre] = valor

	def __delitem__(self, nombre):
		del self.entradas[nombre]

	def __contains__(self, nombre):
		return nombre in self.entradas

	def agregar(self, nombre, valor):
		'''
		Agrega un símbolo con el valor dado a la tabla de símbolos.
		El valor suele ser un nodo AST que representa la declaración
		o definición de una función, variable (por ejemplo, Declaración
		o FuncDeclaration)
		'''
		if nombre in self.entradas:
			if self.entradas[nombre].type != valor.type:
				raise TablaSimbolos.ErrorConflictoSimbolo()
			else:
				raise TablaSimbolos.ErrorSimboloDefinido()
		self.entradas[nombre] = valor
		
	def obtener(self, nombre):
		'''
		Recupera el símbolo con el nombre dado de la tabla de
		símbolos, recorriendo hacia arriba a través de las tablas
		de símbolos principales si no se encuentra en la actual.
		'''
		if nombre in self.entradas:
			return self.entradas[nombre]
		elif self.padre:
			return self.padre.obtener(nombre)
		return None
		
	def imprimir(self):
		print(f"\n{'='*60}")
		print(f"REGISTRO DE SIMBOLOS: {self.nombre.upper()}")
		print(f"{'='*60}")
		
		if not self.entradas:
			print("   [AVISO] No hay simbolos registrados en este ambito")
		else:
			for i, (clave, valor) in enumerate(self.entradas.items(), 1):
				if isinstance(valor, Node):
					tipo_simbolo = valor.__class__.__name__
					nombre_simbolo = getattr(valor, 'name', 'sin_nombre')
					print(f"   {i:2d}. * {clave:<15} -> {tipo_simbolo}({nombre_simbolo})")
				else:
					print(f"   {i:2d}. * {clave:<15} -> {valor}")
		
		print(f"{'='*60}\n")
		
		for hijo in self.hijos:
			hijo.imprimir()
