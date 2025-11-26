#include <stdio.h>
#include <stdbool.h>

// Funciones auxiliares del sistema para impresión
extern "C" {
    void print_integer(long long valor_entero) {
        printf("%lld", valor_entero);
    }

    void print_float(double valor_flotante) {
        printf("%g", valor_flotante);
    }

    void print_boolean(bool valor_booleano) {
        printf("%s", valor_booleano ? "true" : "false");
    }

    void print_char(char caracter) {
        printf("%c", caracter);
    }

    void print_string(const char* cadena_texto) {
        printf("%s", cadena_texto);
    }
}
