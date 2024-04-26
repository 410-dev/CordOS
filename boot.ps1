do {
    if (Test-Path "./restart") {
        Remove-Item "./restart"
    }

    if (Test-Path "./venv") {
        . "./venv/Scripts/Activate.ps1"
    }

    if (Test-Path "./safe_restart") {
        Remove-Item "./safe_restart"
        python3 ./bootloader.py --safe $args
        $exit_code = $LASTEXITCODE
    } else {
        python3 ./bootloader.py $args
        $exit_code = $LASTEXITCODE
    }

    if ($exit_code -eq 1) {
        New-Item -ItemType File -Path "./restart" | Out-Null
    } elseif ($exit_code -eq 3) {
        New-Item -ItemType File -Path "./safe_restart" | Out-Null
    }

    if (Test-Path "./data/cache") {
        Remove-Item "./data/cache" -Recurse
    }

} while (Test-Path "./restart")
