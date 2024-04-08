@echo off
:begin
if exist restart del /q restart

if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
python ./bootloader.py %*
set PYTHON_ERRORLEVEL=%ERRORLEVEL%
if %PYTHON_ERRORLEVEL%==1 echo > restart
rd /s /q data\cache

if exist restart goto begin
