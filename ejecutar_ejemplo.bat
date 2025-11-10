@echo off
echo ========================================
echo Ejecutando Ejemplo del Compilador
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Ejecutar el compilador con un archivo de prueba
if exist test\codegen\test.bminor (
    echo Compilando test\codegen\test.bminor...
    python bminor.py --codegen test\codegen\test.bminor
    echo.
    if exist output.ll (
        echo Compilando LLVM IR a ejecutable...
        clang output.ll runtime.c -o test_program.exe
        if exist test_program.exe (
            echo.
            echo Ejecutando programa...
            echo ========================================
            test_program.exe
            echo ========================================
        ) else (
            echo ERROR: No se pudo compilar el ejecutable
            echo Asegurate de tener Clang instalado
        )
    ) else (
        echo ERROR: No se genero el archivo output.ll
    )
) else (
    echo ERROR: No se encontro el archivo test\codegen\test.bminor
)

echo.
pause

