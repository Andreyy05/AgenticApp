@echo off
chcp 65001 > nul
title Travel-Planner Agent
cd /d "%~dp0"

:menu
cls
echo =====================================================================
echo           AGENTIC TRAVEL-PLANNER APPLICATION
echo =====================================================================
echo.
echo  [1] Spustit ukazkove behy (Run 1 Pariz + Run 2 Tokio)
echo  [2] Interaktivni rezim (naplanovat si vlastni vylet zadanim udaju)
echo  [3] Spustit automaticke Unit Testy
echo  [4] Otevrit slozku s vysledky (traces)
echo  [5] Konec
echo.
echo =====================================================================
set /p choice="Zvolte moznost [1-5]: "

if "%choice%"=="1" goto run_official
if "%choice%"=="2" goto run_interactive
if "%choice%"=="3" goto run_tests
if "%choice%"=="4" goto open_traces
if "%choice%"=="5" goto exit

echo Neplatna volba, zkuste to znovu.
pause
goto menu

:run_official
cls
echo =====================================================================
echo Spoustim ukazkove behy a generuji traces...
echo =====================================================================
echo.
.\.venv\Scripts\python run_agent.py
echo.
echo Stisknete libovolnou klavesu pro navrat do menu...
pause > nul
goto menu

:run_interactive
cls
echo =====================================================================
echo Spoustim interaktivniho agenta...
echo =====================================================================
echo.
.\.venv\Scripts\python run_agent.py --interactive
echo.
echo Stisknete libovolnou klavesu pro navrat do menu...
pause > nul
goto menu

:run_tests
cls
echo =====================================================================
echo Spoustim Unit Testy...
echo =====================================================================
echo.
.\.venv\Scripts\python -m unittest tests/test_agent.py -v
echo.
echo Stisknete libovolnou klavesu pro navrat do menu...
pause > nul
goto menu

:open_traces
explorer "%~dp0traces"
goto menu

:exit
exit
