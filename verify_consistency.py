import subprocess
import sys
import os
import shutil

def run_command(cmd, shell=False, capture_output=True):
    """Ejecuta un comando y retorna su salida."""
    try:
        result = subprocess.run(
            cmd, 
            shell=shell, 
            check=True, 
            capture_output=capture_output, 
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando comando: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        print(f"Salida de error:\n{e.stderr}")
        return None
    except FileNotFoundError:
        print(f"Comando no encontrado: {cmd[0] if isinstance(cmd, list) else cmd}")
        return None

def check_clang():
    """Verifica si clang está disponible."""
    if shutil.which('clang') is None:
        print("ERROR: 'clang' no se encontro en el PATH.")
        print("Por favor instala LLVM/Clang y agregalo al PATH para compilar.")
        print("Descarga: https://github.com/llvm/llvm-project/releases")
        return False
    return True

def verify_consistency(source_file):
    print(f"--- Verificando consistencia para: {source_file} ---")
    
    # 1. Ejecutar Interprete
    print("[1/4] Ejecutando Interprete...")
    interp_output = run_command([sys.executable, "bminor.py", "--interp", source_file])
    if interp_output is None:
        return False
    
    # Filtrar salida del intérprete para obtener solo la salida del programa
    # El intérprete actual imprime mucha info de debug/fases.
    # Buscaremos la sección entre las líneas de "==="
    interp_lines = interp_output.splitlines()
    program_output_interp = []
    capture = False
    for line in interp_lines:
        if "Ejecucion completada exitosamente" in line:
            capture = False
        if capture:
            program_output_interp.append(line)
        if "Ejecucion del Interprete" in line:
             # La siguiente línea suele ser los separadores
             pass
        if "=====" in line:
            # Toggle capture. 
            # Primera vez: empieza captura. Segunda vez: termina.
            # Pero hay dos bloques de separadores.
            # La salida real está entre el primer bloque de "===" y el segundo.
            capture = not capture
            
    # Limpieza básica: eliminar líneas vacías al inicio/final
    interp_clean = "\n".join(program_output_interp).strip()
    
    # 2. Generar Codigo LLVM
    print("[2/4] Generando LLVM IR...")
    codegen_output = run_command([sys.executable, "bminor.py", "--codegen", source_file])
    if codegen_output is None:
        return False
        
    if not os.path.exists("output.ll"):
        print("Error: No se genero output.ll")
        return False

    # 3. Compilar con Clang
    print("[3/4] Compilando con Clang...")
    if not check_clang():
        return False
        
    exe_name = "program.exe"
    # Asumimos que runtime.cpp esta en el directorio actual
    if not os.path.exists("runtime.cpp") and not os.path.exists("runtime.c"):
        print("Advertencia: No se encontro runtime.cpp o runtime.c. La compilacion podria fallar si se usan funciones externas.")
    
    runtime_file = "runtime.cpp" if os.path.exists("runtime.cpp") else "runtime.c"
    
    compile_cmd = ["clang", "output.ll", runtime_file, "-o", exe_name]
    if run_command(compile_cmd) is None:
        return False
        
    # 4. Ejecutar Binario Compilado
    print("[4/4] Ejecutando Binario Compilado...")
    compiled_output = run_command([f".\\{exe_name}"], shell=True)
    if compiled_output is None:
        return False
        
    compiled_clean = compiled_output.strip()
    
    # 5. Comparar
    print("\n--- Resultados ---")
    print("Salida Interprete:")
    print(interp_clean)
    print("\nSalida Compilada:")
    print(compiled_clean)
    print("\n------------------")
    
    if interp_clean == compiled_clean:
        print("[OK] EXITO: Las salidas coinciden.")
        return True
    else:
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python verify_consistency.py <archivo.bminor>")
        sys.exit(1)
        
    source_file = sys.argv[1]
    verify_consistency(source_file)
