import sys
import argparse
import pandas as pd
from tabulate import tabulate
from rich import print
from bminor_lexer import Lexer
from parser import analizar_sintaxis
from errors import errors_detected, clear_errors
from checker import AnalizadorSemantico

def analizar_lexico(archivo_ruta):
    """Realiza el análisis léxico de un archivo y muestra los tokens."""
    try:
        with open(archivo_ruta, 'r', encoding='utf-8') as archivo:
            codigo_fuente = archivo.read()
    except FileNotFoundError:
        print(f"\n{'='*60}")
        print("ERROR: Archivo no encontrado")
        print(f"Archivo buscado: {archivo_ruta}")
        print("Verifica que la ruta del archivo sea correcta")
        print(f"{'='*60}")
        sys.exit(1)

    analizador_lexico = Lexer()
    lista_tokens = []
    lista_errores = []

    # Captura de errores léxicos
    def capturar_error_lexico(token):
        mensaje_error = f"Error Léxico: Carácter ilegal '{token.value[0]}' en la línea {token.lineno}"
        lista_errores.append(mensaje_error)
        analizador_lexico.index += 1
    analizador_lexico.error = capturar_error_lexico

    # Tokenización
    for token in analizador_lexico.tokenize(codigo_fuente):
        if token.type == 'ERROR':
            lista_errores.append(token.value)
        else:
            lista_tokens.append(token)

    if lista_errores:
        print(f"\n{'='*60}")
        print("ERRORES LEXICOS DETECTADOS")
        print(f"{'='*60}")
        for i, error_msg in enumerate(lista_errores, 1):
            print(f"   {i:2d}. [ERROR] {error_msg}")
        print(f"{'='*60}\n")
    
    if not lista_tokens and not lista_errores:
        print("\nANALISIS LEXICO COMPLETADO")
        print("   [AVISO] No se encontraron tokens en el archivo.")
        return

    if lista_tokens:
        print(f"\n{'='*80}")
        print("RESULTADO DEL ANALISIS LEXICO")
        print(f"{'='*80}")
        print(f"Total de tokens encontrados: {len(lista_tokens)}")
        print(f"{'='*80}")
        
        inicio_lineas = [0] + [i + 1 for i, caracter in enumerate(codigo_fuente) if caracter == '\n']
        
        for i, token in enumerate(lista_tokens, 1):
            indice_inicio_linea = inicio_lineas[token.lineno - 1]
            columna = token.index - indice_inicio_linea + 1
            
            print(f"   {i:3d}. * {token.type:<20} | {repr(token.value):<15} | Linea {token.lineno:2d}, Col {columna:2d}")
        
        print(f"{'='*80}\n")

def analizar_sintactico(archivo_ruta):
    """Realiza el análisis sintáctico de un archivo y muestra el AST."""
    try:
        with open(archivo_ruta, 'r', encoding='utf-8') as archivo:
            codigo_fuente = archivo.read()
    except FileNotFoundError:
        print(f"\n{'='*60}")
        print("ERROR: Archivo no encontrado")
        print(f"Archivo buscado: {archivo_ruta}")
        print("Verifica que la ruta del archivo sea correcta")
        print(f"{'='*60}")
        sys.exit(1)

    clear_errors()
    
    arbol_sintaxis = analizar_sintaxis(codigo_fuente)
    
    if not errors_detected():
        print(f"\n{'='*60}")
        print("ANALISIS SINTACTICO COMPLETADO EXITOSAMENTE")
        print(f"{'='*60}")
        if arbol_sintaxis:
            print("ARBOL DE SINTAXIS ABSTRACTA (AST)")
            print(f"{'='*60}")
            visualizacion_arbol = arbol_sintaxis.pretty()
            print(visualizacion_arbol)
            print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print(f"ANALISIS SINTACTICO FALLIDO")
        print(f"Total de errores encontrados: {errors_detected()}")
        print(f"{'='*60}\n")

def analizar_semantico(archivo_ruta):
    """Realiza el análisis sintáctico y semántico de un archivo."""
    try:
        with open(archivo_ruta, 'r', encoding='utf-8') as archivo:
            codigo_fuente = archivo.read()
    except FileNotFoundError:
        print(f"\n{'='*60}")
        print("ERROR: Archivo no encontrado")
        print(f"Archivo buscado: {archivo_ruta}")
        print("Verifica que la ruta del archivo sea correcta")
        print(f"{'='*60}")
        sys.exit(1)

    clear_errors()
    
    arbol_sintaxis = analizar_sintaxis(codigo_fuente)
    
    # Detenerse si hay errores de sintaxis antes de continuar
    if errors_detected():
        print(f"\n{'='*70}")
        print("ERRORES DE SINTAXIS DETECTADOS")
        print(f"Total de errores: {errors_detected()}")
        print("[AVISO] No se puede continuar con el analisis semantico.")
        print(f"{'='*70}\n")
        return
        
    print(f"\n{'='*60}")
    print("INICIANDO ANALISIS SEMANTICO")
    print("Análisis sintáctico completado correctamente")
    print(f"{'='*60}")
    
    # Iniciar el análisis semántico
    entorno_global = AnalizadorSemantico.ejecutar_analisis(arbol_sintaxis)
    
    if not errors_detected():
        print(f"\n{'='*60}")
        print("ANALISIS SEMANTICO COMPLETADO EXITOSAMENTE")
        print(f"{'='*60}")
        print("REGISTRO DE SIMBOLOS GENERADO:")
        entorno_global.imprimir()
    else:
        print(f"\n{'='*60}")
        print(f"ANALISIS SEMANTICO FALLIDO")
        print(f"Total de errores encontrados: {errors_detected()}")
        print(f"{'='*60}\n")

def main():
    print(f"\n{'='*70}")
    print("COMPILADOR B-MINOR 2025 - SISTEMA DE ANALISIS")
    print("Analisis Lexico, Sintactico y Semantico")
    print(f"{'='*70}")
    
    analizador_argumentos = argparse.ArgumentParser(description="Compilador para el lenguaje B-Minor 2025.")  
    analizador_argumentos.add_argument('--scan', action='store_true', help='Realiza el análisis léxico del archivo.')
    analizador_argumentos.add_argument('--parse', action='store_true', help='Realiza el análisis sintáctico del archivo.')
    analizador_argumentos.add_argument('--check', action='store_true', help='Realiza el análisis sintáctico y semántico del archivo.')
    analizador_argumentos.add_argument('filepath', type=str, help='El archivo .bminor a procesar.')
    argumentos = analizador_argumentos.parse_args()

    if argumentos.scan:
        analizar_lexico(argumentos.filepath)
    elif argumentos.parse:
        analizar_sintactico(argumentos.filepath)
    elif argumentos.check:
        analizar_semantico(argumentos.filepath)
    else:
        print(f"\n{'='*60}")
        print("ERROR: No se especifico ninguna accion")
        print("Debes usar una de las siguientes opciones:")
        print("   --scan   : Analisis lexico")
        print("   --parse  : Analisis sintactico") 
        print("   --check  : Analisis completo (lexico + sintactico + semantico)")
        print(f"{'='*60}")
        analizador_argumentos.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main() 