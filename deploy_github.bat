@echo off
echo.
echo ============================================
echo  DEXIS Scanner - GitHub Pages Deployment
echo ============================================
echo.

git --version >/dev/null 2>&1
if errorlevel 1 (
    echo [FEHLER] Git ist nicht installiert!
    echo Bitte herunterladen: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [OK] Git gefunden.

gh --version >/dev/null 2>&1
if errorlevel 1 (
    echo [FEHLER] GitHub CLI nicht installiert!
    echo Bitte herunterladen: https://cli.github.com/
    echo Datei: gh_2.x.x_windows_amd64.msi
    start https://cli.github.com/
    pause
    exit /b 1
)
echo [OK] GitHub CLI gefunden.

gh auth status >/dev/null 2>&1
if errorlevel 1 (
    echo.
    echo [INFO] Starte GitHub Login - Browser oeffnet sich...
    gh auth login
    if errorlevel 1 (
        echo [FEHLER] Login fehlgeschlagen.
        pause
        exit /b 1
    )
)
echo [OK] GitHub Login aktiv.

if not exist "scanner-app.html" (
    echo [FEHLER] scanner-app.html nicht gefunden!
    echo Bitte dieses Skript im Ordner der App starten.
    pause
    exit /b 1
)

set TMPDIR=%TEMP%\dexis-deploy-%RANDOM%
mkdir "%TMPDIR%"
copy /Y "scanner-app.html" "%TMPDIR%\index.html" >nul

cd /d "%TMPDIR%"
git init -q
git add index.html
git commit -q -m "DEXIS Scanner App"

for /f "delims=" %%i in ('gh api user --jq .login') do set GH_USER=%%i
if "%GH_USER%"=="" (
    echo [FEHLER] GitHub-Benutzername nicht ermittelbar.
    pause
    exit /b 1
)
echo [OK] Benutzer: %GH_USER%

echo [INFO] Erstelle Repo und pushe...
gh repo create dexis-scanner --public --source=. --remote=origin --push
if errorlevel 1 (
    echo [HINWEIS] Repo existiert evtl. bereits - versuche Push...
    git remote set-url origin https://github.com/%GH_USER%/dexis-scanner.git
    git push -f origin HEAD:main
)

echo [INFO] Aktiviere GitHub Pages...
gh api repos/%GH_USER%/dexis-scanner/pages --method POST -f source[branch]=main -f source[path]=/ >/dev/null 2>&1
gh api repos/%GH_USER%/dexis-scanner/pages --method POST -f source[branch]=master -f source[path]=/ >/dev/null 2>&1

echo.
echo ============================================
echo  FERTIG!
echo ============================================
echo.
echo  Deine App-URL (nach 2-3 Min aktiv):
echo.
echo    https://%GH_USER%.github.io/dexis-scanner
echo.
echo  Diese URL bookmarken - sie aendert sich NIE!
echo.
pause
