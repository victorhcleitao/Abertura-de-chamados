@echo off
title ServiceFlow - Abertura de Chamados Qualitor
cd /d "%~dp0"
echo ======================================================
echo    ServiceFlow - Abertura e Encerramento em Serie
echo ======================================================
python qualitor_gui.py
if errorlevel 1 (
    echo.
    echo Ocorreu um erro durante a execucao. Verifique as dependencias com:
    echo pip install -r requirements.txt
    pause
)
