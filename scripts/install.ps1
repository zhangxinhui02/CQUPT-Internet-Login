param(
    [string]$__original_cwd  # 提权后恢复工作目录的参数
)

# 检查是否为管理员身份
function Test-IsElevated
{
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

# 检查是否为管理员身份，不是则提权
Write-Host "Checking permission..."
$scriptPath = $PSCommandPath
if (-not (Test-IsElevated))
{
    $cwd = (Get-Location).Path  # 保存现在的工作目录，供提权后恢复
    # 构造传入的参数：保留原始 $args，并追加内部参数
    $quotedArgs = $args | ForEach-Object { '"' + ($_ -replace '"', '\"') + '"' }
    $allArgs = @()
    $allArgs += '-NoProfile'
    $allArgs += '-ExecutionPolicy'
    $allArgs += 'Bypass'
    $allArgs += '-File'
    $allArgs += "`"$scriptPath`""
    if ($quotedArgs.Count -gt 0)
    {
        $allArgs += $quotedArgs
    }
    $allArgs += '-__original_cwd'
    $allArgs += "`"$cwd`""
    Start-Process -FilePath 'powershell.exe' -ArgumentList ($allArgs -join ' ') -Verb RunAs
    exit
}
# 提权后，如果收到 __original_cwd 参数，就恢复它为当前工作目录
if ($__original_cwd)
{
    try
    {
        Set-Location -LiteralPath $__original_cwd
    }
    catch
    {
        Write-Warning "Failed to change directory: $__original_cwd — $_"
        timeout 10
        exit
    }
}
Write-Host "Permission OK."

# 判断命令是否已安装
if (Get-Command cqupt-internet.ps1 -ErrorAction SilentlyContinue)
{
    Write-Host "Command 'cqupt-internet' has already been installed."
    timeout 10
    exit
}

# 定位到项目根目录
Set-Location ..
$INSTALL_DIR = (Get-Location).Path

# 准备Python虚拟环境
Write-Host "Preparing python virtual environment..."
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt

# 将命令复制到bin目录，并加入PATH环境变量
Write-Host "Setting command into PATH environment variable..."
mkdir bin
Copy-Item .\assets\cqupt-internet.ps1 bin
(Get-Content .\bin\cqupt-internet.ps1) -replace '\$\{INSTALL_DIR\}', $INSTALL_DIR |
        Set-Content .\bin\cqupt-internet.ps1  # 将命令中的占位符替换实际安装路径
$BIN_PATH = $INSTALL_DIR + '\bin'
$systemPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($systemPath -notlike "*$BIN_PATH*")
{
    # 拼接新的路径
    $newSystemPath = $systemPath + ";" + $BIN_PATH
    # 设置系统环境变量
    [Environment]::SetEnvironmentVariable("Path", $newSystemPath, "Machine")
    Write-Host "PATH environment variable updated."
}
else
{
    Write-Host "PATH environment variable already been updated."
}

# 安装完毕
Write-Host
Write-Host "========================================"
Write-Host "Install succeed. To use command 'cqupt-internet', you should restart existing shells."
Write-Host "========================================"
Write-Host
timeout 10
