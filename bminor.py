import sys
import argparse
import pandas as pd
from tabulate import tabulate
from bminor_lexer import Lexer

def scan_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{filepath}' no fue encontrado.")
        sys.exit(1)

    lexer = Lexer()
    tokens_list = []
    errors_list = []

    def lexer_error(t):
        error_message = f"Error Léxico: Carácter ilegal '{t.value[0]}' en la línea {t.lineno}"
        errors_list.append(error_message)
        lexer.index += 1

    lexer.error = lexer_error

    for tok in lexer.tokenize(code):
        if tok.type == 'ERROR':
            errors_list.append(tok.value)
        else:
            tokens_list.append(tok)

    if errors_list:
        for error in errors_list:
            print(error)
    
    if not tokens_list:
        print("Análisis léxico completado: no se encontraron tokens.")
        return

    line_starts = [0] + [i + 1 for i, char in enumerate(code) if char == '\n']
        
    table_data = []
    for tok in tokens_list:
        line_start_index = line_starts[tok.lineno - 1]
        columna = tok.index - line_start_index + 1
        table_data.append([tok.type, repr(tok.value), tok.lineno, columna])
            
    df = pd.DataFrame(table_data, columns=["TIPO", "VALOR", "LINEA", "COLUMNA"])
    df.index = range(1, len(df) + 1)
    print(tabulate(df, headers='keys', tablefmt='fancy_grid', stralign='left', showindex="TOKEN #"))

def main():
    parser = argparse.ArgumentParser(description="Compilador para el lenguaje B-Minor 2025.")
    parser.add_argument('--scan', action='store_true', help='Realiza el análisis léxico del archivo.')
    parser.add_argument('filepath', type=str, help='El archivo .bminor a procesar.')
    args = parser.parse_args()

    if args.scan:
        scan_file(args.filepath)
    else:
        print("Acción no especificada. Debes usar la bandera --scan.")
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()