@echo off
chcp 65001 > nul
cls

set "LINE==========================================================="

echo.
echo %LINE%
echo    INSTALACION AUTOMATICA DEL PROYECTO ML
echo %LINE%
echo.

:: --- PASO 1: VERIFICACION STRICTA DE PYTHON 3.13 ---
echo [PASO 1] Buscando Python 3.13...
echo %LINE%

:: 1. Intento con Python Launcher (Lo ideal en Windows)
py -3.13 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py -3.13"
    echo  [OK] Se encontro Python 3.13 (Launcher).
) else (
    :: 2. Intento con comando python directo (Solo si es ver 3.13 exacto)
    python -c "import sys; exit(0) if sys.version_info[:2] == (3, 13) else exit(1)" >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=python"
        echo  [OK] El comando 'python' del sistema es version 3.13.
    ) else (
        :: 3. Si falla todo, ABORTAR.
        echo.
        echo  [ERROR CRITICO] No se encontro Python 3.13.
        echo  -------------------------------------------------------
        echo  Este proyecto REQUIERE Python 3.13 estricto.
        echo  Tu version actual no coincide o no esta instalada.
        echo  Por favor instala Python 3.13 desde python.org
        echo  -------------------------------------------------------
        echo.
        pause
        exit /b 1
    )
)
echo.

:: --- PASO 2: CREAR VENV ---
echo [PASO 2] Creando Entorno Virtual...
echo %LINE%
%PYTHON_CMD% -m venv venv
if %errorlevel% neq 0 (
    echo  [ERROR] Fallo al crear la carpeta venv.
    pause
    exit /b 1
)
echo  [OK] Carpeta 'venv' creada exitosamente.
echo.

:: --- PASO 3: INSTALAR DEPENDENCIAS ---
echo [PASO 3] Instalando librerias (esto puede tardar)...
echo %LINE%
cmd /c ".\venv\Scripts\activate && pip install -r requirements.txt"
if %errorlevel% neq 0 (
    echo  [ERROR] Fallo en la instalacion de librerias.
    pause
    exit /b 1
)
echo.

:: --- PASO 4: PLAYWRIGHT ---
echo [PASO 4] Instalando binarios de Playwright...
echo %LINE%
cmd /c ".\venv\Scripts\activate && playwright install"
echo.

:: --- FINALIZAR ---
echo.
echo %LINE%
echo %LINE%
echo    INSTALACION COMPLETADA CON EXITO
echo %LINE%
echo %LINE%
echo.
echo  Para comenzar a trabajar, escribe:
echo.
echo      .\venv\Scripts\activate
echo.
pause