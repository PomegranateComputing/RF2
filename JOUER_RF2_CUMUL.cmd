@echo off
setlocal
rem Red Flags 2 - candidate CUMUL (Tout en un : ligne de production (ennemis, menus, plaques RF01, HUD, RF02, pied-de-biche) + matieres RF01 1940 (candidate 1606)).
rem Build fige : dist\candidates\RF2_CUMUL_20260929_1801\RF2_CUMUL.pk3  (sha256 5115307cd01b0c3ff98d81095a917fc930da316dcf20f75efa48432be278c684)
rem Configuration et sauvegardes propres a ce lot ; la configuration personnelle n'est pas modifiee.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "PK3=%ROOT%dist\candidates\RF2_CUMUL_20260929_1801\RF2_CUMUL.pk3"
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
echo RF2 candidate CUMUL : dist\candidates\RF2_CUMUL_20260929_1801\RF2_CUMUL.pk3
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_cumul" %*
exit /b %errorlevel%
