import sys
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, c_int, c_bool
from rich import print

from parser import parse
from errors import errors_detected, clear_errors
from checker import Check
from codegen import LLVMCodeGenerator 

# --- Definir el Runtime de JIT (copiado de bminor.py) ---
# Estas son las funciones de Python que LLVM llamará.

@CFUNCTYPE(None, c_int)
def _printi(x):
    # Agregamos un prefijo para saber que viene del JIT
    print(f"[JIT]: {x}")

@CFUNCTYPE(None, c_bool)
def _printb(b):
    # Agregamos un prefijo
    print(f"[JIT]: {bool(b)}")


# --- 3. Lógica principal del arnés de prueba ---

def run_test(filepath):
    """
    Carga un archivo, lo compila y lo ejecuta con JIT.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"[bold red]Error: Archivo no encontrado '{filepath}'[/bold red]")
        sys.exit(1)
    
    # --- FASE 1: PARSE + CHECK ---
    # Necesitamos ejecutar el checker para que el AST
    # tenga las anotaciones de tipo (ej: n.type = 'integer')
    
    clear_errors()
    print(f"--- 1. Parseando {filepath} ---")
    ast = parse(code)
    if errors_detected():
        print("[bold red]Prueba fallida: Errores de Sintaxis.[/bold red]")
        sys.exit(1)

    print("--- 2. Chequeando semántica ---")
    Check.checker(ast)
    if errors_detected():
        print("[bold red]Prueba fallida: Errores Semánticos.[/bold red]")
        sys.exit(1)

    print("[bold green]Análisis completado.[/bold green]")
    
    # --- FASE 2: CODEGEN ---
    print("--- 3. Generando LLVM IR ---")
    codegen = LLVMCodeGenerator()
    codegen.visit(ast) # Esto rellena codegen.module

    llvm_ir = str(codegen.module)
    print("\n[bold blue]---------- INICIO: LLVM IR GENERADO ----------[/bold blue]")
    print(llvm_ir)
    print("[bold blue]----------- FIN: LLVM IR GENERADO ------------[/bold blue]\n")

    # --- FASE 3: JIT ---
    print("--- 4. Preparando JIT ---")
    try:
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        # Registrar las funciones de runtime de Python
        llvm.add_symbol("_printi", _printi._wrapper_address)
        llvm.add_symbol("_printb", _printb._wrapper_address)

        target = llvm.Target.from_default_triple()
        tm = target.create_target_machine()
        
        llvm_mod = llvm.parse_assembly(llvm_ir)
        llvm_mod.verify()
        
        engine = llvm.create_mcjit_compiler(llvm_mod, tm)
        engine.finalize_object()
        
        main_ptr = engine.get_function_address("main")
        main_func = CFUNCTYPE(None)(main_ptr)
        
        print("[bold green]--- 5. Ejecutando JIT ---[/bold green]")
        main_func()
        print("[bold green]-------------------------[/bold green]")

    except Exception as e:
        print(f"[bold red]Error durante el JIT:[/bold red] {e}")


# --- 4. Punto de entrada del script ---

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python test_jit.py <archivo.bminor>")
        sys.exit(1)
    
    # Usa el archivo de prueba que creamos en el paso anterior
    # o cualquier otro archivo .bminor
    run_test(sys.argv[1])