# Guia de Configuracion de la Interfaz Grafica

Esta es una interfaz grafica educativa para el compilador B-Minor, construida con React y Flask.

## Requisitos Previos

- Python 3.8+ (ya instalado)
- Node.js 18+ y npm (para el frontend React)

## Instalacion

### 1. Instalar dependencias de Python

```bash
pip install flask flask-cors
```

O si usas el entorno virtual:

```bash
venv\Scripts\activate
pip install flask flask-cors
```

### 2. Instalar dependencias del Frontend

```bash
cd gui-frontend
npm install
cd ..
```

## Uso

### Modo Desarrollo (Recomendado para demostracion)

**Terminal 1 - Servidor Flask:**
```bash
python gui_server.py
```

**Terminal 2 - Frontend React:**
```bash
cd gui-frontend
npm run dev
```

Luego abre tu navegador en: **http://localhost:3000**

### Modo Produccion (Para mostrar al profesor)

1. **Construir el frontend:**
```bash
cd gui-frontend
npm run build
cd ..
```

2. **Ejecutar solo el servidor Flask:**
```bash
python gui_server.py
```

3. **Abrir en el navegador:**
   - http://localhost:5000

## Caracteristicas

- ✅ Seleccion de archivos .bminor
- ✅ Botones para todas las fases (Scan, Parse, Check, Codegen, Interp)
- ✅ Modo REPL interactivo
- ✅ Opciones de Debug y Profile
- ✅ Visualizacion del codigo fuente
- ✅ Panel de salida con resultados
- ✅ Interfaz moderna y responsive

## Estructura

```
Compilador/
├── gui_server.py          # Servidor Flask (backend)
├── gui-frontend/          # Aplicacion React (frontend)
│   ├── src/
│   │   ├── App.jsx        # Componente principal
│   │   ├── App.css        # Estilos
│   │   └── main.jsx       # Punto de entrada
│   ├── package.json
│   └── vite.config.js
└── ... (resto del compilador)
```

## Notas

- Esta interfaz es solo para uso educativo/demostracion
- No requiere despliegue, funciona completamente local
- El servidor Flask ejecuta los comandos de bminor.py por detras
- Todos los archivos .bminor se cargan automaticamente

## Solucion de Problemas

**Error: "flask no encontrado"**
```bash
pip install flask flask-cors
```

**Error: "npm no encontrado"**
- Instala Node.js desde: https://nodejs.org/

**El frontend no se conecta al backend**
- Asegurate de que el servidor Flask este corriendo en el puerto 5000
- Verifica que no haya errores en la consola del navegador (F12)

**No aparecen archivos .bminor**
- Verifica que haya archivos .bminor en el directorio o en test/codegen/
- Revisa la consola del navegador para errores

