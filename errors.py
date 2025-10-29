# errors.py
'''
Sistema de gestión de errores del compilador.

Este módulo proporciona un sistema centralizado para el manejo y reporte
de errores durante el proceso de compilación. Permite registrar errores,
contar el total de errores encontrados y limpiar el contador cuando sea necesario.

Características:
- Contador global de errores
- Formato de mensajes personalizado
- Soporte para números de línea
'''

from rich import print
from rich.panel import Panel
from rich.text import Text
import datetime

_contador_errores = 0
_lista_errores = []

def registrar_error(mensaje, numero_linea=None):
	global _contador_errores, _lista_errores
	
	timestamp = datetime.datetime.now().strftime("%H:%M:%S")
	
	if numero_linea:
		mensaje_completo = f"[{timestamp}] Linea {numero_linea}: {mensaje}"
		texto_error = Text(f"ERROR EN LINEA {numero_linea}", style="bold red")
		panel = Panel(
			f"[bold red]{mensaje}[/bold red]\n[dim]Tiempo: {timestamp}[/dim]",
			title=texto_error,
			border_style="red",
			padding=(1, 2)
		)
	else:
		mensaje_completo = f"[{timestamp}] {mensaje}"
		texto_error = Text("ERROR GENERAL", style="bold red")
		panel = Panel(
			f"[bold red]{mensaje}[/bold red]\n[dim]Tiempo: {timestamp}[/dim]",
			title=texto_error,
			border_style="red",
			padding=(1, 2)
		)
	
	print(panel)
	_lista_errores.append(mensaje_completo)
	_contador_errores += 1

def obtener_total_errores():
	return _contador_errores

def limpiar_errores():
	global _contador_errores, _lista_errores
	_contador_errores = 0
	_lista_errores.clear()

def mostrar_resumen_errores():
	if _contador_errores > 0:
		print(f"\n{'='*50}")
		print(f"RESUMEN DE ERRORES ENCONTRADOS: {_contador_errores}")
		print(f"{'='*50}")
		for i, error in enumerate(_lista_errores, 1):
			print(f"   {i:2d}. {error}")
		print(f"{'='*50}\n")

# Mantener compatibilidad con el código existente
def error(message, lineno=None):
	registrar_error(message, lineno)

def errors_detected():
	return obtener_total_errores()

def clear_errors():
	limpiar_errores()