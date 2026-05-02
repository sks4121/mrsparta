@echo off
REM Script para crear datos de prueba en MR SPARTA
REM Ejecutar: crear_datos.bat

echo.
echo ========================================
echo  MR SPARTA - Crear Datos de Prueba
echo ========================================
echo.

REM Verificar que estamos en la carpeta correcta
if not exist "manage.py" (
    echo Error: manage.py no encontrado
    echo Por favor ejecutar desde la carpeta del proyecto
    pause
    exit /b 1
)

REM Ejecutar el script Py
echo Ejecutando script...
echo.

py crearCoas_FINAL.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo OK - Datos creados exitosamente
    echo ========================================
    echo.
    echo Ahora ejecutar: py manage.py runserver
    echo Luego ir a: http://127.0.0.1:8000/coaches/1/
    echo.
) else (
    echo.
    echo ERROR - Algo salió mal
    echo.
)

pause
