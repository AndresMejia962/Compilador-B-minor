# builtins.py
'''
Funciones y constantes built-in para el intérprete BMinor
'''
import math

class CallError(Exception):
    """Excepcion lanzada cuando hay un error al llamar una funcion built-in"""
    pass

# Constantes built-in
consts = {
    # Puedes agregar constantes aqui si es necesario
}

# Funciones built-in
def read_integer(*args):
    """Lee un numero entero del usuario"""
    if len(args) > 0:
        raise CallError("read_integer() no acepta argumentos")
    try:
        value = input()
        return int(value)
    except ValueError:
        raise CallError(f"Error: '{value}' no es un numero entero valido")

def read_string(*args):
    """Lee una cadena de texto del usuario"""
    if len(args) > 0:
        raise CallError("read_string() no acepta argumentos")
    return input()

def sqrt(*args):
    """Calcula la raiz cuadrada de un numero"""
    if len(args) != 1:
        raise CallError(f"sqrt() requiere 1 argumento, se recibieron {len(args)}")
    value = args[0]
    if not isinstance(value, (int, float)):
        raise CallError(f"sqrt() requiere un numero, se recibio {type(value).__name__}")
    if value < 0:
        raise CallError("sqrt() no puede calcular la raiz de un numero negativo")
    return math.sqrt(float(value))

def abs_func(*args):
    """Calcula el valor absoluto de un numero"""
    if len(args) != 1:
        raise CallError(f"abs() requiere 1 argumento, se recibieron {len(args)}")
    value = args[0]
    if not isinstance(value, (int, float)):
        raise CallError(f"abs() requiere un numero, se recibio {type(value).__name__}")
    return abs(value)

def max_func(*args):
    """Encuentra el maximo entre dos o mas numeros"""
    if len(args) < 1:
        raise CallError("max() requiere al menos 1 argumento")
    for arg in args:
        if not isinstance(arg, (int, float)):
            raise CallError(f"max() requiere numeros, se recibio {type(arg).__name__}")
    return max(args)

def min_func(*args):
    """Encuentra el minimo entre dos o mas numeros"""
    if len(args) < 1:
        raise CallError("min() requiere al menos 1 argumento")
    for arg in args:
        if not isinstance(arg, (int, float)):
            raise CallError(f"min() requiere numeros, se recibio {type(arg).__name__}")
    return min(args)

def length(*args):
    """Calcula la longitud de un array o string"""
    if len(args) != 1:
        raise CallError(f"length() requiere 1 argumento, se recibieron {len(args)}")
    value = args[0]
    if isinstance(value, list):
        return len(value)
    elif isinstance(value, str):
        return len(value)
    else:
        raise CallError(f"length() requiere un array o string, se recibio {type(value).__name__}")

# Funciones built-in
builtins = {
    'read_integer': read_integer,
    'read_string': read_string,
    'sqrt': sqrt,
    'abs': abs_func,  # Usar abs_func para evitar conflicto con abs() de Python
    'max': max_func,  # Usar max_func para evitar conflicto con max() de Python
    'min': min_func,  # Usar min_func para evitar conflicto con min() de Python
    'length': length,
}

