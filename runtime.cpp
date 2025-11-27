#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <limits.h>

// Funciones auxiliares del sistema para impresión
extern "C" {
    // Funciones de impresión mejoradas con flush automático
    void print_integer(long long valor_entero) {
        printf("%lld", valor_entero);
        fflush(stdout);  // Asegurar que se muestre inmediatamente
    }

    void print_float(double valor_flotante) {
        // Usar formato más preciso: %g para notación científica automática
        // o %f para decimales fijos cuando sea apropiado
        if (valor_flotante == (long long)valor_flotante) {
            // Si es un número entero, mostrarlo sin decimales
            printf("%.0f", valor_flotante);
        } else {
            printf("%g", valor_flotante);
        }
        fflush(stdout);
    }

    void print_boolean(bool valor_booleano) {
        printf("%s", valor_booleano ? "true" : "false");
        fflush(stdout);
    }

    void print_char(char caracter) {
        printf("%c", caracter);
        fflush(stdout);
    }

    void print_string(const char* cadena_texto) {
        // Validación de puntero nulo para evitar crashes
        if (cadena_texto == NULL) {
            printf("(null)");
        } else {
            printf("%s", cadena_texto);
        }
        fflush(stdout);
    }

    // Funciones de entrada para leer datos del usuario
    long long read_integer() {
        long long valor;
        if (scanf("%lld", &valor) != 1) {
            // Si falla la lectura, retornar 0 y limpiar el buffer
            while (getchar() != '\n');  // Limpiar buffer de entrada
            return 0;
        }
        return valor;
    }

    double read_float() {
        double valor;
        if (scanf("%lf", &valor) != 1) {
            // Si falla la lectura, retornar 0.0 y limpiar el buffer
            while (getchar() != '\n');  // Limpiar buffer de entrada
            return 0.0;
        }
        return valor;
    }

    // Leer string (requiere buffer pre-asignado)
    // Nota: En B-Minor, esto se manejaría diferente, pero para runtime básico:
    void read_string(char* buffer, int max_size) {
        if (buffer == NULL || max_size <= 0) {
            return;
        }
        // Leer hasta encontrar nueva línea o alcanzar el límite
        if (fgets(buffer, max_size, stdin) != NULL) {
            // Eliminar el salto de línea final si existe
            size_t len = strlen(buffer);
            if (len > 0 && buffer[len - 1] == '\n') {
                buffer[len - 1] = '\0';
            }
        } else {
            buffer[0] = '\0';  // String vacío si falla
        }
    }

    // Funciones matemáticas
    double sqrt_func(double valor) {
        if (valor < 0.0) {
            // Retornar NaN para valores negativos
            return NAN;
        }
        return sqrt(valor);
    }

    double abs_func(double valor) {
        return fabs(valor);
    }

    double max_func(double a, double b) {
        return (a > b) ? a : b;
    }

    double min_func(double a, double b) {
        return (a < b) ? a : b;
    }

    // Función para obtener la longitud de un string
    int string_length(const char* cadena) {
        if (cadena == NULL) {
            return 0;
        }
        return (int)strlen(cadena);
    }

    // ==================================================
    // ARRAYS DINÁMICOS CON TAMAÑO ALMACENADO
    // ==================================================
    // Técnica: Almacenamos el tamaño en la posición -1 del puntero
    // Esto permite saber el tamaño del array en tiempo de ejecución

    // Crear array dinámico de enteros
    long long* array_new_integer(int n) {
        if (n < 0) n = 0;
        // Reservamos (n + 1) enteros: uno para el tamaño, n para los elementos
        long long* raw = (long long*)malloc(sizeof(long long) * (n + 1));
        if (!raw) {
            fprintf(stderr, "Error: malloc failed in array_new_integer\n");
            exit(1);
        }
        raw[0] = n;          // Guardamos el tamaño en la posición 0
        long long* arr = raw + 1;  // Devolvemos puntero al primer elemento
        
        // Inicializar en cero
        for (int i = 0; i < n; i++) {
            arr[i] = 0;
        }
        return arr;
    }

    // Obtener el tamaño de un array de enteros
    long long array_length_integer(long long* arr) {
        if (!arr) {
            return 0;
        }
        long long* raw = arr - 1;
        return raw[0];
    }

    // Crear array dinámico de flotantes
    double* array_new_float(int n) {
        if (n < 0) n = 0;
        // Reservamos (n + 1) flotantes: uno para el tamaño, n para los elementos
        double* raw = (double*)malloc(sizeof(double) * (n + 1));
        if (!raw) {
            fprintf(stderr, "Error: malloc failed in array_new_float\n");
            exit(1);
        }
        raw[0] = (double)n;   // Guardamos tamaño como double
        double* arr = raw + 1;  // Devolvemos puntero al primer elemento
        
        // Inicializar en cero
        for (int i = 0; i < n; i++) {
            arr[i] = 0.0;
        }
        return arr;
    }

    // Obtener el tamaño de un array de flotantes
    long long array_length_float(double* arr) {
        if (!arr) {
            return 0;
        }
        double* raw = arr - 1;
        return (long long)(raw[0]);
    }

    // Crear array dinámico de booleanos
    bool* array_new_boolean(int n) {
        if (n < 0) n = 0;
        // Para booleanos, almacenamos el tamaño como int en la primera posición
        // Necesitamos un buffer más grande para almacenar el tamaño
        int* raw = (int*)malloc(sizeof(int) + sizeof(bool) * n);
        if (!raw) {
            fprintf(stderr, "Error: malloc failed in array_new_boolean\n");
            exit(1);
        }
        raw[0] = n;  // Guardamos el tamaño
        bool* arr = (bool*)(raw + 1);  // Devolvemos puntero al primer elemento
        
        // Inicializar en false
        for (int i = 0; i < n; i++) {
            arr[i] = false;
        }
        return arr;
    }

    // Obtener el tamaño de un array de booleanos
    long long array_length_boolean(bool* arr) {
        if (!arr) {
            return 0;
        }
        int* raw = (int*)arr - 1;
        return (long long)(raw[0]);
    }
}
