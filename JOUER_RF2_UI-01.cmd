@echo off
setlocal
rem Red Flags 2 - candidate UI-01 (RF2-UI-01 : menus, mort/reprise, art et sons UI Astra, sur RF01 accepte (ennemis d'origine)).
rem Build fige : dist\candidates\RF2_UI-01_20260927_1358\RF2_UI-01.pk3  (sha256 37e503f2a52d3d3db53fda61dc1688f6db499026bcb2031d09a34d10ee514dc8)
rem Configuration et sauvegardes propres a ce lot ; la configuration personnelle n'est pas modifiee.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "PK3=%ROOT%dist\candidates\RF2_UI-01_20260927_1358\RF2_UI-01.pk3"
if not exist "%PK3%" (
    echo Build absent : %PK3%
    exit /b 1
)
if not exist "%ENGINE%" (
    echo UZDoom absent : %ENGINE%
    exit /b 1
)
set "CFG=%ROOT%user\uzdoom_ui01.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_ui01" mkdir "%ROOT%user\savegames_ui01"
echo RF2 candidate UI-01 : dist\candidates\RF2_UI-01_20260927_1358\RF2_UI-01.pk3
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_ui01" %*
exit /b %errorlevel%
