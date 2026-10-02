@echo off
setlocal
rem Red Flags 2 - candidate PORTES (Passe sur les portes du 02/10 : portes, grilles, rideaux et facades des 23 cartes ; lots Codex du 01/10 au soir).
rem Build fige : dist\candidates\RF2_PORTES_20261002_1018\RF2_PORTES.pk3  (sha256 469418f215a662bb8e04e45b0d852c6376c2457e89b534b54877397e1cb21cb5)
rem Configuration et sauvegardes propres a ce lot ; la configuration personnelle n'est pas modifiee.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "PK3=%ROOT%dist\candidates\RF2_PORTES_20261002_1018\RF2_PORTES.pk3"
if not exist "%PK3%" (
    echo Build absent : %PK3%
    exit /b 1
)
if not exist "%ENGINE%" (
    echo UZDoom absent : %ENGINE%
    exit /b 1
)
set "CFG=%ROOT%user\uzdoom_portes.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_portes" mkdir "%ROOT%user\savegames_portes"
echo RF2 candidate PORTES : dist\candidates\RF2_PORTES_20261002_1018\RF2_PORTES.pk3 - depart direct RF01
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_portes" -skill 2 +map RF01 %*
exit /b %errorlevel%
