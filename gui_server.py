# gui_server.py
"""
Servidor Flask simple para la interfaz grafica del compilador B-Minor
Solo para uso educativo/demostracion
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import sys
import os
import json
from pathlib import Path

app = Flask(__name__, static_folder='gui-frontend/dist', static_url_path='')
CORS(app)  # Permitir CORS para desarrollo

# Ruta base del proyecto
BASE_DIR = Path(__file__).parent.resolve()

@app.route('/')
def index():
    """Servir la aplicacion React"""
    return send_from_directory('gui-frontend/dist', 'index.html')

@app.route('/api/run', methods=['POST'])
def run_command():
    """Ejecuta un comando del compilador B-Minor"""
    try:
        data = request.json
        action = data.get('action')  # scan, parse, check, codegen, interp, repl
        file_path = data.get('file')
        debug = data.get('debug', False)
        profile = data.get('profile', False)
        
        if not action:
            return jsonify({'error': 'Accion no especificada'}), 400
        
        if action != 'repl' and not file_path:
            return jsonify({'error': 'Archivo no especificado'}), 400
        
        # Construir comando
        cmd = [sys.executable, str(BASE_DIR / 'bminor.py')]
        
        # Agregar flags
        if action == 'scan':
            cmd.append('--scan')
        elif action == 'parse':
            cmd.append('--parse')
        elif action == 'check':
            cmd.append('--check')
        elif action == 'codegen':
            cmd.append('--codegen')
        elif action == 'interp':
            cmd.append('--interp')
        elif action == 'repl':
            cmd.append('--repl')
        else:
            return jsonify({'error': f'Accion desconocida: {action}'}), 400
        
        if debug:
            cmd.append('--debug')
        if profile:
            cmd.append('--profile')
        
        if file_path:
            # Asegurar que la ruta sea relativa al directorio base
            if not os.path.isabs(file_path):
                file_path = str(BASE_DIR / file_path)
            cmd.append(file_path)
        
        # Ejecutar comando
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Si es codegen y fue exitoso, compilar el LLVM con clang
        compile_result = None
        if action == 'codegen' and result.returncode == 0:
            output_ll_path = BASE_DIR / 'output.ll'
            if output_ll_path.exists():
                try:
                    # Buscar runtime.cpp o runtime.c
                    runtime_file = None
                    if (BASE_DIR / 'runtime.cpp').exists():
                        runtime_file = BASE_DIR / 'runtime.cpp'
                    elif (BASE_DIR / 'runtime.c').exists():
                        runtime_file = BASE_DIR / 'runtime.c'
                    
                    if runtime_file:
                        # Compilar con clang
                        import shutil
                        clang_path = shutil.which('clang')
                        if clang_path:
                            exe_name = 'compiled_output.exe'
                            exe_path = BASE_DIR / exe_name
                            compile_cmd = [
                                clang_path,
                                str(output_ll_path),
                                str(runtime_file),
                                '-o',
                                str(exe_path)
                            ]
                            
                            compile_result = subprocess.run(
                                compile_cmd,
                                cwd=str(BASE_DIR),
                                capture_output=True,
                                text=True,
                                encoding='utf-8',
                                errors='replace'
                            )
                            
                            # Si la compilación fue exitosa, ejecutar el programa
                            execution_output = ''
                            execution_errors = ''
                            execution_success = False
                            if compile_result.returncode == 0 and exe_path.exists():
                                try:
                                    exec_result = subprocess.run(
                                        [str(exe_path)],
                                        cwd=str(BASE_DIR),
                                        capture_output=True,
                                        text=True,
                                        encoding='utf-8',
                                        errors='replace',
                                        timeout=10  # Timeout de 10 segundos
                                    )
                                    execution_output = exec_result.stdout
                                    execution_errors = exec_result.stderr
                                    execution_success = exec_result.returncode == 0
                                except subprocess.TimeoutExpired:
                                    execution_errors = 'Error: El programa excedio el tiempo limite de ejecucion (10 segundos)'
                                except Exception as e:
                                    execution_errors = f'Error ejecutando el programa: {str(e)}'
                            
                            # Limpiar ejecutable temporal
                            if exe_path.exists():
                                try:
                                    os.unlink(exe_path)
                                except:
                                    pass
                            
                            # Agregar información de ejecución al resultado
                            if execution_output or execution_errors:
                                compile_result.execution_output = execution_output
                                compile_result.execution_errors = execution_errors
                                compile_result.execution_success = execution_success
                        else:
                            compile_result = type('obj', (object,), {
                                'returncode': 1,
                                'stdout': '',
                                'stderr': 'Error: Clang no encontrado en el PATH. Asegurate de tener Clang instalado.'
                            })()
                    else:
                        compile_result = type('obj', (object,), {
                            'returncode': 1,
                            'stdout': '',
                            'stderr': 'Advertencia: No se encontro runtime.cpp ni runtime.c. La compilacion requiere runtime.'
                        })()
                except Exception as e:
                    compile_result = type('obj', (object,), {
                        'returncode': 1,
                        'stdout': '',
                        'stderr': f'Error durante la compilacion: {str(e)}'
                    })()
        
        response_data = {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'success': result.returncode == 0
        }
        
        if compile_result is not None:
            response_data['compile_output'] = compile_result.stdout
            response_data['compile_errors'] = compile_result.stderr
            response_data['compile_success'] = compile_result.returncode == 0
            
            # Si hay resultado de ejecución, agregarlo
            if hasattr(compile_result, 'execution_output'):
                response_data['execution_output'] = compile_result.execution_output
                response_data['execution_errors'] = compile_result.execution_errors
                response_data['execution_success'] = compile_result.execution_success
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    """Lista archivos .bminor disponibles"""
    try:
        bminor_files = []
        
        # Buscar en directorio actual y subdirectorios comunes
        search_dirs = [BASE_DIR, BASE_DIR / 'test' / 'codegen', BASE_DIR / 'test' / 'parser']
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for file in search_dir.rglob('*.bminor'):
                    rel_path = file.relative_to(BASE_DIR)
                    bminor_files.append({
                        'name': file.name,
                        'path': str(rel_path).replace('\\', '/'),
                        'full_path': str(file)
                    })
        
        return jsonify({'files': bminor_files})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/read-file', methods=['POST'])
def read_file():
    """Lee el contenido de un archivo"""
    try:
        data = request.json
        file_path = data.get('file')
        
        if not file_path:
            return jsonify({'error': 'Ruta de archivo no especificada'}), 400
        
        # Asegurar que la ruta sea relativa al directorio base
        if not os.path.isabs(file_path):
            file_path = str(BASE_DIR / file_path)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Archivo no encontrado'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({'content': content})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-clang', methods=['GET'])
def check_clang():
    """Verifica si clang esta disponible"""
    import shutil
    clang_available = shutil.which('clang') is not None
    return jsonify({'available': clang_available})

@app.route('/api/save-file', methods=['POST'])
def save_file():
    """Guarda el contenido editado en un archivo"""
    try:
        data = request.json
        file_path = data.get('file')
        content = data.get('content')
        
        if not file_path:
            return jsonify({'error': 'Ruta de archivo no especificada', 'success': False}), 400
        
        if content is None:
            return jsonify({'error': 'Contenido no especificado', 'success': False}), 400
        
        # Asegurar que la ruta sea relativa al directorio base
        if not os.path.isabs(file_path):
            file_path = str(BASE_DIR / file_path)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Guardar archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({'success': True, 'message': 'Archivo guardado exitosamente'})
    
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/run-with-content', methods=['POST'])
def run_with_content():
    """Ejecuta un comando con contenido de codigo en memoria (no archivo)"""
    try:
        data = request.json
        action = data.get('action')
        content = data.get('content')
        debug = data.get('debug', False)
        profile = data.get('profile', False)
        
        if not action or not content:
            return jsonify({'error': 'Accion y contenido requeridos'}), 400
        
        # Crear archivo temporal
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bminor', delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Construir comando
            cmd = [sys.executable, str(BASE_DIR / 'bminor.py')]
            
            if action == 'scan':
                cmd.append('--scan')
            elif action == 'parse':
                cmd.append('--parse')
            elif action == 'check':
                cmd.append('--check')
            elif action == 'codegen':
                cmd.append('--codegen')
            elif action == 'interp':
                cmd.append('--interp')
            else:
                return jsonify({'error': f'Accion desconocida: {action}'}), 400
            
            if debug:
                cmd.append('--debug')
            if profile:
                cmd.append('--profile')
            
            cmd.append(tmp_path)
            
            # Ejecutar
            result = subprocess.run(
                cmd,
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Si es codegen y fue exitoso, compilar el LLVM con clang
            compile_result = None
            if action == 'codegen' and result.returncode == 0:
                output_ll_path = BASE_DIR / 'output.ll'
                if output_ll_path.exists():
                    try:
                        # Buscar runtime.cpp o runtime.c
                        runtime_file = None
                        if (BASE_DIR / 'runtime.cpp').exists():
                            runtime_file = BASE_DIR / 'runtime.cpp'
                        elif (BASE_DIR / 'runtime.c').exists():
                            runtime_file = BASE_DIR / 'runtime.c'
                        
                        if runtime_file:
                            # Compilar con clang
                            import shutil
                            clang_path = shutil.which('clang')
                            if clang_path:
                                exe_name = 'compiled_output.exe'
                                exe_path = BASE_DIR / exe_name
                                compile_cmd = [
                                    clang_path,
                                    str(output_ll_path),
                                    str(runtime_file),
                                    '-o',
                                    str(exe_path)
                                ]
                                
                                compile_result = subprocess.run(
                                    compile_cmd,
                                    cwd=str(BASE_DIR),
                                    capture_output=True,
                                    text=True,
                                    encoding='utf-8',
                                    errors='replace'
                                )
                                
                                # Si la compilación fue exitosa, ejecutar el programa
                                execution_output = ''
                                execution_errors = ''
                                execution_success = False
                                if compile_result.returncode == 0 and exe_path.exists():
                                    try:
                                        exec_result = subprocess.run(
                                            [str(exe_path)],
                                            cwd=str(BASE_DIR),
                                            capture_output=True,
                                            text=True,
                                            encoding='utf-8',
                                            errors='replace',
                                            timeout=10  # Timeout de 10 segundos
                                        )
                                        execution_output = exec_result.stdout
                                        execution_errors = exec_result.stderr
                                        execution_success = exec_result.returncode == 0
                                    except subprocess.TimeoutExpired:
                                        execution_errors = 'Error: El programa excedio el tiempo limite de ejecucion (10 segundos)'
                                    except Exception as e:
                                        execution_errors = f'Error ejecutando el programa: {str(e)}'
                                
                                # Limpiar ejecutable temporal
                                if exe_path.exists():
                                    try:
                                        os.unlink(exe_path)
                                    except:
                                        pass
                                
                                # Agregar información de ejecución al resultado
                                if execution_output or execution_errors:
                                    compile_result.execution_output = execution_output
                                    compile_result.execution_errors = execution_errors
                                    compile_result.execution_success = execution_success
                            else:
                                compile_result = type('obj', (object,), {
                                    'returncode': 1,
                                    'stdout': '',
                                    'stderr': 'Error: Clang no encontrado en el PATH. Asegurate de tener Clang instalado.'
                                })()
                        else:
                            compile_result = type('obj', (object,), {
                                'returncode': 1,
                                'stdout': '',
                                'stderr': 'Advertencia: No se encontro runtime.cpp ni runtime.c. La compilacion requiere runtime.'
                            })()
                    except Exception as e:
                        compile_result = type('obj', (object,), {
                            'returncode': 1,
                            'stdout': '',
                            'stderr': f'Error durante la compilacion: {str(e)}'
                        })()
            
            response_data = {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
            
            if compile_result is not None:
                response_data['compile_output'] = compile_result.stdout
                response_data['compile_errors'] = compile_result.stderr
                response_data['compile_success'] = compile_result.returncode == 0
                
                # Si hay resultado de ejecución, agregarlo
                if hasattr(compile_result, 'execution_output'):
                    response_data['execution_output'] = compile_result.execution_output
                    response_data['execution_errors'] = compile_result.execution_errors
                    response_data['execution_success'] = compile_result.execution_success
            
            return jsonify(response_data)
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Servidor GUI del Compilador B-Minor")
    print("=" * 50)
    print("\nAbre tu navegador en: http://localhost:5000")
    print("\nPresiona Ctrl+C para detener el servidor\n")
    app.run(debug=True, port=5000, host='127.0.0.1')

