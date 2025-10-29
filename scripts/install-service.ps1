param(
    [string]$Interval = "60",  # 登录检查周期（秒），默认为60
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

# 判断cqupt-internet命令是否已安装
if (-not (Get-Command cqupt-internet.ps1 -ErrorAction SilentlyContinue))
{
    Write-Host "Command 'cqupt-internet' required. Install the command first."
    timeout 30
    exit
}

# 定位到项目根目录
Set-Location ..

# 检查并安装nssm
if (-not (Get-Command nssm -ErrorAction SilentlyContinue))
{
    Write-Host "Command 'nssm' required. Installing nssm..."
    # 创建并进入临时目录nssm-temp
    mkdir "nssm-temp"
    Set-Location nssm-temp
    mkdir "nssm_extracted"
    # 下载信息
    $downloadUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $tempZip = ".\nssm.zip"
    $extractPath = ".\nssm_extracted"
    Write-Host "Downloading nssm.zip..."
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempZip -UseBasicParsing
    Write-Host "Extracting zip..."
    Expand-Archive -LiteralPath $tempZip -DestinationPath $extractPath -Force
    $nssmExe = Get-ChildItem -Path $extractPath -Recurse -Filter "nssm.exe" |
            Where-Object { $_.FullName -match "win64" } |
            Select-Object -First 1
    if (-not $nssmExe)
    {
        Write-Host "Failed to get nssm.exe. Checking $downloadUrl or install nssm manually."
        Set-Location ..
        Remove-Item nssm-temp -Recurse -Force
        timeout 30
        exit 1
    }
    $targetPath = "..\bin\nssm.exe"
    Copy-Item $nssmExe.FullName $targetPath -Force
    if (Get-Command nssm -ErrorAction SilentlyContinue)
    {
        Write-Host "Command 'nssm' install succeed."
        Set-Location ..
        Remove-Item nssm-temp -Recurse -Force
    }
    else
    {
        Write-Host "Command 'nssm' not found, install failed. You can install the command 'nssm' manually."
        Set-Location ..
        Remove-Item nssm-temp -Recurse -Force
        timeout 30
        exit 1
    }
}
else
{
    Write-Host "Command 'nssm' existing."
}

# 安装并配置服务
mkdir service-logs
nssm install CQUPT-Internet-Autologin "$((Get-Location).Path)\.venv\Scripts\python.exe" "$((Get-Location).Path)\cli.py" login -k --interval ${Interval}
nssm set CQUPT-Internet-Autologin Start SERVICE_AUTO_START
# nssm set CQUPT-Internet-Autologin AppEnvironment "PYTHONUNBUFFERED=1"  # 禁用输出缓冲，会导致服务启动失败
nssm set CQUPT-Internet-Autologin AppStdout "$((Get-Location).Path)\service-logs\CQUPT-Internet-Autologin_out.log"
nssm set CQUPT-Internet-Autologin AppStderr "$((Get-Location).Path)\service-logs\CQUPT-Internet-Autologin_err.log"
nssm set CQUPT-Internet-Autologin AppRotateFiles 1
nssm set CQUPT-Internet-Autologin AppRotateOnline 1
nssm set CQUPT-Internet-Autologin AppRotateSeconds 86400

# 启动服务
nssm start CQUPT-Internet-Autologin

# 安装完毕
Write-Host
Write-Host "========================================"
Write-Host "Install succeed. Service `CQUPT-Internet-Autologin` was enabled and running now."
Write-Host "You can use 'nssm start/stop CQUPT-Internet-Autologin' to manage the service."
Write-Host "========================================"
Write-Host
timeout 10
