@echo off
REM Script para compilar codigo B-Minor a ejecutable
REM Uso: compilar.bat archivo.bminor

if "%1"=="" (
    echo Uso: compilar.bat archivo.bminor
    echo Ejemplo: compilar.bat mi_programa.bminor
    echo Ejemplo: compilar.bat test\codegen\ejercicio.bminor
    exit /b 1
)

set ARCHIVO=%1

REM Convertir a ruta absoluta si es relativa
if not exist "%ARCHIVO%" (
    echo ERROR: No se encuentra el archivo "%ARCHIVO%"
    echo.
    echo Buscando en subdirectorios comunes...
    if exist "test\codegen\%ARCHIVO%" (
        set ARCHIVO=test\codegen\%ARCHIVO%
        echo Encontrado en: %ARCHIVO%
    ) else if exist "test\%ARCHIVO%" (
        set ARCHIVO=test\%ARCHIVO%
        echo Encontrado en: %ARCHIVO%
    ) else (
        echo No se encontro el archivo. Verifica la ruta.
        exit /b 1
    )
)

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo ========================================
echo Compilando %ARCHIVO%
echo ========================================
echo.

REM Eliminar output.ll anterior si existe (para evitar usar archivos viejos)
if exist output.ll (
    del output.ll >nul 2>&1
)

REM Paso 1: Generar codigo LLVM IR
echo [1/3] Generando codigo LLVM IR...
python bminor.py --codegen "%ARCHIVO%" > compilacion_temp.txt 2>&1
set COMPILACION_EXITOSA=%ERRORLEVEL%

REM Mostrar la salida
type compilacion_temp.txt

REM Verificar si hubo errores en la salida (buscar mensajes de error especificos)
findstr /C:"Error de sintaxis" /C:"Error de tipo" /C:"Error Lexico" /C:"Se encontraron" /C:"errores" /C:"ERROR:" compilacion_temp.txt | findstr /V /C:"completado sin errores" /C:"generado exitosamente" >nul
if %ERRORLEVEL% == 0 (
    echo.
    echo ERROR: Se encontraron errores durante la compilacion.
    del compilacion_temp.txt >nul 2>&1
    pause
    exit /b 1
)

REM Verificar codigo de salida
if %COMPILACION_EXITOSA% NEQ 0 (
    echo.
    echo ERROR: La compilacion fallo con codigo de error %COMPILACION_EXITOSA%
    del compilacion_temp.txt >nul 2>&1
    pause
    exit /b 1
)

REM Verificar que se genero output.ll
if not exist output.ll (
    echo.
    echo ERROR: No se genero el archivo output.ll
    echo La compilacion puede haber fallado silenciosamente.
    del compilacion_temp.txt >nul 2>&1
    pause
    exit /b 1
)

REM Limpiar archivo temporal
del compilacion_temp.txt >nul 2>&1

echo [OK] Codigo LLVM IR generado exitosamente
echo.

REM Paso 2: Compilar LLVM IR a ejecutable
echo [2/3] Compilando LLVM IR a ejecutable...
set NOMBRE_EJECUTABLE=%~n1.exe

REM Verificar si existe runtime.cpp o runtime.c
if exist runtime.cpp (
    clang output.ll runtime.cpp -o "%NOMBRE_EJECUTABLE%"
) else if exist runtime.c (
    clang output.ll runtime.c -o "%NOMBRE_EJECUTABLE%"
) else (
    echo ERROR: No se encontro runtime.cpp ni runtime.c
    pause
    exit /b 1
)

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo compilar el ejecutable.
    echo Asegurate de tener Clang instalado y en el PATH.
    pause
    exit /b 1
)

echo [OK] Ejecutable generado: %NOMBRE_EJECUTABLE%
echo.

REM Paso 3: Ejecutar (opcional)
echo [3/3] Ejecutando programa...
echo ========================================
echo.
"%NOMBRE_EJECUTABLE%"
echo.
echo ========================================
echo.
echo Compilacion completada exitosamente!
echo Ejecutable: %NOMBRE_EJECUTABLE%
echo.

