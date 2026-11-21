@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
set "VASM=%ROOT%tools\vasmm68k_mot.exe"
if defined VASM_M68K if exist "%VASM_M68K%" set "VASM=%VASM_M68K%"
if not exist "%VASM%" (
  echo [ERREUR] vasmm68k_mot.exe absent dans tools\
  pause
  exit /b 1
)
if not exist "%ROOT%src\native\m19_p2d\M19_P2D_LINKED_EDITABLE.s" (
  echo [ERREUR] Source ASM maitre absent. Mets main a jour.
  pause
  exit /b 1
)
if not exist "%ROOT%src\generated\p2d_editable" mkdir "%ROOT%src\generated\p2d_editable"
cd /d "%ROOT%src\native\m19_p2d"
"%VASM%" -Fbin -m68020 -no-opt -quiet -o "%ROOT%src\generated\p2d_editable\M19_P2D_DIRECT_ASM_UNTESTED.Lib" "M19_P2D_LINKED_EDITABLE.s"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo [ERREUR] Echec assemblage. Aucune Lib officielle modifiee.
  pause
  exit /b %RC%
)
echo.
echo [OK] ASM direct termine : src\generated\p2d_editable\M19_P2D_DIRECT_ASM_UNTESTED.Lib
echo Le fichier est NON VALIDE si les sources ont ete modifiees.
echo Pour verifier les offsets AP20 et l'identite, lancer BUILD_P2D_ASM.bat.
pause
exit /b 0
