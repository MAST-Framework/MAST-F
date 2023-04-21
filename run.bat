@echo off

if [%1]==[] goto usage
SET conf=%1
goto :run
:usage
SET conf=127.0.0.1:8000
:run
set venv=.\venv\Scripts\activate
set server=.\venv\Scripts\waitress-serve.exe
if exist %server% (
  echo Running MobSF on %conf%
  %venv%
  %server% --listen=%conf% --threads=10 --channel-timeout=3600 mastf.MASTF.wsgi:application
) else (
  echo [ERROR] Incomplete setup. Please ensure that setup.bat completes without any errors.
  pause
  exit /b
)