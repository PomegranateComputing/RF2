@echo off
setlocal
rem Red Flags 2 - BANC DU BOSS (hors campagne) : le surveillant-chef, prototype (adaptation declaree).
rem Module dist\boss\RF2_BOSS_ESSAI_20261001_1605\RF2_BOSS_ESSAI.pk3 (sha256 6203958d4fd5af947fa9a695552b71bc80a0803747dca664984fd680a755fc86)
rem Base   dist\boss\base\RF2_BASE_0efa372613c3.pk3 (sha256 0efa372613c3b84579f61dd53bad6a70f5f2eb15a4991d7c3dc9b0c4caf696db)
rem Configuration, sauvegardes et journaux propres au banc ; ni la partie normale ni ses sauvegardes ne sont touchees.
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
set "BASE=%ROOT%dist\boss\base\RF2_BASE_0efa372613c3.pk3"
set "MODULE=%ROOT%dist\boss\RF2_BOSS_ESSAI_20261001_1605\RF2_BOSS_ESSAI.pk3"
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
set "CFG=%ROOT%user\uzdoom_boss_essai.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_boss_essai" mkdir "%ROOT%user\savegames_boss_essai"
if not exist "%ROOT%user\logs_boss_essai" mkdir "%ROOT%user\logs_boss_essai"
set "D=%DATE:/=-%"
set "D=%D: =_%"
set "T=%TIME: =0%"
set "T=%T::=-%"
set "T=%T:.=-%"
set "T=%T:,=-%"
set "LOG=%ROOT%user\logs_boss_essai\essai_%D%_%T%.log"
echo RF2 BANC DU BOSS (hors campagne) : dist\boss\RF2_BOSS_ESSAI_20261001_1605\RF2_BOSS_ESSAI.pk3
echo Journal : %LOG%
"%ENGINE%" -iwad "%IWAD%" -file "%BASE%" "%MODULE%" -config "%CFG%" -savedir "%ROOT%user\savegames_boss_essai" -skill 2 -stdout +map BOSS01 %* > "%LOG%" 2>&1
exit /b %errorlevel%
