# GUION DE SUSTENTACIÓN - COMPILADOR B-MINOR

## 1. INTRODUCCIÓN (2 minutos)

### Saludo y Presentación
- Buenos días/tardes profesor
- Presentar el proyecto: Compilador completo para el lenguaje B-Minor
- Objetivo: Implementar un compilador que traduzca código fuente B-Minor a código LLVM IR

### Contexto del Proyecto
- Lenguaje B-Minor: lenguaje de programación educativo similar a C
- Tecnologías utilizadas: Python, LLVM, SLY (parser generator)
- Resultado: Compilador funcional con todas las fases de compilación

---

## 2. ARQUITECTURA DEL COMPILADOR (3 minutos)

### Estructura Modular
El compilador está dividido en módulos especializados:

1. **bminor_lexer.py** - Analizador Léxico
   - Identifica tokens del lenguaje
   - Maneja errores léxicos

2. **parser.py** - Analizador Sintáctico
   - Construye el Árbol de Sintaxis Abstracta (AST)
   - Verifica la estructura gramatical

3. **checker.py** - Analizador Semántico
   - Verificación de tipos
   - Validación de declaraciones y uso de variables

4. **codegen.py** - Generador de Código
   - Traduce AST a código LLVM IR
   - Optimizaciones básicas

5. **symtab.py** - Tabla de Símbolos
   - Gestión de variables y funciones
   - Resolución de ámbitos

6. **typesys.py** - Sistema de Tipos
   - Definición de tipos del lenguaje
   - Verificación de compatibilidad

---

## 3. FASES DE COMPILACIÓN (5 minutos)

### Fase 1: Análisis Léxico (Scanning)
**Comando:** `python bminor.py --scan archivo.bminor`

**Funcionalidad:**
- Identifica tokens: palabras clave, identificadores, literales, operadores
- Detecta errores léxicos (caracteres ilegales)
- Genera lista de tokens con posición (línea, columna)

**Ejemplo de salida:**
- Tokens identificados con su tipo y posición
- Tabla organizada de todos los tokens encontrados

### Fase 2: Análisis Sintáctico (Parsing)
**Comando:** `python bminor.py --parse archivo.bminor`

**Funcionalidad:**
- Construye el AST según la gramática del lenguaje
- Verifica estructura sintáctica correcta
- Detecta errores de sintaxis (paréntesis, llaves, etc.)

**Características:**
- Soporte para expresiones complejas
- Declaraciones de variables y funciones
- Estructuras de control (if, while, for)

### Fase 3: Análisis Semántico (Type Checking)
**Comando:** `python bminor.py --check archivo.bminor`

**Funcionalidad:**
- Verificación de tipos en expresiones
- Validación de declaraciones de variables
- Verificación de llamadas a funciones
- Detección de variables no declaradas
- Validación de parámetros de funciones

**Tipos soportados:**
- `integer` - Números enteros
- `boolean` - Valores booleanos
- `float` - Números de punto flotante
- `char` - Caracteres
- `string` - Cadenas de texto
- `array` - Arreglos

### Fase 4: Generación de Código (Code Generation)
**Comando:** `python bminor.py --codegen archivo.bminor`

**Funcionalidad:**
- Traduce el AST a código LLVM IR
- Genera archivo `output.ll` con código intermedio
- Código optimizado y listo para compilación

**Ventajas de LLVM IR:**
- Código portable
- Optimizaciones automáticas
- Compatible con múltiples arquitecturas

---

## 4. CARACTERÍSTICAS IMPLEMENTADAS (4 minutos)

### Tipos de Datos
✅ Enteros (`integer`)
✅ Booleanos (`boolean`)
✅ Punto flotante (`float`)
✅ Caracteres (`char`)
✅ Cadenas (`string`)
✅ Arreglos (`array`)

### Estructuras de Control
✅ Condicionales: `if`, `if-else`
✅ Bucles: `while`, `do-while`, `for`
✅ Expresiones booleanas complejas

### Funciones
✅ Declaración de funciones
✅ Parámetros y valores de retorno
✅ Recursión
✅ Ámbitos y visibilidad

### Operadores
✅ Aritméticos: `+`, `-`, `*`, `/`, `%`
✅ Relacionales: `==`, `!=`, `<`, `>`, `<=`, `>=`
✅ Lógicos: `&&`, `||`, `!`
✅ Asignación: `=`, `+=`, `-=`, etc.
✅ Incremento/Decremento: `++`, `--`

### Características Avanzadas
✅ Tabla de símbolos con resolución de ámbitos
✅ Sistema de tipos robusto
✅ Manejo de errores completo
✅ Mensajes de error descriptivos

---

## 5. DEMOSTRACIÓN PRÁCTICA (5 minutos)

### Demostración Paso a Paso

**Paso 1: Mostrar código fuente de ejemplo**
```bminor
// Archivo: prueba_completa.bminor
suma: function integer (a: integer, b: integer) = {
    return a + b;
}

main: function void () = {
    resultado: integer = suma(10, 20);
    print(resultado);
}
```

**Paso 2: Ejecutar análisis léxico**
```bash
python bminor.py --scan prueba_completa.bminor
```
- Mostrar tokens identificados

**Paso 3: Ejecutar análisis sintáctico**
```bash
python bminor.py --parse prueba_completa.bminor
```
- Mostrar AST generado (si está disponible)

**Paso 4: Ejecutar análisis semántico**
```bash
python bminor.py --check prueba_completa.bminor
```
- Verificar que no hay errores semánticos

**Paso 5: Generar código LLVM IR**
```bash
python bminor.py --codegen prueba_completa.bminor
```
- Mostrar fragmento del archivo `output.ll` generado

**Paso 6: Compilar y ejecutar**
```bash
# Compilar LLVM IR a ejecutable
clang output.ll runtime.c -o programa.exe

# Ejecutar
.\programa.exe
```
- Mostrar salida del programa ejecutándose

### Scripts de Automatización
- `ejecutar_ejemplo.bat` - Ejecuta ejemplo completo
- `ejecutar_prueba.bat` - Prueba rápida
- `probar_todo.bat` - Prueba todas las fases secuencialmente

---

## 6. PRUEBAS Y VALIDACIÓN (3 minutos)

### Suite de Pruebas
El proyecto incluye más de 60 archivos de prueba organizados por fase:

**Pruebas de Análisis Léxico** (`test/scanner/`)
- 10 casos "good" (correctos)
- 13 casos "bad" (con errores esperados)

**Pruebas de Análisis Sintáctico** (`test/parser/`)
- 3 casos "good"
- 5 casos "bad"

**Pruebas de Análisis Semántico** (`test/typechecker/`)
- 10 casos "good"
- 10 casos "bad"

**Pruebas de Generación de Código** (`test/codegen/`)
- 9 casos de prueba con diferentes características

### Resultados de Pruebas
- ✅ Todas las pruebas pasan correctamente
- ✅ Errores detectados apropiadamente
- ✅ Código generado es válido y ejecutable

---

## 7. ASPECTOS TÉCNICOS DESTACADOS (3 minutos)

### Manejo de Errores
- Errores léxicos: caracteres ilegales
- Errores sintácticos: estructura incorrecta
- Errores semánticos: tipos incompatibles, variables no declaradas
- Mensajes de error claros con posición (línea, columna)

### Optimizaciones
- Generación de código LLVM IR optimizado
- Eliminación de código muerto
- Optimización de expresiones constantes

### Portabilidad
- Código LLVM IR portable entre plataformas
- Compatible con Windows, Linux, macOS
- Compilación a múltiples arquitecturas

### Extensibilidad
- Arquitectura modular facilita agregar características
- Sistema de tipos extensible
- Fácil agregar nuevos operadores o tipos

---

## 8. DIFICULTADES Y SOLUCIONES (2 minutos)

### Desafíos Enfrentados

**1. Integración de LLVM**
- **Problema:** Configurar llvmlite y generar código IR correcto
- **Solución:** Estudio de la documentación de LLVM IR y ejemplos

**2. Sistema de Tipos**
- **Problema:** Verificar compatibilidad de tipos en expresiones complejas
- **Solución:** Implementación de tabla de tipos y reglas de conversión

**3. Resolución de Ámbitos**
- **Problema:** Manejar variables locales vs globales
- **Solución:** Implementación de tabla de símbolos con stack de ámbitos

**4. Generación de Código**
- **Problema:** Traducir AST a código LLVM IR correcto
- **Solución:** Uso del patrón Visitor para recorrer el AST

---

## 9. CONCLUSIONES (2 minutos)

### Logros Alcanzados
✅ Compilador funcional y completo
✅ Todas las fases de compilación implementadas
✅ Generación de código LLVM IR válido
✅ Suite completa de pruebas
✅ Documentación y scripts de automatización

### Aprendizajes
- Comprensión profunda del proceso de compilación
- Experiencia con herramientas modernas (LLVM, SLY)
- Desarrollo de software modular y mantenible
- Manejo de errores y validación

### Posibles Mejoras Futuras
- Optimizaciones más avanzadas
- Soporte para más características del lenguaje
- Depurador integrado
- Interfaz gráfica para visualización del AST

---

## 10. PREGUNTAS Y RESPUESTAS (Tiempo restante)

### Preguntas Frecuentes Esperadas

**P: ¿Por qué LLVM IR y no código máquina directo?**
R: LLVM IR es portable, permite optimizaciones avanzadas y es más fácil de depurar.

**P: ¿Cómo maneja la recursión?**
R: El generador de código crea llamadas recursivas en LLVM IR, que el linker resuelve correctamente.

**P: ¿Qué tan eficiente es el código generado?**
R: El código LLVM IR se beneficia de las optimizaciones del compilador LLVM, generando código eficiente.

**P: ¿Se puede extender fácilmente?**
R: Sí, la arquitectura modular permite agregar nuevas características sin modificar código existente.

---

## NOTAS PARA LA PRESENTACIÓN

### Tiempo Total Estimado: 25-30 minutos

### Material de Apoyo
- Código fuente del compilador
- Archivos de prueba
- Ejemplos de ejecución
- Diagramas de arquitectura (si están disponibles)

### Recomendaciones
1. Tener el entorno preparado antes de la presentación
2. Tener ejemplos de código listos para mostrar
3. Preparar respuestas para preguntas técnicas
4. Mostrar confianza en el conocimiento del código
5. Destacar los aspectos más complejos implementados

### Puntos Clave a Enfatizar
- ✅ Compilador completo y funcional
- ✅ Todas las fases implementadas correctamente
- ✅ Código bien estructurado y documentado
- ✅ Pruebas exhaustivas
- ✅ Generación de código ejecutable

---

## FIN DEL GUION

**¡Éxito en tu sustentación!** 🎓

