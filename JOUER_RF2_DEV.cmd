@echo off
setlocal
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build.ps1"
if errorlevel 1 exit /b %errorlevel%
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run.ps1" -Map RF01
exit /b %errorlevel%
