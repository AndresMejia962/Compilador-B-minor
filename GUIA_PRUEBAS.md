# 🧪 Guía de Pruebas del Compilador B-Minor

Esta guía te muestra cómo probar tu compilador paso a paso.

## 📋 Prerequisitos

1. **Entorno virtual activado** (si usas uno):
   ```bash
   venv\Scripts\activate.bat
   ```

2. **Dependencias instaladas**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Clang instalado** (para compilar el código LLVM IR generado)

## 🚀 Formas de Probar el Compilador

### Opción 1: Prueba Rápida (Recomendada)

```bash
ejecutar_prueba.bat
```

Este script ejecuta automáticamente:
1. Compilación del archivo `prueba_completa.bminor`
2. Generación de código LLVM IR
3. Compilación a ejecutable
4. Ejecución del programa

### Opción 2: Prueba Manual Paso a Paso

#### Paso 1: Análisis Léxico (Scanner)
Verifica que el código se tokenice correctamente:
```bash
python bminor.py --scan prueba_completa.bminor
```

**Qué verifica:**
- ✅ Todos los tokens se reconocen correctamente
- ✅ No hay caracteres ilegales
- ✅ Los literales se identifican bien

#### Paso 2: Análisis Sintáctico (Parser)
Verifica que la estructura del código sea correcta:
```bash
python bminor.py --parse prueba_completa.bminor
```

**Qué verifica:**
- ✅ El AST se construye correctamente
- ✅ La gramática es válida
- ✅ No hay errores de sintaxis

#### Paso 3: Análisis Semántico (Type Checker)
Verifica tipos y declaraciones:
```bash
python bminor.py --check prueba_completa.bminor
```

**Qué verifica:**
- ✅ Tipos correctos en expresiones
- ✅ Variables declaradas antes de usar
- ✅ Funciones llamadas con argumentos correctos
- ✅ Tablas de símbolos correctas

#### Paso 4: Generación de Código Completa
Genera el código LLVM IR:
```bash
python bminor.py --codegen prueba_completa.bminor
```

Esto genera el archivo `output.ll` con el código LLVM IR.

#### Paso 5: Compilar y Ejecutar
```bash
# Compilar el IR a ejecutable
clang output.ll runtime.c -o prueba_completa.exe

# Ejecutar
.\prueba_completa.exe
```

### Opción 3: Pruebas Individuales

Puedes probar archivos específicos de la carpeta `test/`:

```bash
# Prueba de análisis léxico
python bminor.py --scan test/scanner/good0.bminor

# Prueba de análisis sintáctico
python bminor.py --parse test/parser/good1.bminor

# Prueba de análisis semántico
python bminor.py --check test/typechecker/good0.bminor

# Prueba de generación de código
python bminor.py --codegen test/codegen/fibonacci.bminor
```

## 📊 Qué Prueba `prueba_completa.bminor`

El archivo `prueba_completa.bminor` incluye pruebas para:

1. ✅ **Tipos de Datos**: integer, float, boolean, char, string
2. ✅ **Operadores Aritméticos**: +, -, *, /, %, ^
3. ✅ **Operadores de Comparación**: <, >, <=, >=, ==, !=
4. ✅ **Operadores Lógicos**: &&, ||, !
5. ✅ **Incremento/Decremento**: ++, --
6. ✅ **Estructuras de Control**: if-else, while, do-while, for
7. ✅ **Arrays**: Declaración, inicialización, acceso, modificación
8. ✅ **Funciones**: Declaración, llamadas, parámetros, retorno
9. ✅ **Recursión**: Funciones recursivas
10. ✅ **Expresiones Complejas**: Operaciones anidadas
11. ✅ **Anidamiento**: Estructuras de control anidadas
12. ✅ **Operaciones con Floats**: Aritmética de punto flotante

## 🔍 Interpretando los Resultados

### ✅ Compilación Exitosa
Si todo va bien, verás:
- Mensajes de éxito en cada fase
- Archivo `output.ll` generado
- Ejecutable creado sin errores
- Salida del programa ejecutándose correctamente

### ❌ Errores Comunes

**Error: "No module named 'X'"**
```bash
pip install -r requirements.txt
```

**Error: "clang: command not found"**
- Instala LLVM/Clang
- Asegúrate de que esté en el PATH

**Error de sintaxis en el código**
- Revisa el mensaje de error
- Verifica la línea indicada en `prueba_completa.bminor`

**Error de tipos**
- Verifica que los tipos coincidan
- Revisa las declaraciones de variables y funciones

## 🎯 Ejemplo de Salida Esperada

Cuando ejecutes `ejecutar_prueba.bat`, deberías ver algo como:

```
========================================
Ejecutando Prueba Completa del Compilador
========================================

[1/3] Compilando prueba_completa.bminor...
Fase 1: Análisis Léxico y Sintáctico...
Análisis sintáctico completado sin errores.

Fase 2: Análisis Semántico...
Análisis semántico completado sin errores.

Fase 3: Generación de Código LLVM...
Código LLVM IR generado exitosamente y guardado en 'output.ll'

[2/3] Compilando LLVM IR a ejecutable...

[3/3] Ejecutando programa...
========================================
PRUEBA COMPLETA DEL COMPILADOR B-MINOR
========================================
--- PRUEBA 1: Tipos de Datos ---
...
[Todas las pruebas ejecutándose]
...
========================================
TODAS LAS PRUEBAS COMPLETADAS
========================================
```

## 🛠️ Solución de Problemas

### El compilador no encuentra el archivo
```bash
# Asegúrate de estar en el directorio correcto
cd C:\Users\andre\Desktop\codigoIR\Compilador
```

### Error al activar el entorno virtual
```bash
# Reinstala el entorno virtual
python -m venv venv
```

### El ejecutable no funciona
- Verifica que `runtime.c` esté en el mismo directorio
- Asegúrate de compilar con: `clang output.ll runtime.c -o programa`

## 📝 Notas Adicionales

- El archivo `output.ll` se sobrescribe cada vez que compilas
- Los ejecutables generados pueden tener diferentes nombres según el sistema
- En Windows, los ejecutables terminan en `.exe`

