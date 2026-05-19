@echo off
chcp 65001 >nul
echo ==========================================
echo   Cattle Control — Build Revisao 0
echo ==========================================
echo.

echo [1/3] Buildando o frontend (Vue + Vite)...
pushd ..\frontend
call npm run build
if errorlevel 1 (
    echo.
    echo ERRO: falha no build do frontend.
    popd & pause & exit /b 1
)
popd
echo     Frontend OK — dist/ gerado.
echo.

echo [2/3] Empacotando com PyInstaller...
.venv\Scripts\pyinstaller.exe cattle_control.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo ERRO: falha no PyInstaller.
    pause & exit /b 1
)
echo     Executavel OK.
echo.

echo [3/3] Pronto!
echo.
echo  Distribuicao: dist\CattleControl\
echo  Copie a pasta inteira para o PC de destino
echo  e execute CattleControl.exe
echo.
echo  Na primeira execucao, configure:
echo  %%APPDATA%%\CattleControl\.env
echo    ANTHROPIC_API_KEY=...
echo    SYNC_SECRET=...
echo    CLOUD_SYNC_URL=...
echo.
pause
