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
    call python .\bootloader.py --safe %*
) else (
    call python .\bootloader.py %*
)

:: Directly check the errorlevel
if errorlevel 1 (
    if errorlevel 3 (
        echo. > .\safe_restart
    ) else (
        echo. > .\restart
    )
)

if exist ".\tmp" (
    rmdir /s /q ".\tmp"
)

if not exist ".\restart" (
    if not exist ".\safe_restart" (
        goto :eof
    )
)

goto loop
