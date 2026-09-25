@echo off
setlocal
rem Red Flags 2 - revue de la passe artistique RF2-ART-01.
rem Lance le build de revue fige (dist\review\LATEST.txt, ecrit par scripts\export_review.py) sans recompiler.
rem Configuration de revue separee : user\uzdoom_art_review.ini (copie de user\uzdoom.ini au premier lancement).
set "ROOT=%~dp0"
set "ENGINE=C:\PROJECTS\TOOLS\UZDoom-5.0.1\uzdoom.exe"
set "IWAD=C:\PROJECTS\TOOLS\Freedoom-0.13.0\freedoom2.wad"
if not exist "%ROOT%dist\review\LATEST.txt" (
    echo Aucun build de revue. Lancer : python scripts\export_review.py
    exit /b 1
)
set /p REVIEW=<"%ROOT%dist\review\LATEST.txt"
set "PK3=%ROOT%%REVIEW%"
if not exist "%PK3%" (
    echo Build de revue absent : %PK3%
    exit /b 1
)
if not exist "%ENGINE%" (
    echo UZDoom absent : %ENGINE%
    exit /b 1
)
set "CFG=%ROOT%user\uzdoom_art_review.ini"
if not exist "%ROOT%user" mkdir "%ROOT%user"
if not exist "%CFG%" if exist "%ROOT%user\uzdoom.ini" copy /y "%ROOT%user\uzdoom.ini" "%CFG%" >nul
if not exist "%ROOT%user\savegames_art_review" mkdir "%ROOT%user\savegames_art_review"
echo RF2 revue artistique : %REVIEW%
"%ENGINE%" -iwad "%IWAD%" -file "%PK3%" -config "%CFG%" -savedir "%ROOT%user\savegames_art_review" +map RF01 %*
exit /b %errorlevel%
