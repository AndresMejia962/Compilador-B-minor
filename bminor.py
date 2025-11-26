import sys
import argparse
import pandas as pd
from tabulate import tabulate
from rich import print

from bminor_lexer import Lexer
from parser import parse
from errors import errors_detected, clear_errors
from checker import SemanticAnalyzer
from codegen import generate_code
from interp import Interpreter, Context

def perform_lexical_analysis(input_file):
    """Ejecuta el escaneo léxico del código fuente y presenta los tokens identificados."""
    try:
        with open(input_file, 'r', encoding='utf-8') as source_file:
            source_code = source_file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no fue encontrado.")
        sys.exit(1)

    token_analyzer = Lexer()
    identified_tokens = []
    lexical_errors = []

    # Manejo de errores durante el analisis lexico
    def handle_lexical_error(token):
        error_msg = f"Error Lexico: Caracter ilegal '{token.value[0]}' en la linea {token.lineno}"
        lexical_errors.append(error_msg)
        token_analyzer.index += 1
    token_analyzer.error = handle_lexical_error

    # Proceso de identificación de tokens
    for token in token_analyzer.tokenize(source_code):
        if token.type == 'ERROR':
            lexical_errors.append(token.value)
        else:
            identified_tokens.append(token)

    if lexical_errors:
        for err in lexical_errors:
            print(err)
    
    if not identified_tokens and not lexical_errors:
        print("Analisis lexico completado: no se encontraron tokens.")
        return

    if identified_tokens:
        line_offsets = [0] + [i + 1 for i, char in enumerate(source_code) if char == '\n']
        
        token_table = []
        for token in identified_tokens:
            line_offset = line_offsets[token.lineno - 1]
            column_pos = token.index - line_offset + 1
            token_table.append([token.type, repr(token.value), token.lineno, column_pos])
                
        token_df = pd.DataFrame(token_table, columns=["TIPO", "VALOR", "LINEA", "COLUMNA"])
        token_df.index = range(1, len(token_df) + 1)
        print(tabulate(token_df, headers='keys', tablefmt='grid', stralign='left', showindex="TOKEN #"))

def perform_syntax_analysis(input_file):
    """Ejecuta el análisis sintáctico del código y presenta el árbol de sintaxis abstracta."""
    try:
        with open(input_file, 'r', encoding='utf-8') as source_file:
            source_code = source_file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no fue encontrado.")
        sys.exit(1)

    clear_errors()
    
    syntax_tree = parse(source_code)
    
    if not errors_detected():
        print("[bold green]Analisis sintactico completado sin errores.[/bold green]")
        if syntax_tree:
            print("[bold blue]Mostrando Arbol de Sintaxis Abstracta (AST):[/bold blue]")
            tree_visualization = syntax_tree.pretty()
            print(tree_visualization)
    else:
        print(f"[bold red]Se encontraron {errors_detected()} errores de sintaxis.[/bold red]")

def perform_semantic_analysis(input_file):
    """Ejecuta el análisis sintáctico y semántico completo del código fuente."""
    try:
        with open(input_file, 'r', encoding='utf-8') as source_file:
            source_code = source_file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no fue encontrado.")
        sys.exit(1)

    clear_errors()
    
    syntax_tree = parse(source_code)
    
    # Verificar errores sintacticos antes de proceder
    if errors_detected():
        print(f"[bold red]Se encontraron {errors_detected()} errores de sintaxis. No se puede continuar con el analisis semantico.[/bold red]")
        return
        
    print("[bold blue]Analisis sintactico completado. Iniciando analisis semantico...[/bold blue]")
    
    # Ejecutar verificacion semantica
    global_symbol_table = SemanticAnalyzer.checker(syntax_tree)
    
    if not errors_detected():
        print("[bold green]Analisis semantico completado sin errores.[/bold green]")
        print("[bold blue]Mostrando Tablas de Simbolos:[/bold blue]")
        global_symbol_table.print()
    else:
        print(f"[bold red]Se encontraron {errors_detected()} errores en total.[/bold red]")

def generate_llvm_code(input_file):
    """
    Ejecuta el proceso completo de compilación: Análisis, Verificación y Generación de Código IR.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as source_file:
            source_code = source_file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no fue encontrado.")
        sys.exit(1)

    clear_errors()
    
    # Primera etapa: Analisis lexico y sintactico
    print("Fase 1: Analisis Lexico y Sintactico...")
    syntax_tree = parse(source_code)
    if errors_detected():
        print(f"[bold red]Se encontraron {errors_detected()} errores de sintaxis. No se puede continuar.[/bold red]")
        return
    print("Analisis sintactico completado sin errores.\n")

    # Segunda etapa: Verificacion semantica
    print("Fase 2: Analisis Semantico...")
    global_symbol_table = SemanticAnalyzer.checker(syntax_tree)
    if errors_detected():
        print(f"[bold red]Se encontraron {errors_detected()} errores semanticos. No se puede continuar.[/bold red]")
        return
    print("Analisis semantico completado sin errores.\n")

    # Tercera etapa: Generacion de codigo intermedio
    print("Fase 3: Generacion de Codigo LLVM...")
    try:
        llvm_ir_output = generate_code(syntax_tree)
        
        output_file = "output.ll"
        with open(output_file, 'w') as output:
            output.write(llvm_ir_output)
        
        print(f"Codigo LLVM IR generado exitosamente y guardado en '{output_file}'")

    except Exception as ex:
        print(f"Error durante la generacion de codigo:")
        print(f"   {type(ex).__name__}: {ex}")
        import traceback
        traceback.print_exc()

def interpret_code(input_file, debug=False, profile=False):
    """
    Ejecuta el interprete tree-walking para el codigo BMinor.
    
    Args:
        input_file: Archivo .bminor a ejecutar
        debug: Habilita modo debugging
        profile: Habilita perfilamiento
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as source_file:
            source_code = source_file.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no fue encontrado.")
        sys.exit(1)

    clear_errors()
    
    # Primera etapa: Analisis lexico y sintactico
    print("[bold blue]Fase 1: Analisis Lexico y Sintactico...[/bold blue]")
    syntax_tree = parse(source_code)
    if errors_detected():
        print(f"[bold red]Se encontraron {errors_detected()} errores de sintaxis. No se puede continuar.[/bold red]")
        return
    print("[bold green]Analisis sintactico completado sin errores.[/bold green]\n")

    # Segunda etapa: Verificacion semantica
    print("[bold blue]Fase 2: Analisis Semantico...[/bold blue]")
    global_symbol_table = SemanticAnalyzer.checker(syntax_tree)
    if errors_detected():
        print(f"[bold red]Se encontraron {errors_detected()} errores semanticos. No se puede continuar.[/bold red]")
        return
    print("[bold green]Analisis semantico completado sin errores.[/bold green]\n")

    # Tercera etapa: Ejecucion con el interprete
    print("[bold blue]Fase 3: Ejecucion del Interprete...[/bold blue]")
    print("[bold yellow]==========================================[/bold yellow]")
    try:
        ctxt = Context()
        # Opciones de debugging y profiling
        interpreter = Interpreter(ctxt, debug=debug, profile=profile)
        interpreter.interpret(syntax_tree)
        
        if ctxt.have_errors:
            print(f"\n[bold red]Se encontraron {len(ctxt.errors)} errores durante la ejecucion.[/bold red]")
        else:
            print("[bold yellow]==========================================[/bold yellow]")
            print("[bold green]Ejecucion completada exitosamente.[/bold green]")

    except Exception as ex:
        print(f"\n[bold red]Error durante la ejecucion:[/bold red]")
        print(f"   {type(ex).__name__}: {ex}")
        import traceback
        traceback.print_exc()

def repl_mode():
    """
    Modo interactivo (REPL) para ejecutar codigo B-Minor linea por linea.
    """
    from rich.console import Console
    from rich.panel import Panel
    from model import Program, Expression, Assignment, PrintStmt, ReturnStmt
    
    console = Console()
    
    print("[bold green]B-Minor REPL (Read-Eval-Print Loop)[/bold green]")
    print("[dim]Escribe codigo B-Minor. Comandos especiales:[/dim]")
    print("[dim]  .exit o .quit - Salir del REPL[/dim]")
    print("[dim]  .vars - Mostrar variables definidas[/dim]")
    print("[dim]  .clear - Limpiar todas las variables[/dim]")
    print("[dim]  .help - Mostrar ayuda[/dim]")
    print()
    
    # Inicializar interprete y contexto
    ctxt = Context()
    interpreter = Interpreter(ctxt)
    
    # Inicializar builtins y constantes (usar el mismo metodo que interp.py)
    import importlib.util
    import os
    from symtab import SymbolTable
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    builtins_path = os.path.join(current_dir, "builtins.py")
    spec = importlib.util.spec_from_file_location("bminor_builtins", builtins_path)
    bminor_builtins = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bminor_builtins)
    
    for name, cval in bminor_builtins.consts.items():
        interpreter.env[name] = cval
    for name, func in bminor_builtins.builtins.items():
        interpreter.env[name] = func
    
    # Tabla de simbolos global para el REPL (se actualiza incrementalmente)
    global_symbol_table = SymbolTable('repl_global')
    
    # Registrar funciones built-in en la tabla de simbolos del REPL
    analyzer_temp = SemanticAnalyzer()
    analyzer_temp._register_builtins(global_symbol_table)
    
    # Buffer para lineas multi-linea
    buffer = ""
    line_count = 0
    
    try:
        while True:
            try:
                # Mostrar prompt
                if buffer:
                    prompt = "... "
                else:
                    prompt = ">>> "
                
                # Leer linea
                try:
                    line = input(prompt)
                except EOFError:
                    print("\n[dim]Saliendo...[/dim]")
                    break
                except KeyboardInterrupt:
                    print("\n[dim]Interrumpido. Usa .exit para salir.[/dim]")
                    buffer = ""
                    continue
                
                # Comandos especiales
                line_stripped = line.strip()
                if line_stripped in ['.exit', '.quit', '.q']:
                    print("[dim]Saliendo del REPL...[/dim]")
                    break
                elif line_stripped == '.vars':
                    _show_variables(interpreter)
                    continue
                elif line_stripped == '.clear':
                    _clear_variables(interpreter)
                    continue
                elif line_stripped == '.help':
                    _show_help()
                    continue
                elif line_stripped == '':
                    continue
                
                # Agregar al buffer
                if buffer:
                    buffer += "\n" + line
                else:
                    buffer = line
                
                # Verificar si la linea esta completa (termina con ;)
                if not buffer.strip().endswith(';') and not buffer.strip().endswith('}'):
                    # Podria ser una expresion sin punto y coma, intentar parsear
                    pass
                
                # Intentar parsear y ejecutar
                try:
                    clear_errors()
                    
                    # Parsear el codigo
                    syntax_tree = parse(buffer)
                    
                    if errors_detected():
                        # Si hay errores, podria ser porque falta mas codigo
                        # Verificar si es un error de EOF
                        error_msg = str(errors_detected())
                        if "EOF" in error_msg or "final" in error_msg.lower():
                            # Continuar leyendo
                            continue
                        else:
                            # Error real, mostrar y limpiar buffer
                            print(f"[red]Error de sintaxis[/red]")
                            buffer = ""
                            continue
                    
                    # Verificar semanticamente usando la tabla de simbolos acumulada
                    analyzer = SemanticAnalyzer()
                    analyzer.visit(syntax_tree, global_symbol_table)
                    
                    if errors_detected():
                        print(f"[red]Error semantico[/red]")
                        buffer = ""
                        continue
                    
                    # Ejecutar
                    if isinstance(syntax_tree, Program) and syntax_tree.body:
                        for stmt in syntax_tree.body:
                            # Verificar si es una expresion (Assignment es Expression pero tambien Statement)
                            # Si es una expresion pura (no Assignment, PrintStmt, ReturnStmt), mostrar resultado
                            if isinstance(stmt, Expression) and not isinstance(stmt, (Assignment, PrintStmt, ReturnStmt)):
                                result = stmt.accept(interpreter)
                                if result is not None:
                                    console.print(f"[cyan]=> {result}[/cyan]")
                            else:
                                # Es una sentencia normal, ejecutarla
                                # Si es una declaracion, se agregara a la tabla de simbolos automaticamente
                                stmt.accept(interpreter)
                    
                    # Limpiar buffer despues de ejecucion exitosa
                    buffer = ""
                    line_count += 1
                    
                except Exception as e:
                    # Error durante ejecucion
                    if "BminorExit" in str(type(e)):
                        # Error manejado por el interprete
                        pass
                    else:
                        print(f"[red]Error: {e}[/red]")
                    buffer = ""
                    continue
                    
            except Exception as e:
                print(f"[red]Error inesperado: {e}[/red]")
                buffer = ""
                continue
                
    except KeyboardInterrupt:
        print("\n[dim]Saliendo...[/dim]")

def _show_variables(interpreter):
    """Muestra las variables definidas en el entorno actual."""
    from rich.table import Table
    from rich import print as rprint
    
    table = Table(title="Variables Definidas")
    table.add_column("Nombre", style="cyan")
    table.add_column("Tipo", style="magenta")
    table.add_column("Valor", style="green")
    
    vars_found = False
    for name, value in interpreter.env.items():
        # Omitir funciones y builtins
        if callable(value) or name.startswith('_'):
            continue
        vars_found = True
        value_str = str(value)
        if isinstance(value, list):
            value_str = f"[{len(value)} elementos]"
        elif isinstance(value, str) and len(value_str) > 50:
            value_str = value_str[:50] + "..."
        table.add_row(name, type(value).__name__, value_str)
    
    if vars_found:
        rprint(table)
    else:
        print("[dim]No hay variables definidas.[/dim]")

def _clear_variables(interpreter):
    """Limpia todas las variables del entorno (excepto builtins)."""
    from builtins import builtins, consts
    
    # Guardar builtins y constantes
    saved_builtins = {}
    saved_consts = {}
    for name in builtins.keys():
        if name in interpreter.env:
            saved_builtins[name] = interpreter.env[name]
    for name in consts.keys():
        if name in interpreter.env:
            saved_consts[name] = interpreter.env[name]
    
    # Limpiar entorno
    interpreter.env = interpreter.env.new_child()
    
    # Restaurar builtins y constantes
    for name, val in saved_consts.items():
        interpreter.env[name] = val
    for name, val in saved_builtins.items():
        interpreter.env[name] = val
    
    print("[green]Variables limpiadas.[/green]")

def _show_help():
    """Muestra ayuda sobre el REPL."""
    help_text = """
[bold]Comandos del REPL:[/bold]

[cyan].exit, .quit, .q[/cyan]  - Salir del REPL
[cyan].vars[/cyan]            - Mostrar todas las variables definidas
[cyan].clear[/cyan]           - Limpiar todas las variables
[cyan].help[/cyan]            - Mostrar esta ayuda

[bold]Ejemplos:[/bold]
  >>> x: integer = 10;
  >>> print x;
  >>> y: integer = x + 5;
  >>> print y;
    """
    print(help_text)

def main():
    argument_parser = argparse.ArgumentParser(description="Compilador para el lenguaje B-Minor 2025.")  
    argument_parser.add_argument('--scan', action='store_true', help='Realiza el analisis lexico del archivo.')
    argument_parser.add_argument('--parse', action='store_true', help='Realiza el analisis sintactico del archivo.')
    argument_parser.add_argument('--check', action='store_true', help='Realiza el analisis sintactico y semantico del archivo.')
    argument_parser.add_argument('--codegen', action='store_true', help='Genera el codigo LLVM IR (.ll) del archivo.')
    argument_parser.add_argument('--interp', action='store_true', help='Ejecuta el interprete tree-walking del archivo.')
    argument_parser.add_argument('--repl', action='store_true', help='Inicia el modo interactivo (REPL).')
    argument_parser.add_argument('--debug', action='store_true', help='Habilita el modo debugging (breakpoints, inspeccion de variables).')
    argument_parser.add_argument('--profile', action='store_true', help='Habilita el perfilamiento (medicion de tiempo y llamadas a funciones).')
    
    argument_parser.add_argument('filepath', type=str, nargs='?', help='El archivo .bminor a procesar.')
    parsed_args = argument_parser.parse_args()

    if parsed_args.repl:
        repl_mode()
    elif parsed_args.scan:
        if not parsed_args.filepath:
            print("Error: Se requiere un archivo para --scan")
            sys.exit(1)
        perform_lexical_analysis(parsed_args.filepath)
    elif parsed_args.parse:
        if not parsed_args.filepath:
            print("Error: Se requiere un archivo para --parse")
            sys.exit(1)
        perform_syntax_analysis(parsed_args.filepath)
    elif parsed_args.check:
        if not parsed_args.filepath:
            print("Error: Se requiere un archivo para --check")
            sys.exit(1)
        perform_semantic_analysis(parsed_args.filepath)
    elif parsed_args.codegen:
        if not parsed_args.filepath:
            print("Error: Se requiere un archivo para --codegen")
            sys.exit(1)
        generate_llvm_code(parsed_args.filepath)
    elif parsed_args.interp:
        if not parsed_args.filepath:
            print("Error: Se requiere un archivo para --interp")
            sys.exit(1)
        interpret_code(parsed_args.filepath, debug=parsed_args.debug, profile=parsed_args.profile)
    else:
        print("Accion no especificada. Debes usar --scan, --parse, --check, --codegen, --interp, o --repl.")
        argument_parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()