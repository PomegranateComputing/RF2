@echo off
setlocal
rem Red Flags 2 - candidate CUMUL (Cumul 30/09 : ligne de production (RF01 1940, RF02 corrige), code ennemis corrige, Luna Park RF04 RF05 RF06, chaine des chapitres reparee).
rem Build fige : dist\candidates\RF2_CUMUL_20260930_1724\RF2_CUMUL.pk3  (sha256 f8497716aef45354ec6bb572173f28cc4e9679d98d53ee4af95e20e2b28e72c3)
rem Configuration et sauvegardes propres a ce lot ; la configuration personnelle n'est pas modifiee.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "PK3=%ROOT%dist\candidates\RF2_CUMUL_20260930_1724\RF2_CUMUL.pk3"
if not exist "%PK3%" (
    echo Build absent : %PK3%
    exit /b 1
)
if not exist "%ENGINE%" (
    echo UZDoom absent : %ENGINE%
    exit /b 1
)
set "CFG=%ROOT%user\uzdoom_cumul.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_cumul" mkdir "%ROOT%user\savegames_cumul"
echo RF2 candidate CUMUL : dist\candidates\RF2_CUMUL_20260930_1724\RF2_CUMUL.pk3 - depart direct RF05
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_cumul" -skill 2 +map RF05 %*
exit /b %errorlevel%
