@echo off
echo ========================================
echo Ejecutando Prueba Completa del Compilador
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Entorno virtual activado.
    echo.
)

REM Ejecutar el compilador
echo [1/3] Compilando prueba_completa.bminor...
python bminor.py --codegen prueba_completa.bminor

if errorlevel 1 (
    echo.
    echo ERROR: La compilacion fallo. Revisa los errores arriba.
    pause
    exit /b 1
)

if not exist output.ll (
    echo.
    echo ERROR: No se genero el archivo output.ll
    pause
    exit /b 1
)

echo.
echo [2/3] Compilando LLVM IR a ejecutable...
clang output.ll runtime.c -o prueba_completa.exe

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo compilar el ejecutable.
    echo Asegurate de tener Clang instalado y en el PATH.
    pause
    exit /b 1
)

echo.
echo [3/3] Ejecutando programa...
echo ========================================
echo.
prueba_completa.exe
echo.
echo ========================================
echo.
echo Prueba completada exitosamente!
echo.
pause

