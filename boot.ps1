if (Test-Path .\venv) {
    .\venv\Scripts\Activate.ps1
}
python3 ./bootloader.py $args
rm -rf ./data/cache