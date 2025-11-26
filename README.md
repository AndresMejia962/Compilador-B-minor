# Compilador B-Minor

Compilador completo para el lenguaje B-Minor que traduce código fuente a LLVM IR.

## 📋 Requisitos Previos

- Python 3.8 o superior
- LLVM y Clang (para compilar el código IR generado)

## 🚀 Instalación

### Opción 1: Entorno Virtual (Recomendado)

1. **Crear un entorno virtual:**
```bash
python -m venv venv
```

2. **Activar el entorno virtual:**
```bash
# PowerShell
.\venv\Scripts\Activate.ps1

# CMD
venv\Scripts\activate.bat
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

### Opción 2: Instalación Global

```bash
pip install -r requirements.txt
```

## 📦 Dependencias

- **sly**: Analizador léxico y sintáctico
- **rich**: Visualización mejorada en terminal
- **tabulate**: Formato de tablas
- **pandas**: Manipulación de datos
- **llvmlite**: Generación de código LLVM IR
- **multimethod**: Patrón Visitor con métodos múltiples
- **graphviz**: Visualización de AST (opcional)

## 🎯 Uso

### Análisis Léxico
```bash
python bminor.py --scan archivo.bminor
```

### Análisis Sintáctico
```bash
python bminor.py --parse archivo.bminor
```

### Análisis Semántico
```bash
python bminor.py --check archivo.bminor
```

### Generación de Código LLVM IR
```bash
python bminor.py --codegen archivo.bminor
```

Esto genera un archivo `output.ll` con el código LLVM IR.

### Compilar y Ejecutar

1. **Compilar el IR a ejecutable:**
```bash
clang output.ll runtime.c -o programa
```

2. **Ejecutar:**
```bash
.\programa.exe
```

## 📁 Estructura del Proyecto

```
Compilador/
├── bminor.py          # Punto de entrada principal
├── bminor_lexer.py    # Analizador léxico
├── parser.py          # Analizador sintáctico
├── checker.py         # Verificador de tipos
├── codegen.py         # Generador de código LLVM
├── model.py           # Definiciones del AST
├── typesys.py         # Sistema de tipos
├── symtab.py          # Tabla de símbolos
├── errors.py          # Manejo de errores
├── runtime.c          # Funciones de runtime
├── requirements.txt   # Dependencias Python
└── test/              # Archivos de prueba
    ├── scanner/       # Pruebas de análisis léxico
    ├── parser/        # Pruebas de análisis sintáctico
    ├── typechecker/   # Pruebas de análisis semántico
    └── codegen/       # Pruebas de generación de código
```

## 🔧 Solución de Problemas

### Error: "No module named 'sly'"
```bash
pip install -r requirements.txt
```

### Error al compilar con clang
Asegúrate de tener LLVM y Clang instalados:
- **Windows**: Descarga desde [LLVM Releases](https://github.com/llvm/llvm-project/releases) y agrega Clang al PATH

### Error con llvmlite
Si tienes problemas con llvmlite, asegúrate de tener la versión correcta de LLVM instalada. llvmlite requiere LLVM 11-15.

## 📝 Ejemplo Completo

```bash
# 1. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 2. Compilar un archivo de prueba
python bminor.py --codegen test/codegen/test.bminor

# 3. Compilar el IR a ejecutable
clang output.ll runtime.c -o test_program

# 4. Ejecutar
.\test_program.exe
```

## 🧪 Pruebas

El proyecto incluye archivos de prueba organizados por fase:
- `test/scanner/` - Pruebas de análisis léxico
- `test/parser/` - Pruebas de análisis sintáctico
- `test/typechecker/` - Pruebas de análisis semántico
- `test/codegen/` - Pruebas de generación de código

