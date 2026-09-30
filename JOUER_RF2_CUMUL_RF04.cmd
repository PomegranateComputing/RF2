@echo off
setlocal
rem Red Flags 2 - candidate CUMUL (Cumul 30/09 : ligne de production, chaine reparee, Luna Park RF04 RF05 RF06, lots Astra du 30/09 (infirmier V03, RF01 V03, Luna tranche 01)).
rem Build fige : dist\candidates\RF2_CUMUL_20260930_1821\RF2_CUMUL.pk3  (sha256 6c85e747bbae437f9b9ccd05e9602ea1d310cd8451b870271cff6ec3dc89ec31)
rem Configuration et sauvegardes propres a ce lot ; la configuration personnelle n'est pas modifiee.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "PK3=%ROOT%dist\candidates\RF2_CUMUL_20260930_1821\RF2_CUMUL.pk3"
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
echo RF2 candidate CUMUL : dist\candidates\RF2_CUMUL_20260930_1821\RF2_CUMUL.pk3 - depart direct RF04
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_cumul" -skill 2 +map RF04 %*
exit /b %errorlevel%
