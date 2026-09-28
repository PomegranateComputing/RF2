@echo off
setlocal
rem Red Flags 2 - candidate HUD-02 (Portrait de Viktor, six etats de sante (cumulatif : RF01 + ART-02 + UI-01 + RF02)).
rem Build fige : dist\candidates\RF2_HUD-02_20260927_2230\RF2_HUD-02.pk3  (sha256 447f911efc594810f5e777987847b9690159dd6ef90b2b8c15f3cad55ad826d9)
rem Configuration et sauvegardes propres a ce lot ; la configuration personnelle n'est pas modifiee.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "PK3=%ROOT%dist\candidates\RF2_HUD-02_20260927_2230\RF2_HUD-02.pk3"
if not exist "%PK3%" (
    echo Build absent : %PK3%
    exit /b 1
)
if not exist "%ENGINE%" (
    echo UZDoom absent : %ENGINE%
    exit /b 1
)
set "CFG=%ROOT%user\uzdoom_hud02.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_hud02" mkdir "%ROOT%user\savegames_hud02"
echo RF2 candidate HUD-02 : dist\candidates\RF2_HUD-02_20260927_2230\RF2_HUD-02.pk3
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_hud02" %*
exit /b %errorlevel%
