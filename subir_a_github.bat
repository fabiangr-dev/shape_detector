@echo off
echo.
echo ========================================================
echo   Subir Proyecto a GitHub - Geometric Shape Detector
echo ========================================================
echo.
echo Este script te ayudara a subir el proyecto a GitHub.
echo.
echo IMPORTANTE: Antes de ejecutar este script:
echo   1. Crea el repositorio en GitHub: https://github.com/new
echo   2. Nombre sugerido: geometric-shape-detector
echo   3. NO añadas README, .gitignore o LICENSE
echo.
pause
echo.

REM Pedir el nombre de usuario de GitHub
set /p USUARIO="Ingresa tu usuario de GitHub: "
echo.

REM Verificar si ya existe un remote
git remote -v > nul 2>&1
if %errorlevel% == 0 (
    echo Remote detectado. Removiendo remote existente...
    git remote remove origin
)

REM Añadir el remote
echo Añadiendo remote de GitHub...
git remote add origin https://github.com/%USUARIO%/geometric-shape-detector.git

REM Renombrar rama a main
echo Renombrando rama a 'main'...
git branch -M main

REM Subir a GitHub
echo.
echo Subiendo archivos a GitHub...
echo Se te pedira tu usuario y token de acceso personal.
echo.
git push -u origin main

if %errorlevel% == 0 (
    echo.
    echo ========================================================
    echo   ¡Exito! Proyecto subido a GitHub
    echo ========================================================
    echo.
    echo Tu repositorio esta disponible en:
    echo https://github.com/%USUARIO%/geometric-shape-detector
    echo.
) else (
    echo.
    echo ========================================================
    echo   Error al subir el proyecto
    echo ========================================================
    echo.
    echo Verifica:
    echo   1. Que creaste el repositorio en GitHub
    echo   2. Que tu usuario de GitHub es correcto
    echo   3. Que usaste tu Personal Access Token como contraseña
    echo.
    echo Para crear un token: https://github.com/settings/tokens
    echo.
)

pause
