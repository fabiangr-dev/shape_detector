@echo off
echo.
echo ====================================
echo   Detector de Figuras Geometricas
echo ====================================
echo.
cd /d %~dp0
python geometric_shape_detector.py
if errorlevel 1 (
    echo.
    echo Error al ejecutar la aplicacion.
    echo Verifica que Python y las dependencias esten instaladas.
    pause
)
