# debugger.py
"""
Sistema de debugging y profiling para el interprete B-Minor
"""
import time
import traceback
from collections import defaultdict
from typing import Dict, List, Set, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class Debugger:
    """Sistema de debugging con puntos de interrupcion y inspeccion de variables"""
    
    def __init__(self, enabled=False):
        self.enabled = enabled
        self.breakpoints: Set[int] = set()  # Lineas con breakpoints
        self.step_mode = False
        self.current_line = 0
        self.variable_history: List[Dict] = []  # Historial de cambios de variables
        
    def add_breakpoint(self, lineno: int):
        """Agrega un punto de interrupcion en una linea"""
        self.breakpoints.add(lineno)
        console.print(f"[green]Breakpoint agregado en linea {lineno}[/green]")
    
    def remove_breakpoint(self, lineno: int):
        """Elimina un punto de interrupcion"""
        if lineno in self.breakpoints:
            self.breakpoints.remove(lineno)
            console.print(f"[yellow]Breakpoint eliminado en linea {lineno}[/yellow]")
        else:
            console.print(f"[red]No hay breakpoint en linea {lineno}[/red]")
    
    def check_breakpoint(self, lineno: int, interpreter_env) -> bool:
        """Verifica si hay un breakpoint en la linea actual"""
        if not self.enabled:
            return False
        
        if lineno in self.breakpoints or self.step_mode:
            self.current_line = lineno
            self._show_debug_info(lineno, interpreter_env)
            return True
        return False
    
    def _show_debug_info(self, lineno: int, interpreter_env):
        """Muestra informacion de debugging"""
        console.print(Panel(f"[bold cyan]Breakpoint en linea {lineno}[/bold cyan]", 
                          title="Debug", border_style="cyan"))
        
        # Mostrar variables actuales
        self.inspect_variables(interpreter_env)
        
        # Esperar comando del usuario
        while True:
            cmd = input("\n[debug] (c)ontinue, (s)tep, (v)ars, (q)uit: ").strip().lower()
            if cmd == 'c' or cmd == '':
                self.step_mode = False
                break
            elif cmd == 's':
                self.step_mode = True
                break
            elif cmd == 'v':
                self.inspect_variables(interpreter_env)
            elif cmd == 'q':
                raise KeyboardInterrupt("Debugging interrumpido por usuario")
    
    def inspect_variables(self, interpreter_env):
        """Inspecciona las variables del entorno actual"""
        table = Table(title="Variables")
        table.add_column("Nombre", style="cyan")
        table.add_column("Tipo", style="magenta")
        table.add_column("Valor", style="green")
        
        for name, value in interpreter_env.items():
            if not callable(value) and not name.startswith('_'):
                value_str = str(value)
                if isinstance(value, list):
                    value_str = f"[{len(value)} elementos] {value[:5] if len(value) > 5 else value}"
                elif isinstance(value, str) and len(value_str) > 50:
                    value_str = value_str[:50] + "..."
                table.add_row(name, type(value).__name__, value_str)
        
        console.print(table)
    
    def trace_execution(self, lineno: int, node_type: str, interpreter_env):
        """Registra la ejecucion para trazado"""
        if self.enabled:
            # Guardar snapshot de variables
            snapshot = {
                'line': lineno,
                'node_type': node_type,
                'variables': {k: v for k, v in interpreter_env.items() 
                             if not callable(v) and not k.startswith('_')}
            }
            self.variable_history.append(snapshot)


class Profiler:
    """Sistema de perfilamiento para medir rendimiento"""
    
    def __init__(self, enabled=False):
        self.enabled = enabled
        self.function_calls: Dict[str, int] = defaultdict(int)
        self.function_times: Dict[str, List[float]] = defaultdict(list)
        self.total_time = 0.0
        self.start_time = None
        self.call_stack: List[str] = []
        
    def start(self):
        """Inicia el perfilamiento"""
        if self.enabled:
            self.start_time = time.time()
    
    def end(self):
        """Termina el perfilamiento"""
        if self.enabled and self.start_time:
            self.total_time = time.time() - self.start_time
    
    def enter_function(self, func_name: str):
        """Registra entrada a una funcion"""
        if self.enabled:
            self.function_calls[func_name] += 1
            self.call_stack.append(func_name)
            return time.time()
        return None
    
    def exit_function(self, func_name: str, start_time: Optional[float]):
        """Registra salida de una funcion"""
        if self.enabled and start_time:
            elapsed = time.time() - start_time
            self.function_times[func_name].append(elapsed)
            if self.call_stack and self.call_stack[-1] == func_name:
                self.call_stack.pop()
    
    def get_report(self) -> str:
        """Genera un reporte de perfilamiento"""
        if not self.enabled:
            return "Perfilamiento deshabilitado"
        
        report = []
        report.append(f"\n[bold cyan]Reporte de Perfilamiento[/bold cyan]")
        report.append(f"Tiempo total de ejecucion: {self.total_time:.4f} segundos\n")
        
        # Tabla de funciones
        table = Table(title="Llamadas a Funciones")
        table.add_column("Funcion", style="cyan")
        table.add_column("Llamadas", style="yellow")
        table.add_column("Tiempo Total", style="green")
        table.add_column("Tiempo Promedio", style="magenta")
        table.add_column("Tiempo Max", style="red")
        
        for func_name in sorted(self.function_calls.keys()):
            calls = self.function_calls[func_name]
            times = self.function_times[func_name]
            total_time = sum(times)
            avg_time = total_time / calls if calls > 0 else 0
            max_time = max(times) if times else 0
            
            table.add_row(
                func_name,
                str(calls),
                f"{total_time:.4f}s",
                f"{avg_time:.4f}s",
                f"{max_time:.4f}s"
            )
        
        console.print("\n".join(report))
        console.print(table)
        
        return ""


class RuntimeValidator:
    """Validador en tiempo de ejecucion"""
    
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.errors: List[Dict] = []
    
    def validate_division_by_zero(self, node, divisor):
        """Valida division por cero"""
        if self.enabled and divisor == 0:
            lineno = getattr(node, 'lineno', 0)
            error_info = {
                'type': 'DivisionPorCero',
                'line': lineno,
                'message': 'Division por cero detectada'
            }
            self.errors.append(error_info)
            raise RuntimeError(f"Error en linea {lineno}: Division por cero")
    
    def validate_array_index(self, node, array, index):
        """Valida indices de arrays"""
        if not self.enabled:
            return
        
        lineno = getattr(node, 'lineno', 0)
        
        if not isinstance(array, list):
            error_info = {
                'type': 'TipoInvalido',
                'line': lineno,
                'message': f'Intento de indexar algo que no es un array: {type(array).__name__}'
            }
            self.errors.append(error_info)
            raise RuntimeError(f"Error en linea {lineno}: Intento de indexar algo que no es un array")
        
        if not isinstance(index, int):
            error_info = {
                'type': 'IndiceInvalido',
                'line': lineno,
                'message': f'El indice debe ser un entero, se recibio: {type(index).__name__}'
            }
            self.errors.append(error_info)
            raise RuntimeError(f"Error en linea {lineno}: El indice debe ser un entero")
        
        if index < 0 or index >= len(array):
            error_info = {
                'type': 'IndiceFueraDeRango',
                'line': lineno,
                'message': f'Indice fuera de rango: {index} (array tiene {len(array)} elementos)'
            }
            self.errors.append(error_info)
            raise RuntimeError(f"Error en linea {lineno}: Indice fuera de rango: {index} (array tiene {len(array)} elementos)")
    
    def validate_type(self, node, value, expected_type: str):
        """Valida tipos dinamicos"""
        if not self.enabled:
            return
        
        lineno = getattr(node, 'lineno', 0)
        actual_type = type(value).__name__
        
        type_map = {
            'int': 'integer',
            'float': 'float',
            'bool': 'boolean',
            'str': 'string',
            'list': 'array'
        }
        
        actual_bminor_type = type_map.get(actual_type, actual_type)
        
        if actual_bminor_type != expected_type:
            error_info = {
                'type': 'ErrorDeTipo',
                'line': lineno,
                'message': f'Se esperaba {expected_type} pero se obtuvo {actual_bminor_type}'
            }
            self.errors.append(error_info)
            # No lanzar excepcion, solo registrar para debugging


class ErrorHandler:
    """Manejo mejorado de errores con stack traces y sugerencias"""
    
    def __init__(self):
        self.call_stack: List[Dict] = []
        self.error_context: List[Dict] = []
    
    def push_context(self, func_name: str, lineno: int):
        """Agrega un contexto a la pila de llamadas"""
        self.call_stack.append({
            'function': func_name,
            'line': lineno
        })
    
    def pop_context(self):
        """Elimina el contexto actual de la pila"""
        if self.call_stack:
            self.call_stack.pop()
    
    def format_error(self, error: Exception, node=None) -> str:
        """Formatea un error con stack trace y sugerencias"""
        lineno = getattr(node, 'lineno', 0) if node else 0
        error_type = type(error).__name__
        error_message = str(error)
        
        # Construir stack trace
        stack_trace = []
        stack_trace.append(f"[bold red]Error: {error_type}[/bold red]")
        stack_trace.append(f"[red]Mensaje: {error_message}[/red]")
        
        if self.call_stack:
            stack_trace.append("\n[bold yellow]Stack Trace:[/bold yellow]")
            for i, ctx in enumerate(reversed(self.call_stack)):
                indent = "  " * i
                stack_trace.append(f"{indent}-> {ctx['function']} (linea {ctx['line']})")
        
        if lineno > 0:
            stack_trace.append(f"\n[bold cyan]Ubicacion:[/bold cyan] Linea {lineno}")
        
        # Agregar sugerencias
        suggestions = self._get_suggestions(error_type, error_message)
        if suggestions:
            stack_trace.append("\n[bold green]Sugerencias:[/bold green]")
            for suggestion in suggestions:
                stack_trace.append(f"  - {suggestion}")
        
        return "\n".join(stack_trace)
    
    def _get_suggestions(self, error_type: str, error_message: str) -> List[str]:
        """Genera sugerencias basadas en el tipo de error"""
        suggestions = []
        
        if "Division por cero" in error_message or "DivisionPorCero" in error_type:
            suggestions.append("Verifica que el divisor no sea cero antes de dividir")
            suggestions.append("Usa una condicion if para validar el divisor")
        
        if "Indice fuera de rango" in error_message or "IndiceFueraDeRango" in error_type:
            suggestions.append("Verifica que el indice este dentro del rango del array")
            suggestions.append("Usa length() para obtener el tamano del array antes de indexar")
        
        if "no definida" in error_message or "no definido" in error_message:
            suggestions.append("Verifica que la variable o funcion este declarada antes de usarla")
            suggestions.append("Revisa la ortografia del nombre")
        
        if "Error de tipo" in error_message or "ErrorDeTipo" in error_type:
            suggestions.append("Verifica que los tipos de las variables coincidan")
            suggestions.append("Usa conversiones de tipo si es necesario")
        
        return suggestions

