@echo off
:loop
if exist ".\restart" (
    del ".\restart"
)

if exist ".\venv" (
    call .\venv\Scripts\activate.bat
)

if exist ".\safe_restart" (
    del ".\safe_restart"
    python .\bootloader.py --safe %*
    set exit_code=%errorlevel%
) else (
    python .\bootloader.py %*
    set exit_code=%errorlevel%
)

if %exit_code% equ 1 (
    echo. > .\restart
) else if %exit_code% equ 3 (
    echo. > .\safe_restart
)

if exist ".\data\cache" (
    rmdir /s /q ".\data\cache"
)

if not exist ".\restart" (
    goto :eof
)

goto loop
