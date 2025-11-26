# EXPLICACIÓN DE LAS FASES DEL COMPILADOR

## Resumen del Flujo

Cuando ejecutas `python bminor.py --codegen archivo.bminor`, el compilador pasa por estas fases:

```
Código Fuente (.bminor)
    ↓
[1] ANÁLISIS LÉXICO (bminor_lexer.py)
    ↓ Tokens
[2] ANÁLISIS SINTÁCTICO (parser.py)
    ↓ AST (Árbol de Sintaxis Abstracta)
[3] ANÁLISIS SEMÁNTICO (checker.py)
    ↓ AST Verificado
[4] GENERACIÓN DE CÓDIGO (codegen.py)
    ↓
Código LLVM IR (output.ll)
```

---

## FASE 1: ANÁLISIS LÉXICO (Scanning)

**Comando:** `python bminor.py --scan archivo.bminor`

### Archivo Principal: `bminor_lexer.py`

**Clase:** `Lexer` (hereda de `sly.Lexer`)

### ¿Qué hace?
Convierte el código fuente en una secuencia de **tokens** (unidades léxicas).

### Proceso:

1. **Lee el código fuente** (líneas 13-20 en `bminor.py`)
   ```python
   with open(input_file, 'r', encoding='utf-8') as source_file:
       source_code = source_file.read()
   ```

2. **Crea el analizador léxico** (línea 22 en `bminor.py`)
   ```python
   token_analyzer = Lexer()
   ```

3. **Tokeniza el código** (línea 34 en `bminor.py`)
   ```python
   for token in token_analyzer.tokenize(source_code):
   ```

4. **Identifica tokens** usando expresiones regulares en `bminor_lexer.py`:
   - **Palabras reservadas**: `function`, `if`, `while`, `return`, etc.
   - **Identificadores**: nombres de variables y funciones
   - **Literales**: números (`INTEGER_LITERAL`, `FLOAT_LITERAL`), cadenas (`STRING_LITERAL`), caracteres (`CHAR_LITERAL`)
   - **Operadores**: `+`, `-`, `*`, `/`, `==`, `!=`, `&&`, `||`, etc.
   - **Símbolos**: `(`, `)`, `{`, `}`, `;`, `,`, etc.

### Ejemplo de Tokens Generados:
```
INPUT: "x: integer = 10;"
TOKENS:
  - ID("x")
  - COLON(":")
  - INTEGER("integer")
  - ASSIGN("=")
  - INTEGER_LITERAL(10)
  - SEMICOLON(";")
```

### Archivos Involucrados:
- `bminor.py` → función `perform_lexical_analysis()` (líneas 13-59)
- `bminor_lexer.py` → clase `Lexer` (define todos los tokens y reglas)

---

## FASE 2: ANÁLISIS SINTÁCTICO (Parsing)

**Comando:** `python bminor.py --parse archivo.bminor`

### Archivo Principal: `parser.py`

**Clase:** `Parser` (hereda de `sly.Parser`)

### ¿Qué hace?
Toma la secuencia de tokens y construye un **Árbol de Sintaxis Abstracta (AST)** según la gramática del lenguaje.

### Proceso:

1. **Lee el código fuente** (líneas 64-68 en `bminor.py`)

2. **Limpia errores previos** (línea 70 en `bminor.py`)
   ```python
   clear_errors()
   ```

3. **Parsea el código** (línea 72 en `bminor.py`)
   ```python
   syntax_tree = parse(source_code)
   ```
   Esta función crea un `Parser` y llama a `parser.parse()`

4. **Construye el AST** usando reglas gramaticales en `parser.py`:
   - **Programa**: `prog` → lista de declaraciones
   - **Declaraciones**: variables, arrays, funciones
   - **Expresiones**: aritméticas, lógicas, comparaciones
   - **Sentencias**: asignaciones, condicionales, bucles, retornos

### Ejemplo de AST Generado:
```
INPUT: "factorial: function integer (n: integer) = { return n * factorial(n-1); }"

AST:
FunctionDecl(
  name="factorial",
  return_type="integer",
  params=[Param("n", "integer")],
  body=BlockStmt([
    ReturnStmt(
      BinaryExpr(
        "*",
        VarExpr("n"),
        CallExpr("factorial", [BinaryExpr("-", VarExpr("n"), IntegerLiteral(1))])
      )
    )
  ])
)
```

### Archivos Involucrados:
- `bminor.py` → función `perform_syntax_analysis()` (líneas 61-81)
- `parser.py` → clase `Parser` (define la gramática)
- `model.py` → define las clases del AST (Program, FunctionDecl, VarDecl, etc.)

---

## FASE 3: ANÁLISIS SEMÁNTICO (Type Checking)

**Comando:** `python bminor.py --check archivo.bminor`

### Archivo Principal: `checker.py`

**Clase:** `SemanticAnalyzer` (hereda de `Visitor`)

### ¿Qué hace?
Recorre el AST y verifica:
- **Tipos**: que las expresiones tengan tipos compatibles
- **Declaraciones**: que las variables estén declaradas antes de usarse
- **Ámbitos**: que las variables sean accesibles en su contexto
- **Funciones**: que los parámetros y valores de retorno sean correctos

### Proceso:

1. **Parsea el código** (línea 94 en `bminor.py`)
   ```python
   syntax_tree = parse(source_code)
   ```

2. **Ejecuta el analizador semántico** (línea 104 en `bminor.py`)
   ```python
   global_symbol_table = SemanticAnalyzer.checker(syntax_tree)
   ```

3. **Recorre el AST** usando el patrón Visitor:
   - Crea una **tabla de símbolos** global
   - Visita cada nodo del AST
   - Para cada declaración: agrega el símbolo a la tabla
   - Para cada uso: verifica que el símbolo exista y tenga el tipo correcto

### Verificaciones Realizadas:

**En `checker.py`:**

- **Variables** (líneas 36-50):
  ```python
  def visit(self, n: VarDecl, env: SymbolTable):
      # Verifica que el tipo de la inicialización coincida
      if n.value:
          if n.sym_type != n.value.type:
              error("Error de tipo...")
  ```

- **Expresiones Binarias** (líneas ~150-170):
  ```python
  def visit(self, n: BinaryExpr, env: SymbolTable):
      # Verifica tipos compatibles para operaciones
      n.type = check_binop(n.op, left_type, right_type)
  ```

- **Llamadas a Funciones** (líneas ~200-220):
  ```python
  def visit(self, n: CallExpr, env: SymbolTable):
      # Verifica que la función exista
      # Verifica que los parámetros coincidan
  ```

### Archivos Involucrados:
- `bminor.py` → función `perform_semantic_analysis()` (líneas 83-111)
- `checker.py` → clase `SemanticAnalyzer` (visita y verifica el AST)
- `symtab.py` → clase `SymbolTable` (gestiona símbolos y ámbitos)
- `typesys.py` → funciones `check_binop()`, `check_unaryop()` (verifica compatibilidad de tipos)

---

## FASE 4: GENERACIÓN DE CÓDIGO (Code Generation)

**Comando:** `python bminor.py --codegen archivo.bminor`

### Archivo Principal: `codegen.py`

**Clase:** `IRGenerator` (hereda de `Visitor`)

### ¿Qué hace?
Recorre el AST verificado y genera código **LLVM IR** (código intermedio).

### Proceso:

1. **Parsea y verifica** (líneas 127-140 en `bminor.py`)
   ```python
   syntax_tree = parse(source_code)
   global_symbol_table = SemanticAnalyzer.checker(syntax_tree)
   ```

2. **Genera código LLVM** (línea 145 en `bminor.py`)
   ```python
   llvm_ir_output = generate_code(syntax_tree)
   ```

3. **Escribe el archivo** (líneas 147-149 en `bminor.py`)
   ```python
   with open("output.ll", 'w') as output:
       output.write(llvm_ir_output)
   ```

4. **Traduce cada nodo del AST** a código LLVM IR en `codegen.py`:

### Traducciones Principales:

**Variables** (líneas ~200-250):
```python
def visit(self, n: VarDecl, env):
    # Crea una variable LLVM
    var = self.constructor_ir.alloca(tipo_llvm, name=n.name)
    self.variables[n.name] = var
```

**Expresiones Binarias** (líneas ~400-500):
```python
def visit(self, n: BinaryExpr, env):
    left = self.visit(n.left, env)
    right = self.visit(n.right, env)
    if n.op == '+':
        return self.constructor_ir.add(left, right)
    elif n.op == '*':
        return self.constructor_ir.mul(left, right)
```

**Funciones** (líneas ~600-700):
```python
def visit(self, n: FunctionDecl, env):
    # Crea la función LLVM
    tipo_funcion = ir.FunctionType(tipo_retorno, tipos_params)
    funcion_llvm = ir.Function(self.llvm_module, tipo_funcion, name=n.name)
    # Genera el cuerpo de la función
    for stmt in n.body.statements:
        self.visit(stmt, env)
```

**Llamadas a Funciones** (líneas ~700-750):
```python
def visit(self, n: CallExpr, env):
    # Obtiene la función LLVM
    funcion = self.funciones_llvm[n.name]
    # Genera los argumentos
    args = [self.visit(arg, env) for arg in n.args]
    # Crea la llamada
    return self.constructor_ir.call(funcion, args)
```

### Ejemplo de Código Generado:

**INPUT (B-Minor):**
```bminor
suma: function integer (a: integer, b: integer) = {
    return a + b;
}
```

**OUTPUT (LLVM IR):**
```llvm
define i64 @suma(i64 %a, i64 %b) {
entry:
  %add = add i64 %a, %b
  ret i64 %add
}
```

### Archivos Involucrados:
- `bminor.py` → función `generate_llvm_code()` (líneas 113-157)
- `codegen.py` → clase `IRGenerator` (genera código LLVM)
- `model.py` → clases del AST (usadas para recorrer el árbol)

---

## RESUMEN POR ARCHIVO

| Archivo | Fase | Función Principal |
|---------|------|-------------------|
| `bminor.py` | Todas | Punto de entrada, coordina todas las fases |
| `bminor_lexer.py` | Léxico | `Lexer.tokenize()` - Convierte código a tokens |
| `parser.py` | Sintáctico | `Parser.parse()` - Construye el AST |
| `checker.py` | Semántico | `SemanticAnalyzer.checker()` - Verifica tipos y símbolos |
| `codegen.py` | Generación | `IRGenerator.visit()` - Genera código LLVM IR |
| `model.py` | Todas | Define las clases del AST |
| `symtab.py` | Semántico | `SymbolTable` - Gestiona símbolos y ámbitos |
| `typesys.py` | Semántico | Funciones de verificación de tipos |

---

## FLUJO COMPLETO EN CÓDIGO

```python
# bminor.py - función generate_llvm_code()

# 1. LÉXICO + SINTÁCTICO
syntax_tree = parse(source_code)  # → parser.py → usa bminor_lexer.py

# 2. SEMÁNTICO
global_symbol_table = SemanticAnalyzer.checker(syntax_tree)  # → checker.py

# 3. GENERACIÓN DE CÓDIGO
llvm_ir_output = generate_code(syntax_tree)  # → codegen.py

# 4. ESCRITURA
with open("output.ll", 'w') as output:
    output.write(llvm_ir_output)
```

---

## EJEMPLO PRÁCTICO COMPLETO

**Código Fuente:**
```bminor
x: integer = 10;
y: integer = 20;
resultado: integer = x + y;
```

**Fase 1 - Tokens:**
```
ID("x"), COLON, INTEGER, ASSIGN, INTEGER_LITERAL(10), SEMICOLON,
ID("y"), COLON, INTEGER, ASSIGN, INTEGER_LITERAL(20), SEMICOLON,
ID("resultado"), COLON, INTEGER, ASSIGN, ID("x"), PLUS, ID("y"), SEMICOLON
```

**Fase 2 - AST:**
```
Program([
  VarDecl("x", "integer", IntegerLiteral(10)),
  VarDecl("y", "integer", IntegerLiteral(20)),
  VarDecl("resultado", "integer", BinaryExpr("+", VarExpr("x"), VarExpr("y")))
])
```

**Fase 3 - Verificación:**
- ✅ "x" declarada como integer
- ✅ "y" declarada como integer
- ✅ "x + y" es válido (integer + integer = integer)
- ✅ "resultado" puede recibir integer

**Fase 4 - LLVM IR:**
```llvm
%x = alloca i64
store i64 10, i64* %x
%y = alloca i64
store i64 20, i64* %y
%resultado = alloca i64
%1 = load i64, i64* %x
%2 = load i64, i64* %y
%3 = add i64 %1, %2
store i64 %3, i64* %resultado
```

---

## NOTAS IMPORTANTES

1. **Cada fase depende de la anterior**: No puedes hacer análisis semántico sin sintaxis, ni generación sin semántica.

2. **El AST es la estructura central**: Se crea en la fase sintáctica y se usa en las fases siguientes.

3. **El patrón Visitor**: Tanto `SemanticAnalyzer` como `IRGenerator` usan el patrón Visitor para recorrer el AST.

4. **Tabla de símbolos**: Se construye durante el análisis semántico y se usa para verificar que las variables existan.

5. **LLVM IR es código intermedio**: No es código máquina, pero es muy cercano y puede compilarse a código máquina eficiente.

