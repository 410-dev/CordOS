do {
    if (Test-Path .\restart) {
        Remove-Item .\restart -Force
    }

    if (Test-Path .\venv\Scripts\Activate.ps1) {
        .\venv\Scripts\Activate.ps1
    }

    python3 ./bootloader.py $args

    Remove-Item -Path ./data/cache -Recurse -Force -ErrorAction SilentlyContinue

} while (Test-Path .\restart)
