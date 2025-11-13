@echo off
REM Se omite la activación de entorno virtual; se usará la instalación global de Python.

if not exist test\codegen\test.bminor (
    echo [ERROR] No se encontro el archivo test\codegen\test.bminor
    pause
    exit /b 1
)

python bminor.py --codegen test\codegen\test.bminor >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Fallo la generacion de codigo LLVM
    pause
    exit /b 1
)

if not exist output.ll (
    echo [ERROR] No se genero el archivo output.ll
    pause
    exit /b 1
)

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
"%COMPILER_EXE%" output.ll runtime.c -o test_program.exe >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Fallo el enlace del ejecutable
    pause
    exit /b 1
)

if not exist test_program.exe (
    echo [ERROR] No se genero el ejecutable
    pause
    exit /b 1
)

test_program.exe >nul 2>&1
if errorlevel 1 (
    echo [ERROR] El programa fallo al ejecutarse
    pause
    exit /b 1
)

echo [OK] Ejemplo ejecutado correctamente
