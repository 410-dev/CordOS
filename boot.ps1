do {
    if (Test-Path .\restart) {
        Remove-Item .\restart -Force
    }

    if (Test-Path .\venv\Scripts\Activate.ps1) {
        .\venv\Scripts\Activate.ps1
    }

    python ./bootloader.py $args

    if ($LASTEXITCODE -eq 1) {
        New-Item -Path .\restart -ItemType "file" -Force
    }

    Remove-Item -Path ./data/cache -Recurse -Force -ErrorAction SilentlyContinue

} while (Test-Path .\restart)
