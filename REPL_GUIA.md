# Guia del Modo Interactivo (REPL)

El REPL (Read-Eval-Print Loop) te permite ejecutar codigo B-Minor linea por linea de forma interactiva.

## Iniciar el REPL

```bash
python bminor.py --repl
```

## Comandos Especiales

- `.exit`, `.quit`, `.q` - Salir del REPL
- `.vars` - Mostrar todas las variables definidas
- `.clear` - Limpiar todas las variables (excepto builtins)
- `.help` - Mostrar ayuda

## Ejemplos de Uso

### Declarar Variables

```
>>> x: integer = 10;
>>> y: integer = 20;
>>> resultado: integer = x + y;
```

### Imprimir Valores

```
>>> print resultado;
40
```

### Expresiones

```
>>> x + y;
=> 30
>>> x * 2;
=> 20
```

### Estructuras de Control

```
>>> if (x < y) {
...     print "x es menor";
... } else {
...     print "y es menor";
... }
```

### Funciones

```
>>> suma: function integer (a: integer, b: integer) = {
...     return a + b;
... }
>>> resultado: integer = suma(5, 3);
>>> print resultado;
8
```

### Ver Variables

```
>>> .vars
```

### Arrays

```
>>> numeros: array [5] integer = {1, 2, 3, 4, 5};
>>> print numeros[2];
3
```

## Caracteristicas

- **Estado Persistente**: Las variables se mantienen entre lineas
- **Multi-linea**: Puedes escribir bloques de codigo en varias lineas
- **Validacion**: El codigo se valida sintactica y semanticamente antes de ejecutar
- **Manejo de Errores**: Los errores no detienen el REPL, puedes continuar

## Notas

- Todas las lineas deben terminar con `;` (excepto bloques)
- El REPL mantiene el estado del interprete entre ejecuciones
- Puedes usar Ctrl+C para interrumpir, pero usa `.exit` para salir correctamente

