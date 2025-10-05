@echo off
setlocal

rem Start Flask app from CMD (Windows)
rem Usage:
rem   start.bat                      -> FLASK_CONFIG=default
rem   start.bat development          -> FLASK_CONFIG=development
rem   start.bat default skipinstall  -> skip pip install

rem Go to repo root (this file's directory)
pushd "%~dp0"

set CONFIG=%1
if "%CONFIG%"=="" set CONFIG=default
set SKIP=%2

set VENV=.venv
set ACTIVATE=%VENV%\Scripts\activate.bat

rem Create virtual env if missing
if not exist "%ACTIVATE%" (
  echo Creating virtual env .venv
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3 -m venv "%VENV%"
  ) else (
    python -m venv "%VENV%"
  )
)

rem Activate venv
call "%ACTIVATE%"
if errorlevel 1 (
  echo Failed to activate .venv
  exit /b 1
)

rem Install dependencies (unless skipinstall)
if /i "%SKIP%"=="skipinstall" (
  echo Skipping dependency installation [skipinstall]
) else (
  if exist requirements.txt (
  echo Upgrading pip and installing dependencies
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
  )
)

rem Set configuration and start app
set FLASK_CONFIG=%CONFIG%
echo Starting app with FLASK_CONFIG=%FLASK_CONFIG%
python run.py

popd
endlocal
