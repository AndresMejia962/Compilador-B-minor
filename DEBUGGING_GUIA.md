# Guia de Debugging y Perfilamiento

Este documento explica como usar las herramientas avanzadas de debugging, validacion y perfilamiento del interprete B-Minor.

## Caracteristicas Disponibles

### 1. Debugging
- Puntos de interrupcion (breakpoints)
- Inspeccion de variables
- Trazado de ejecucion
- Modo paso a paso

### 2. Validacion en Tiempo de Ejecucion
- Deteccion de division por cero
- Validacion de indices de arrays
- Verificacion de tipos dinamicos

### 3. Manejo Mejorado de Errores
- Mensajes descriptivos
- Stack traces
- Sugerencias de correccion

### 4. Perfilamiento
- Medicion de tiempo de ejecucion
- Conteo de llamadas a funciones
- Analisis de rendimiento

## Uso Basico

### Ejecutar con Debugging

```bash
python bminor.py --interp --debug archivo.bminor
```

### Ejecutar con Perfilamiento

```bash
python bminor.py --interp --profile archivo.bminor
```

### Ejecutar con Ambos

```bash
python bminor.py --interp --debug --profile archivo.bminor
```

## Debugging

### Puntos de Interrupcion

Cuando el interprete encuentra un breakpoint o esta en modo paso a paso, muestra:

```
[Debug] Breakpoint en linea 10
```

Y permite los siguientes comandos:
- `c` o Enter: Continuar ejecucion
- `s`: Ejecutar paso a paso (step)
- `v`: Ver variables actuales
- `q`: Salir del debugging

### Inspeccion de Variables

Durante un breakpoint, puedes ver todas las variables definidas con el comando `v`:

```
Variables:
┌─────────┬──────┬───────┐
│ Nombre  │ Tipo │ Valor │
├─────────┼──────┼───────┤
│ x       │ int  │ 10    │
│ y       │ int  │ 20    │
└─────────┴──────┴───────┘
```

### Trazado de Ejecucion

El sistema registra automaticamente:
- Linea de codigo ejecutada
- Tipo de nodo (Assignment, FuncCall, etc.)
- Estado de las variables en ese momento

## Validacion en Tiempo de Ejecucion

### Division por Cero

El interprete detecta automaticamente divisiones por cero:

```bminor
x: integer = 10;
y: integer = 0;
resultado: integer = x / y;  // Error detectado!
```

**Mensaje de error:**
```
Error en linea 3: Division por cero
Sugerencias:
  - Verifica que el divisor no sea cero antes de dividir
  - Usa una condicion if para validar el divisor
```

### Validacion de Indices de Arrays

```bminor
arr: array [5] integer = {1, 2, 3, 4, 5};
x: integer = arr[10];  // Error: Indice fuera de rango
```

**Mensaje de error:**
```
Error en linea 2: Indice fuera de rango: 10 (array tiene 5 elementos)
Sugerencias:
  - Verifica que el indice este dentro del rango del array
  - Usa length() para obtener el tamano del array antes de indexar
```

### Verificacion de Tipos

El sistema valida tipos en tiempo de ejecucion y registra discrepancias para debugging.

## Manejo Mejorado de Errores

### Stack Traces

Cuando ocurre un error, se muestra un stack trace completo:

```
Error: RuntimeError
Mensaje: Division por cero

Stack Trace:
  -> main (linea 5)
    -> calcular (linea 10)

Ubicacion: Linea 10
```

### Sugerencias Automaticas

El sistema genera sugerencias basadas en el tipo de error:

- **Division por cero**: Sugiere validar el divisor
- **Indice fuera de rango**: Sugiere verificar el tamano del array
- **Variable no definida**: Sugiere revisar la declaracion
- **Error de tipo**: Sugiere verificar tipos y conversiones

## Perfilamiento

### Reporte de Perfilamiento

Al finalizar la ejecucion con `--profile`, se muestra:

```
Reporte de Perfilamiento
Tiempo total de ejecucion: 0.0234 segundos

Llamadas a Funciones:
┌──────────┬──────────┬──────────────┬─────────────────┬───────────┐
│ Funcion  │ Llamadas │ Tiempo Total │ Tiempo Promedio │ Tiempo Max│
├──────────┼──────────┼──────────────┼─────────────────┼───────────┤
│ factorial│    5     │   0.0100s    │    0.0020s      │  0.0030s  │
│ main     │    1     │   0.0134s    │    0.0134s      │  0.0134s  │
└──────────┴──────────┴──────────────┴─────────────────┴───────────┘
```

### Metricas Disponibles

- **Tiempo total**: Tiempo total de ejecucion del programa
- **Llamadas**: Numero de veces que se llamo cada funcion
- **Tiempo total por funcion**: Tiempo acumulado en cada funcion
- **Tiempo promedio**: Tiempo promedio por llamada
- **Tiempo maximo**: Tiempo de la llamada mas lenta

## Ejemplos

### Ejemplo 1: Debugging de Division por Cero

```bminor
main: function integer () = {
    x: integer = 10;
    y: integer = 0;
    resultado: integer = x / y;  // Breakpoint aqui
    return 0;
}
```

Ejecutar:
```bash
python bminor.py --interp --debug ejemplo.bminor
```

### Ejemplo 2: Perfilamiento de Funcion Recursiva

```bminor
factorial: function integer (n: integer) = {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

main: function integer () = {
    resultado: integer = factorial(10);
    print resultado;
    return 0;
}
```

Ejecutar:
```bash
python bminor.py --interp --profile factorial.bminor
```

### Ejemplo 3: Validacion de Arrays

```bminor
main: function integer () = {
    arr: array [5] integer = {1, 2, 3, 4, 5};
    i: integer = 0;
    while (i < 10) {  // Error: i puede ser >= 5
        print arr[i];
        i = i + 1;
    }
    return 0;
}
```

El interprete detectara cuando `i >= 5` y mostrara un error descriptivo.

## Integracion con REPL

En el futuro, el REPL tambien soportara comandos de debugging:

```
>>> .break 10        # Agregar breakpoint en linea 10
>>> .step            # Modo paso a paso
>>> .vars            # Ver variables (ya disponible)
>>> .profile on      # Activar perfilamiento
```

## Notas

- El debugging y perfilamiento agregan overhead a la ejecucion
- Usa `--profile` solo cuando necesites analizar rendimiento
- Los breakpoints se pueden agregar programaticamente en el codigo
- Las validaciones en tiempo de ejecucion siempre estan activas

