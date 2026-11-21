@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo.
echo AMOSPro AGA M19 P2d - REBUILD depuis ASM editable MC68020
echo Sources : src\native\m19_p2d\M19_P2C_PLANES_MC68020.s + M19_P2D_CONTROLS_MC68020.s
echo Sortie : src\generated\p2d_editable\
echo.
set "VASM="
if defined VASM_M68K if exist "%VASM_M68K%" set "VASM=%VASM_M68K%"
if not defined VASM if exist "tools\vasmm68k_mot.exe" set "VASM=%CD%\tools\vasmm68k_mot.exe"
if not defined VASM (
  where vasmm68k_mot.exe >nul 2>nul
  if not errorlevel 1 set "VASM=vasmm68k_mot.exe"
)
if not defined VASM (
  echo [ERREUR] vasmm68k_mot.exe absent. Place-le dans tools\.
  pause
  exit /b 1
)
where py >nul 2>nul
if not errorlevel 1 (
  set "PY=py -3"
) else (
  set "PY=python"
)
%PY% tools\build_m19_p2d_editable_asm.py --vasm "%VASM%" %*
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo [ERREUR] Assemblage refuse. Aucune Lib officielle modifiee.
  pause
  exit /b %RC%
)
echo.
echo [OK] Assemblage et controles de structure termines.
echo ATTENTION : une Lib editee n'est PAS validee sous WinUAE.
pause
exit /b 0
