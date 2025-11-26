@echo off
echo ========================================
echo Configuracion del Compilador B-Minor
echo ========================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor, instala Python 3.8 o superior
    pause
    exit /b 1
)

echo [1/3] Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo [2/3] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [3/3] Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo ========================================
echo Configuracion completada exitosamente!
echo ========================================
echo.
echo Para usar el compilador:
echo   1. Activa el entorno virtual: venv\Scripts\activate.bat
echo   2. Ejecuta: python bminor.py --codegen archivo.bminor
echo.
pause

