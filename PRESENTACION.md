# Compilador B-Minor
## Presentación del Proyecto

---

## Índice

1. [Introducción](#introducción)
2. [Objetivos del Proyecto](#objetivos-del-proyecto)
3. [Arquitectura del Compilador](#arquitectura-del-compilador)
4. [Fases de Compilación](#fases-de-compilación)
5. [Características Implementadas](#características-implementadas)
6. [Tecnologías Utilizadas](#tecnologías-utilizadas)
7. [Ejemplos Prácticos](#ejemplos-prácticos)
8. [Demostración](#demostración)
9. [Conclusiones](#conclusiones)

---

## Introducción

### ¿Qué es B-Minor?

**B-Minor** es un lenguaje de programación educativo similar a C, diseñado para enseñar los conceptos fundamentales de compilación.

### ¿Qué hemos construido?

Un **compilador completo** que traduce código fuente B-Minor a **LLVM IR** (código intermedio), capaz de generar ejecutables optimizados.

### ¿Por qué es importante?

- Implementa todas las fases de un compilador real
- Genera código LLVM IR portable y optimizable
- Demuestra comprensión profunda de sistemas de compilación
- Base para futuras extensiones y optimizaciones

---

## Objetivos del Proyecto

### Objetivo Principal
Implementar un compilador funcional que traduzca código fuente B-Minor a código LLVM IR.

### Objetivos Específicos

1. **Análisis Léxico**
   - Identificar tokens del lenguaje
   - Detectar errores léxicos

2. **Análisis Sintáctico**
   - Construir el Árbol de Sintaxis Abstracta (AST)
   - Validar la estructura gramatical

3. **Análisis Semántico**
   - Verificar tipos y compatibilidad
   - Validar declaraciones y uso de variables

4. **Generación de Código**
   - Traducir AST a LLVM IR
   - Generar código ejecutable

---

## Arquitectura del Compilador

### Flujo General

```
Código Fuente (.bminor)
    ↓
[1] ANÁLISIS LÉXICO
    ↓ Tokens
[2] ANÁLISIS SINTÁCTICO
    ↓ AST (Árbol de Sintaxis Abstracta)
[3] ANÁLISIS SEMÁNTICO
    ↓ AST Verificado
[4] GENERACIÓN DE CÓDIGO
    ↓
Código LLVM IR (output.ll)
    ↓
[5] COMPILACIÓN (Clang)
    ↓
Ejecutable (.exe)
```

### Estructura Modular

| Módulo | Responsabilidad |
|--------|----------------|
| `bminor_lexer.py` | Análisis léxico - Identificación de tokens |
| `parser.py` | Análisis sintáctico - Construcción del AST |
| `checker.py` | Análisis semántico - Verificación de tipos |
| `codegen.py` | Generación de código - Traducción a LLVM IR |
| `model.py` | Definiciones del AST |
| `symtab.py` | Gestión de tabla de símbolos |
| `typesys.py` | Sistema de tipos |
| `errors.py` | Manejo de errores |

---

## Fases de Compilación

### Fase 1: Análisis Léxico (Scanning)

**Comando:** `python bminor.py --scan archivo.bminor`

**¿Qué hace?**
- Convierte el código fuente en una secuencia de **tokens**
- Identifica palabras clave, identificadores, literales, operadores

**Ejemplo:**
```bminor
x: integer = 10;
```

**Tokens generados:**
- `ID("x")`
- `COLON(":")`
- `INTEGER("integer")`
- `ASSIGN("=")`
- `INTEGER_LITERAL(10)`
- `SEMICOLON(";")`

**Tecnología:** SLY (Simple Lex Yacc) - Parser Generator

---

### Fase 2: Análisis Sintáctico (Parsing)

**Comando:** `python bminor.py --parse archivo.bminor`

**¿Qué hace?**
- Construye el **Árbol de Sintaxis Abstracta (AST)**
- Verifica que el código siga la gramática del lenguaje

**Ejemplo de AST:**
```bminor
factorial: function integer (n: integer) = {
    return n * factorial(n-1);
}
```

**AST generado:**
```
FunctionDecl(
  name="factorial",
  return_type="integer",
  params=[Param("n", "integer")],
  body=BlockStmt([
    ReturnStmt(
      BinaryExpr("*", VarExpr("n"), 
        CallExpr("factorial", [...])
      )
    )
  ])
)
```

**Tecnología:** SLY - Análisis descendente recursivo

---

### Fase 3: Análisis Semántico (Type Checking)

**Comando:** `python bminor.py --check archivo.bminor`

**¿Qué hace?**
- Verifica tipos en expresiones
- Valida declaraciones de variables
- Verifica llamadas a funciones
- Detecta variables no declaradas
- Valida parámetros de funciones

**Verificaciones realizadas:**
- Compatibilidad de tipos en operaciones
- Variables declaradas antes de usarse
- Parámetros de funciones correctos
- Tipos de retorno válidos
- Ámbitos y visibilidad

**Tecnología:** Patrón Visitor para recorrer el AST

---

### Fase 4: Generación de Código (Code Generation)

**Comando:** `python bminor.py --codegen archivo.bminor`

**¿Qué hace?**
- Recorre el AST verificado
- Genera código **LLVM IR**
- Crea archivo `output.ll`

**Ejemplo de traducción:**

**Entrada (B-Minor):**
```bminor
suma: function integer (a: integer, b: integer) = {
    return a + b;
}
```

**Salida (LLVM IR):**
```llvm
define i64 @suma(i64 %a, i64 %b) {
entry:
  %add = add i64 %a, %b
  ret i64 %add
}
```

**Tecnología:** llvmlite - Biblioteca Python para LLVM

---

## Características Implementadas

### Tipos de Datos

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `integer` | Números enteros | `x: integer = 42;` |
| `boolean` | Valores booleanos | `flag: boolean = true;` |
| `float` | Números de punto flotante | `pi: float = 3.14;` |
| `char` | Caracteres | `c: char = 'A';` |
| `string` | Cadenas de texto | `s: string = "Hola";` |
| `array` | Arreglos | `arr: array[10] integer;` |

### Estructuras de Control

**Condicionales**
- `if`, `if-else`
- Expresiones booleanas complejas

**Bucles**
- `while`
- `do-while`
- `for`

**Expresiones**
- Aritméticas: `+`, `-`, `*`, `/`, `%`
- Relacionales: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Lógicas: `&&`, `||`, `!`

### Funciones

- Declaración de funciones
- Parámetros y valores de retorno
- Recursión
- Ámbitos y visibilidad
- Funciones built-in

### Operadores

| Categoría | Operadores |
|-----------|-----------|
| Aritméticos | `+`, `-`, `*`, `/`, `%` |
| Relacionales | `==`, `!=`, `<`, `>`, `<=`, `>=` |
| Lógicos | `&&`, `||`, `!` |
| Asignación | `=`, `+=`, `-=`, `*=`, `/=` |
| Incremento/Decremento | `++`, `--` |

---

## Tecnologías Utilizadas

### Lenguajes y Frameworks

| Tecnología | Propósito |
|------------|-----------|
| **Python 3.8+** | Lenguaje principal del compilador |
| **SLY** | Generador de analizadores léxicos y sintácticos |
| **llvmlite** | Generación de código LLVM IR |
| **LLVM/Clang** | Compilación del código IR a ejecutable |

### Bibliotecas Python

- **sly**: Analizador léxico y sintáctico
- **rich**: Visualización mejorada en terminal
- **tabulate**: Formato de tablas
- **pandas**: Manipulación de datos
- **llvmlite**: Interfaz con LLVM
- **multimethod**: Patrón Visitor con métodos múltiples

### Herramientas

- **Clang**: Compilador LLVM para generar ejecutables
- **Git**: Control de versiones

---

## Ejemplos Prácticos

### Ejemplo 1: Función Recursiva (Fibonacci)

**Código B-Minor:**
```bminor
fibonacci: function integer (n: integer) = {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n-1) + fibonacci(n-2);
}

main: function void () = {
    resultado: integer = fibonacci(10);
    print(resultado);
}
```

**Proceso de compilación:**
```bash
# 1. Generar LLVM IR
python bminor.py --codegen fibonacci.bminor

# 2. Compilar a ejecutable
clang output.ll runtime.c -o fibonacci.exe

# 3. Ejecutar
.\fibonacci.exe
```

---

### Ejemplo 2: Operaciones con Arrays

**Código B-Minor:**
```bminor
main: function void () = {
    arr: array[5] integer;
    i: integer = 0;
    
    while (i < 5) {
        arr[i] = i * 2;
        i = i + 1;
    }
    
    suma: integer = 0;
    i = 0;
    while (i < 5) {
        suma = suma + arr[i];
        i = i + 1;
    }
    
    print(suma);
}
```

---

### Ejemplo 3: Verificación de Tipos

El compilador detecta errores de tipo:

```bminor
x: integer = 10;
y: boolean = true;
resultado: integer = x + y;  // Error: no se puede sumar integer + boolean
```

**Salida del compilador:**
```
Error semántico: Tipos incompatibles en operación binaria
  Línea 3: resultado: integer = x + y;
```

---

## Demostración

### Flujo Completo de Compilación

1. **Análisis Léxico**
   ```bash
   python bminor.py --scan ejemplo.bminor
   ```
   - Muestra todos los tokens identificados
   - Tabla organizada con tipo y posición

2. **Análisis Sintáctico**
   ```bash
   python bminor.py --parse ejemplo.bminor
   ```
   - Construye y muestra el AST
   - Detecta errores de sintaxis

3. **Análisis Semántico**
   ```bash
   python bminor.py --check ejemplo.bminor
   ```
   - Verifica tipos y declaraciones
   - Muestra tabla de símbolos

4. **Generación de Código**
   ```bash
   python bminor.py --codegen ejemplo.bminor
   ```
   - Genera `output.ll` con código LLVM IR

5. **Compilación y Ejecución**
   ```bash
   clang output.ll runtime.c -o programa.exe
   .\programa.exe
   ```

---

## Estadísticas del Proyecto

### Archivos Principales

- **~15 módulos Python** implementando las fases del compilador
- **~2000+ líneas de código** en total
- **Sistema completo** de manejo de errores
- **Tabla de símbolos** con gestión de ámbitos
- **Sistema de tipos** robusto

### Cobertura de Funcionalidades

- Análisis léxico completo
- Análisis sintáctico completo
- Análisis semántico completo
- Generación de código LLVM IR
- Soporte para todos los tipos básicos
- Estructuras de control
- Funciones y recursión
- Arrays y operaciones con arrays

---

## Conclusiones

### Logros Alcanzados

- **Compilador funcional completo** con todas las fases implementadas
- **Generación de código LLVM IR** optimizable y portable
- **Sistema robusto de verificación de tipos**
- **Manejo completo de errores** en todas las fases
- **Arquitectura modular** y extensible

### Aprendizajes

- Comprensión profunda de las fases de compilación
- Implementación práctica de teoría de compiladores
- Trabajo con tecnologías modernas (LLVM, SLY)
- Diseño de sistemas complejos

### Posibles Mejoras Futuras

- Optimizaciones del código generado
- Soporte para más características del lenguaje
- Mejor manejo de errores con sugerencias
- Interfaz gráfica para visualización del AST
- Debugger integrado

---

## Preguntas y Respuestas

### Preguntas Frecuentes

**¿Por qué LLVM IR?**
- Código intermedio portable
- Optimizaciones automáticas
- Compatible con múltiples arquitecturas
- Estándar de la industria

**¿Qué tan eficiente es el código generado?**
- El código LLVM IR puede ser optimizado por el backend de LLVM
- Genera código comparable a compiladores profesionales

**¿Se puede extender el lenguaje?**
- Sí, la arquitectura modular permite agregar nuevas características fácilmente

---

## Referencias y Recursos

- **LLVM Documentation**: https://llvm.org/docs/
- **SLY Parser Generator**: https://sly.readthedocs.io/
- **B-Minor Language Specification**
- **Compiladores: Principios, Técnicas y Herramientas** (Dragon Book)

---

## Gracias por su Atención

### Contacto y Repositorio

- **Proyecto**: Compilador B-Minor
- **Autor**: [Tu Nombre]
- **Fecha**: [Fecha de Presentación]

---

*"La mejor forma de aprender compiladores es construyendo uno"*

