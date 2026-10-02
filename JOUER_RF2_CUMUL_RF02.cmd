@echo off
setlocal
rem Red Flags 2 - candidate CUMUL (Cumul du 01/10 soir : RF06 eclaire, lots Codex de l'apres-midi (pilote Luna 02, facades, Brooklyn, machines et voute RF05, beton RF06, humidite V05, ciel RF04), cinq planches BD, sons d'armes recadres).
rem Build fige : dist\candidates\RF2_CUMUL_20261001_1605\RF2_CUMUL.pk3  (sha256 0efa372613c3b84579f61dd53bad6a70f5f2eb15a4991d7c3dc9b0c4caf696db)
rem Configuration et sauvegardes propres a ce lot ; la configuration personnelle n'est pas modifiee.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "PK3=%ROOT%dist\candidates\RF2_CUMUL_20261001_1605\RF2_CUMUL.pk3"
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
echo RF2 candidate CUMUL : dist\candidates\RF2_CUMUL_20261001_1605\RF2_CUMUL.pk3 - depart direct RF02
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_cumul" -skill 2 +map RF02 %*
exit /b %errorlevel%
