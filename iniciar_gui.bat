@echo off
REM Script para iniciar la interfaz grafica del compilador B-Minor

echo ========================================
echo Iniciando Interfaz Grafica B-Minor
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Entorno virtual activado
    echo.
)

REM Verificar que las dependencias esten instaladas
echo [1/3] Verificando dependencias de Python...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Instalando Flask...
    pip install flask flask-cors
)

echo.
echo [2/3] Verificando dependencias de Node.js...
cd gui-frontend
if not exist node_modules (
    echo Instalando dependencias de React...
    call npm install
)
cd ..

echo.
echo [3/3] Iniciando servidores...
echo.
echo ========================================
echo Servidor Flask: http://localhost:5000
echo Frontend React: http://localhost:3000
echo ========================================
echo.
echo Presiona Ctrl+C para detener ambos servidores
echo.

REM Iniciar Flask en segundo plano y React en primer plano
start "Flask Server" cmd /k "python gui_server.py"
timeout /t 2 /nobreak >nul
cd gui-frontend
call npm run dev

