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

    # Manejo de errores durante el análisis léxico
    def handle_lexical_error(token):
        error_msg = f"Error Léxico: Carácter ilegal '{token.value[0]}' en la línea {token.lineno}"
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
        print("Análisis léxico completado: no se encontraron tokens.")
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
        print("[bold green]Análisis sintáctico completado sin errores.[/bold green]")
        if syntax_tree:
            print("[bold blue]Mostrando Árbol de Sintaxis Abstracta (AST):[/bold blue]")
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
    
    # Verificar errores sintácticos antes de proceder
    if errors_detected():
        print(f"[bold red]Se encontraron {errors_detected()} errores de sintaxis. No se puede continuar con el análisis semántico.[/bold red]")
        return
        
    print("[bold blue]Análisis sintáctico completado. Iniciando análisis semántico...[/bold blue]")
    
    # Ejecutar verificación semántica
    global_symbol_table = SemanticAnalyzer.checker(syntax_tree)
    
    if not errors_detected():
        print("[bold green]Análisis semántico completado sin errores.[/bold green]")
        print("[bold blue]Mostrando Tablas de Símbolos:[/bold blue]")
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
    
    # Primera etapa: Análisis léxico y sintáctico
    print("Fase 1: Análisis Léxico y Sintáctico...")
    syntax_tree = parse(source_code)
    if errors_detected():
        print(f"[bold red]Se encontraron {errors_detected()} errores de sintaxis. No se puede continuar.[/bold red]")
        return
    print("Análisis sintáctico completado sin errores.\n")

    # Segunda etapa: Verificación semántica
    print("Fase 2: Análisis Semántico...")
    global_symbol_table = SemanticAnalyzer.checker(syntax_tree)
    if errors_detected():
        print(f"[bold red]Se encontraron {errors_detected()} errores semánticos. No se puede continuar.[/bold red]")
        return
    print("Análisis semántico completado sin errores.\n")

    # Tercera etapa: Generación de código intermedio
    print("Fase 3: Generación de Código LLVM...")
    try:
        llvm_ir_output = generate_code(syntax_tree)
        
        output_file = "output.ll"
        with open(output_file, 'w') as output:
            output.write(llvm_ir_output)
        
        print(f"Código LLVM IR generado exitosamente y guardado en '{output_file}'")

    except Exception as ex:
        print(f"Error durante la generación de código:")
        print(f"   {type(ex).__name__}: {ex}")
        import traceback
        traceback.print_exc()

def main():
    argument_parser = argparse.ArgumentParser(description="Compilador para el lenguaje B-Minor 2025.")  
    argument_parser.add_argument('--scan', action='store_true', help='Realiza el análisis léxico del archivo.')
    argument_parser.add_argument('--parse', action='store_true', help='Realiza el análisis sintáctico del archivo.')
    argument_parser.add_argument('--check', action='store_true', help='Realiza el análisis sintáctico y semántico del archivo.')
    argument_parser.add_argument('--codegen', action='store_true', help='Genera el código LLVM IR (.ll) del archivo.')
    
    argument_parser.add_argument('filepath', type=str, help='El archivo .bminor a procesar.')
    parsed_args = argument_parser.parse_args()

    if parsed_args.scan:
        perform_lexical_analysis(parsed_args.filepath)
    elif parsed_args.parse:
        perform_syntax_analysis(parsed_args.filepath)
    elif parsed_args.check:
        perform_semantic_analysis(parsed_args.filepath)
    elif parsed_args.codegen:
        generate_llvm_code(parsed_args.filepath)
    else:
        print("Acción no especificada. Debes usar --scan, --parse, --check, o --codegen.")
        argument_parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()