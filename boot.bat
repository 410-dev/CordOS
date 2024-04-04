if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
python3 ./bootloader.py %*
rd /s /q data\cache