@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo.
echo AMOS Professional AGA - export assembleur natif MC68020 verifie
echo Source : dist\AMOSPro_AGA.Lib (lecture seule)
echo Sortie : src\generated\
echo.
if not exist "tools\generate_aga_native_source.py" (
  echo [ERREUR] Generateur source manquant.
  pause
  exit /b 1
)
if not exist "dist\AMOSPro_AGA.Lib" (
  echo [ERREUR] Bibliotheque active absente.
  pause
  exit /b 1
)
set "VASM="
if defined VASM_M68K (
  if exist "%VASM_M68K%" set "VASM=%VASM_M68K%"
)
if not defined VASM (
  where vasmm68k_mot.exe >nul 2>nul
  if not errorlevel 1 set "VASM=vasmm68k_mot.exe"
)
if not defined VASM (
  if exist "tools\vasmm68k_mot.exe" set "VASM=%CD%\tools\vasmm68k_mot.exe"
)
if not defined VASM (
  echo [ERREUR] vasmm68k_mot.exe introuvable.
  echo Installe vasm Motorola et ajoute-le au PATH, ou definis VASM_M68K.
  echo La generation n'est pas declaree verifiee sans l'assembleur.
  pause
  exit /b 2
)
where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON=py -3"
) else (
  set "PYTHON=python"
)
%PYTHON% "tools\generate_aga_native_source.py" --lib "dist\AMOSPro_AGA.Lib" --out "src\generated" --baseline none --strict --verify-vasm "%VASM%" %*
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo [ERREUR] Source assembleur non identique a la Lib officielle.
  echo Aucune bibliotheque installee ou sous dist n'a ete modifiee.
  pause
  exit /b %RC%
)
echo.
echo [OK] Assemblage MC68020 et comparaison binaire avec la Lib active.
echo Source principale : src\generated\AMOSPro_AGA_R88_NATIVE.s
echo Modules inclus  : C2P, IFF, BOBS, AGA.
echo ATTENTION : les octets encore non classes sont conserves en DC.B.
echo La validation vasm ne prouve pas les Gates WinUAE B/C.
echo Aucune Lib officielle n'a ete remplacee.
pause
exit /b 0
