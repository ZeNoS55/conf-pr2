@echo off
setlocal
py -3 -m src.main %*
if errorlevel 1 (
    python -m src.main %*
)
endlocal
