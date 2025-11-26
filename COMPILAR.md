# 📖 Guía para Compilar Código B-Minor

Esta guía te explica cómo compilar código B-Minor usando tu compilador.

## 🚀 Método Rápido (Recomendado)

### Usando el script automático:

```bash
compilar.bat mi_programa.bminor
```

Esto automáticamente:
1. Genera el código LLVM IR (`output.ll`)
2. Compila el IR a ejecutable (`mi_programa.exe`)
3. Ejecuta el programa

---

## 📝 Método Manual (Paso a Paso)

### Paso 1: Generar Código LLVM IR

Ejecuta el compilador con la opción `--codegen`:

```bash
python bminor.py --codegen archivo.bminor
```

Esto genera un archivo `output.ll` con el código LLVM IR.

**Ejemplo:**
```bash
python bminor.py --codegen mi_programa.bminor
```

### Paso 2: Compilar LLVM IR a Ejecutable

Usa `clang` para compilar el archivo `.ll` junto con `runtime.cpp`:

```bash
clang output.ll runtime.cpp -o mi_programa.exe
```

**Nota:** Si tienes `runtime.c` en lugar de `runtime.cpp`, usa:
```bash
clang output.ll runtime.c -o mi_programa.exe
```

### Paso 3: Ejecutar el Programa

```bash
.\mi_programa.exe
```

---

## 🔍 Verificar el Código Antes de Compilar

Antes de compilar, puedes verificar tu código en diferentes etapas:

### 1. Análisis Léxico (ver tokens)
```bash
python bminor.py --scan archivo.bminor
```

### 2. Análisis Sintáctico (ver AST)
```bash
python bminor.py --parse archivo.bminor
```

### 3. Análisis Semántico (verificar tipos)
```bash
python bminor.py --check archivo.bminor
```

### 4. Ejecutar con Intérprete (sin compilar)
```bash
python bminor.py --interp archivo.bminor
```

---

## ⚠️ Requisitos

1. **Python 3.8+** con las dependencias instaladas
2. **Clang/LLVM** instalado y en el PATH
3. **Archivo `runtime.cpp`** o `runtime.c` en el directorio actual

### Verificar que Clang está instalado:
```bash
clang --version
```

---

## 📋 Ejemplo Completo

Supongamos que tu profesor te dio un archivo llamado `tarea.bminor`:

```bash
# 1. Verificar que no tiene errores
python bminor.py --check tarea.bminor

# 2. Generar código LLVM
python bminor.py --codegen tarea.bminor

# 3. Compilar a ejecutable
clang output.ll runtime.cpp -o tarea.exe

# 4. Ejecutar
.\tarea.exe
```

O simplemente:
```bash
compilar.bat tarea.bminor
```

---

## 🐛 Solución de Problemas

### Error: "No se generó output.ll"
- Verifica que el código B-Minor no tenga errores sintácticos o semánticos
- Ejecuta `python bminor.py --check archivo.bminor` primero

### Error: "clang no se encontró"
- Instala LLVM/Clang desde: https://github.com/llvm/llvm-project/releases
- Asegúrate de agregarlo al PATH del sistema

### Error: "símbolo externo sin resolver"
- Verifica que `runtime.cpp` o `runtime.c` exista en el directorio actual
- Asegúrate de usar el mismo archivo runtime que se usó para generar el código

---

## 💡 Consejos

- **Siempre verifica primero:** Usa `--check` antes de compilar para detectar errores
- **Usa el intérprete para probar:** `--interp` es más rápido para probar código
- **Revisa `output.ll`:** Si hay problemas, puedes ver el código LLVM generado
- **Nombres de archivos:** Evita espacios en los nombres de archivos

