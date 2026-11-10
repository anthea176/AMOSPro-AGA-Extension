@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo.
echo AMOS Professional AGA - generation source assembleur Motorola 68000
echo Source active : dist\AMOSPro_AGA.Lib (lecture seule)
echo Sortie : src\generated\
echo.
if not exist "tools\generate_aga_native_source.py" (
  echo [ERREUR] Fichier tools\generate_aga_native_source.py absent.
  pause
  exit /b 1
)
if not exist "dist\AMOSPro_AGA.Lib" (
  echo [ERREUR] Binaire dist\AMOSPro_AGA.Lib absent.
  pause
  exit /b 1
)
where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON=py -3"
) else (
  set "PYTHON=python"
)
if not exist "src\generated" mkdir "src\generated"
%PYTHON% "tools\generate_aga_native_source.py" --lib "dist\AMOSPro_AGA.Lib" --out "src\generated" --baseline auto --strict %*
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo [ERREUR] Export refuse. Voir le detail de l'erreur Python.
  echo Aucune bibliotheque .Lib n'a ete modifiee.
  pause
  exit /b %RC%
)
echo.
echo Export termine. Ouvrir src\generated\AMOSPro_AGA_Rxx_NATIVE.s
echo IMPORTANT : le .s doit encore etre reassemble et compare avec la .Lib.
pause
exit /b 0
