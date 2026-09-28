@echo off
setlocal
rem Red Flags 2 - candidate RF01-PAN (RF01 accepte + 13 panneaux muraux retablis, releves et poses sur leur mur (lot isole)).
rem Build fige : dist\candidates\RF2_RF01-PAN_20260928_0725\RF2_RF01-PAN.pk3  (sha256 1439a27e8be3136d0b5054649f5c91946b7c65a6a1785127e30724dfcfed93fc)
rem Configuration et sauvegardes propres a ce lot ; la configuration personnelle n'est pas modifiee.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "PK3=%ROOT%dist\candidates\RF2_RF01-PAN_20260928_0725\RF2_RF01-PAN.pk3"
if not exist "%PK3%" (
    echo Build absent : %PK3%
    exit /b 1
)
if not exist "%ENGINE%" (
    echo UZDoom absent : %ENGINE%
    exit /b 1
)
set "CFG=%ROOT%user\uzdoom_rf01pan.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_rf01pan" mkdir "%ROOT%user\savegames_rf01pan"
echo RF2 candidate RF01-PAN : dist\candidates\RF2_RF01-PAN_20260928_0725\RF2_RF01-PAN.pk3
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_rf01pan" %*
exit /b %errorlevel%
