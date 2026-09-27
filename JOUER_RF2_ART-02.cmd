@echo off
setlocal
rem Red Flags 2 - candidate ART-02 (RF2-ART-02 : ennemis RF01 retouches par Astra, seuls, sur RF01 accepte).
rem Build fige : dist\candidates\RF2_ART-02_20260927_1356\RF2_ART-02.pk3  (sha256 3e67b20b6ff43db94b2aeb5d7ae200058f6cc213b41bc8b16405f263df3297df)
rem Configuration et sauvegardes propres a ce lot ; la configuration personnelle n'est pas modifiee.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "PK3=%ROOT%dist\candidates\RF2_ART-02_20260927_1356\RF2_ART-02.pk3"
if not exist "%PK3%" (
    echo Build absent : %PK3%
    exit /b 1
)
if not exist "%ENGINE%" (
    echo UZDoom absent : %ENGINE%
    exit /b 1
)
set "CFG=%ROOT%user\uzdoom_art02.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_art02" mkdir "%ROOT%user\savegames_art02"
echo RF2 candidate ART-02 : dist\candidates\RF2_ART-02_20260927_1356\RF2_ART-02.pk3
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_art02" %*
exit /b %errorlevel%
