@echo off
setlocal
rem Red Flags 2 - candidate MAP-02 (RF02 Paris - Rue de service (cumulatif : RF01 accepte + ART-02 + UI-01 + RF02)).
rem Build fige : dist\candidates\RF2_MAP-02_20260927_1543\RF2_MAP-02.pk3  (sha256 11167ce28e37d07e84914435cc561d50d222e09824c142424c12c98c8778b7c1)
rem Configuration et sauvegardes propres a ce lot ; la configuration personnelle n'est pas modifiee.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "PK3=%ROOT%dist\candidates\RF2_MAP-02_20260927_1543\RF2_MAP-02.pk3"
if not exist "%PK3%" (
    echo Build absent : %PK3%
    exit /b 1
)
if not exist "%ENGINE%" (
    echo UZDoom absent : %ENGINE%
    exit /b 1
)
set "CFG=%ROOT%user\uzdoom_map02.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_map02" mkdir "%ROOT%user\savegames_map02"
echo RF2 candidate MAP-02 : dist\candidates\RF2_MAP-02_20260927_1543\RF2_MAP-02.pk3
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_map02" %*
exit /b %errorlevel%
