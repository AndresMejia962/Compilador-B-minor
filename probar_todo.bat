@echo off
REM Se omite la activación de entorno virtual para operar con Python global.

if not exist prueba_completa.bminor (
    echo [ERROR] No se encuentra prueba_completa.bminor
    pause
    exit /b 1
)

python bminor.py --scan prueba_completa.bminor >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Falla en analisis lexico
    pause
    exit /b 1
)
echo [OK] Analisis lexico

python bminor.py --parse prueba_completa.bminor >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Falla en analisis sintactico
    pause
    exit /b 1
)
echo [OK] Analisis sintactico

python bminor.py --check prueba_completa.bminor >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Falla en analisis semantico
    pause
    exit /b 1
)
echo [OK] Analisis semantico

python bminor.py --codegen prueba_completa.bminor >nul 2>&1
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
echo [OK] Generacion de codigo LLVM

set "COMPILER_EXE="
set "MSYS_BIN="
REM Buscar clang en MSYS2 primero
for %%p in ("C:\msys64\clang64\bin" "C:\msys64\clangarm64\bin") do (
    if exist "%%~p\clang.exe" (
        set "COMPILER_EXE=%%~p\clang.exe"
        set "MSYS_BIN=%%~p"
        goto :found_compiler
    )
)
REM Buscar clang en LLVM instalado
where clang >nul 2>&1
if not errorlevel 1 (
    set "COMPILER_EXE=clang"
    goto :found_compiler
)
for %%p in ("C:\Program Files\LLVM\bin" "C:\Program Files (x86)\LLVM\bin") do (
    if exist "%%~p\clang.exe" (
        set "COMPILER_EXE=%%~p\clang.exe"
        goto :found_compiler
    )
)
REM Si no hay clang, buscar gcc en MSYS2
for %%p in ("C:\msys64\ucrt64\bin" "C:\msys64\mingw64\bin" "C:\msys64\mingw32\bin") do (
    if exist "%%~p\gcc.exe" (
        set "COMPILER_EXE=%%~p\gcc.exe"
        set "MSYS_BIN=%%~p"
        goto :found_compiler
    )
)
:found_compiler
if not defined COMPILER_EXE (
    echo [ERROR] No se encontro clang ni gcc
    pause
    exit /b 1
)

if defined MSYS_BIN (
    set "PATH=%MSYS_BIN%;%PATH%"
)
REM Mostrar que compilador se esta usando (temporal para debug)
echo | findstr /C:"clang64" >nul 2>&1
if "%COMPILER_EXE%"=="C:\msys64\clang64\bin\clang.exe" (
    echo [INFO] Usando clang de MSYS2
) else if "%COMPILER_EXE%"=="clang" (
    echo [INFO] Usando clang del PATH
) else (
    echo [INFO] Usando gcc como alternativa
)
"%COMPILER_EXE%" output.ll runtime.c -o prueba_completa.exe >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Fallo la compilacion y enlace del ejecutable
    pause
    exit /b 1
)
echo [OK] Compilacion y enlace

prueba_completa.exe >nul 2>&1
if errorlevel 1 (
    echo [ERROR] El programa fallo al ejecutarse
    pause
    exit /b 1
)
echo [OK] Ejecucion del programa
echo [OK] TODAS LAS PRUEBAS COMPLETADAS
