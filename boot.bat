@echo off
:begin
if exist restart del /q restart

if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
python3 ./bootloader.py %*
if errorlevel 1 echo > restart
rd /s /q data\cache

if exist restart goto begin
