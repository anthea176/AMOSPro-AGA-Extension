@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo.
echo AMOSPro-AGA M19 P2d - source assembleur Motorola MC68020
echo Source Python : tools\build_m19_p2d_in_memory.py
echo Sortie : src\generated\p2d_source\
echo.
if not exist "tools\export_m19_p2d_native_source.py" (
  echo [ERREUR] Exporteur P2d manquant. Mets a jour la branche main.
  pause
  exit /b 1
)
if not exist "dist\AMOSPro_AGA.Lib" (
  echo [ERREUR] Lib P2d absente.
  pause
  exit /b 1
)
where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON=py -3"
) else (
  set "PYTHON=python"
)
set "VASM="
if defined VASM_M68K (
  if exist "%VASM_M68K%" set "VASM=%VASM_M68K%"
)
if not defined VASM (
  if exist "tools\vasmm68k_mot.exe" set "VASM=%CD%\tools\vasmm68k_mot.exe"
)
if not defined VASM (
  where vasmm68k_mot.exe >nul 2>nul
  if not errorlevel 1 set "VASM=vasmm68k_mot.exe"
)
if defined VASM (
  echo Verification vasm : %VASM%
  %PYTHON% "tools\export_m19_p2d_native_source.py" --out "src\generated\p2d_source" --vasm "%VASM%" %*
) else (
  echo [INFO] vasm absent : source genere, verification assembleur NON faite.
  %PYTHON% "tools\export_m19_p2d_native_source.py" --out "src\generated\p2d_source" %*
)
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo [ERREUR] Export ou verification source P2d echoue.
  echo Aucune bibliotheque officielle modifiee.
  pause
  exit /b %RC%
)
echo.
echo [OK] Sources assembleur P2d generees depuis le builder exact.
echo Voir src\generated\p2d_source\M19_P2D_SOURCE_MANIFEST.json
echo Verifier le champ verified_native_asm avant de reutiliser les .s.
echo dist\ et LAST_GOOD inchanges.
pause
exit /b 0