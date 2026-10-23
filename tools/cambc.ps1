# Wrapper for the cambc CLI installed by pip (not on PATH).
$cambc = "$env:LOCALAPPDATA\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe"
Set-Location (Split-Path $PSScriptRoot -Parent)
& $cambc @args
