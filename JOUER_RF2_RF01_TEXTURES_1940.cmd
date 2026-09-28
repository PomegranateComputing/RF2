@echo off
setlocal
rem Red Flags 2 - candidate RF01_TEXTURES_1940 (RF01 materiaux Sainte-Anne 1940 (Astra 28/09), RF01 seul).
rem Build fige : dist\candidates\RF2_RF01_TEXTURES_1940_20260928_1745\RF2_RF01_TEXTURES_1940.pk3  (sha256 1c77187c3856c842bd39d1c57194365b4ef00600e14587096f0d923cd9d5125f)
rem Configuration et sauvegardes propres a ce lot ; la configuration personnelle n'est pas modifiee.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "PK3=%ROOT%dist\candidates\RF2_RF01_TEXTURES_1940_20260928_1745\RF2_RF01_TEXTURES_1940.pk3"
if not exist "%PK3%" (
    echo Build absent : %PK3%
    exit /b 1
)
if not exist "%ENGINE%" (
    echo UZDoom absent : %ENGINE%
    exit /b 1
)
set "CFG=%ROOT%user\uzdoom_rf01_textures_1940.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_rf01_textures_1940" mkdir "%ROOT%user\savegames_rf01_textures_1940"
echo RF2 candidate RF01_TEXTURES_1940 : dist\candidates\RF2_RF01_TEXTURES_1940_20260928_1745\RF2_RF01_TEXTURES_1940.pk3
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_rf01_textures_1940" %*
exit /b %errorlevel%
