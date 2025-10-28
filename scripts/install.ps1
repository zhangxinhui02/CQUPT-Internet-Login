Set-Location ..
$INSTALL_DIR = (Get-Location).Path
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt
mkdir bin
Copy-Item .\assets\cqupt-internet.bat bin
(Get-Content .\bin\cqupt-internet.bat) -replace '\$\{INSTALL_DIR\}', $INSTALL_DIR |
    Set-Content .\bin\cqupt-internet.bat
$BIN_PATH = $INSTALL_DIR + '\bin'
$systemPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($systemPath -notlike "*$BIN_PATH*") {
    # 拼接新的路径
    $newSystemPath = $systemPath + ";" + $BIN_PATH
    # 设置系统环境变量
    [Environment]::SetEnvironmentVariable("Path", $newSystemPath, "Machine")
    $env:Path += ";${BIN_PATH}"
    Write-Host "Path environment variable updated."
} else {
    Write-Host "Path environment variable already been updated."
}
Write-Host "Install succeed."
