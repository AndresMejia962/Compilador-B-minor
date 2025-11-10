# errors.py
'''
Sistema de manejo de errores para el compilador.

Uno de los aspectos críticos en el desarrollo de compiladores
es proporcionar mensajes de error claros y precisos. Este módulo
centraliza las funciones básicas de gestión de errores.
Permite reportar errores de manera consistente. Permite verificar
si existen errores en el proceso de compilación.

Puede extenderse en el futuro para ofrecer más funcionalidades.

Contador global que registra la cantidad de errores encontrados.
El compilador utiliza este valor para determinar si debe abortar.
'''
from rich import print

_error_count = 0

def error(error_message, line_number=None):
	global _error_count
	if line_number:
		print(f'{line_number}: [red]{error_message}[/red]')
	else:
		print(f"[red]{error_message}[/red]")
	_error_count += 1
	
def errors_detected():
	return _error_count
	
def clear_errors():
	global _error_count
	_error_count = 0