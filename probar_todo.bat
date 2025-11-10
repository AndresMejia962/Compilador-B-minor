@echo off
echo ========================================
echo PRUEBA COMPLETA DEL COMPILADOR B-MINOR
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Entorno virtual activado
    echo.
)

REM Verificar que el archivo de prueba existe
if not exist prueba_completa.bminor (
    echo [ERROR] No se encuentra prueba_completa.bminor
    pause
    exit /b 1
)

echo ========================================
echo FASE 1: ANALISIS LEXICO
echo ========================================
python bminor.py --scan prueba_completa.bminor
if errorlevel 1 (
    echo [ERROR] Falla en analisis lexico
    pause
    exit /b 1
)
echo [OK] Analisis lexico completado
echo.
pause

echo ========================================
echo FASE 2: ANALISIS SINTACTICO
echo ========================================
python bminor.py --parse prueba_completa.bminor
if errorlevel 1 (
    echo [ERROR] Falla en analisis sintactico
    pause
    exit /b 1
)
echo [OK] Analisis sintactico completado
echo.
pause

echo ========================================
echo FASE 3: ANALISIS SEMANTICO
echo ========================================
python bminor.py --check prueba_completa.bminor
if errorlevel 1 (
    echo [ERROR] Falla en analisis semantico
    pause
    exit /b 1
)
echo [OK] Analisis semantico completado
echo.
pause

echo ========================================
echo FASE 4: GENERACION DE CODIGO
echo ========================================
python bminor.py --codegen prueba_completa.bminor
if errorlevel 1 (
    echo [ERROR] Falla en generacion de codigo
    pause
    exit /b 1
)

if not exist output.ll (
    echo [ERROR] No se genero output.ll
    pause
    exit /b 1
)
echo [OK] Codigo LLVM IR generado
echo.
pause

echo ========================================
echo FASE 5: COMPILACION A EJECUTABLE
echo ========================================
clang output.ll runtime.c -o prueba_completa.exe
if errorlevel 1 (
    echo [ERROR] No se pudo compilar el ejecutable
    echo Asegurate de tener Clang instalado
    pause
    exit /b 1
)
echo [OK] Ejecutable compilado
echo.
pause

echo ========================================
echo FASE 6: EJECUCION DEL PROGRAMA
echo ========================================
echo.
prueba_completa.exe
echo.
echo ========================================
echo [OK] TODAS LAS PRUEBAS COMPLETADAS
echo ========================================
echo.
pause

