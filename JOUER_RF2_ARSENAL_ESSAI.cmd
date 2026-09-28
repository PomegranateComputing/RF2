@echo off
setlocal
rem Red Flags 2 - BANC D'ESSAI DE L'ARSENAL (hors campagne) : W03 Manufrance Rapid, W04 Manurhin MR73.
rem Module dist\arsenal\RF2_ARSENAL_ESSAI_20260928_1822\RF2_ARSENAL_ESSAI.pk3 (sha256 ebca717d42d6e45292a27c4f304b024999ae0f2906fc890bb42f3f1181449313)
rem Base   dist\arsenal\base\RF2_BASE_src_23773520f797.pk3 (sha256 a03fad5f97fd7731b9f5a07c7332f709250a6e74bd6c76dbfe58b276444b644d)
rem Configuration, sauvegardes et journaux propres au banc ; ni la partie normale ni ses sauvegardes ne sont touchees.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "BASE=%ROOT%dist\arsenal\base\RF2_BASE_src_23773520f797.pk3"
set "MODULE=%ROOT%dist\arsenal\RF2_ARSENAL_ESSAI_20260928_1822\RF2_ARSENAL_ESSAI.pk3"
if not exist "%BASE%" (
    echo Build de base absent : %BASE%
    exit /b 1
)
if not exist "%MODULE%" (
    echo Module du banc absent : %MODULE%
    exit /b 1
)
if not exist "%ENGINE%" (
    echo UZDoom absent : %ENGINE%
    exit /b 1
)
set "CFG=%ROOT%user\uzdoom_arsenal_essai.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_arsenal_essai" mkdir "%ROOT%user\savegames_arsenal_essai"
if not exist "%ROOT%user\logs_arsenal_essai" mkdir "%ROOT%user\logs_arsenal_essai"
set "D=%DATE:/=-%"
set "D=%D: =_%"
set "T=%TIME: =0%"
set "T=%T::=-%"
set "T=%T:.=-%"
set "T=%T:,=-%"
set "STAMP=%D%_%T%"
set "LOG=%ROOT%user\logs_arsenal_essai\essai_%STAMP%.log"
echo RF2 BANC D'ESSAI ARSENAL (hors campagne) : dist\arsenal\RF2_ARSENAL_ESSAI_20260928_1822\RF2_ARSENAL_ESSAI.pk3
echo Journal : %LOG%
rem Journal par la sortie standard du moteur (+logfile n'est pas pris en compte en ligne de commande par UZDoom 5.0.1).
"%ENGINE%" -iwad "%IWAD%" -file "%BASE%" "%MODULE%" -config "%CFG%" -savedir "%ROOT%user\savegames_arsenal_essai" -skill 2 -stdout +map ARSENAL %* > "%LOG%" 2>&1
exit /b %errorlevel%
