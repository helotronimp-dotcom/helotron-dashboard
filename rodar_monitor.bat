@echo off
REM ============================================================
REM  HELOTRON — Monitor de Precos Mercado Livre
REM  Clique duplo para rodar manualmente
REM ============================================================

set GMAIL_USER=helotron.imp@gmail.com
set GMAIL_APP_PASSWORD=COLE_AQUI_SUA_SENHA_DE_APP

python "%~dp0monitor_precos_cloud.py"

echo.
echo Pressione qualquer tecla para fechar...
pause > nul
