param(
    [string]$Interval = "60"
)
Set-Location ..
sc.exe create CQUPT-Internet-Autologin binPath= "$((Get-Command cqupt-internet.bat).Source) login -k --interval ${Interval}" DisplayName= "CQUPT-Internet-Autologin" start= auto
sc.exe start CQUPT-Internet-Autologin
Write-Host "Install succeed. Service `CQUPT-Internet-Autologin` was enabled and running now."
