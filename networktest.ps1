$IsWin = [System.Environment]::OSVersion.Platform -eq "Win32NT"
$Uname = if (-Not $IsWin -And (Get-Command uname -ErrorAction SilentlyContinue)) {
    & uname -s
} else {
    ""
}
$IsMac = $Uname -eq "Darwin"
$IsLin = $Uname -eq "Linux"
$PythonCommand = if ($IsWin) { "python" } else { "python3" }

# 檢查 Python 是否安裝
if (-Not (Get-Command $PythonCommand -ErrorAction SilentlyContinue)) {
    Write-Host "未找到 $PythonCommand，請根據作業系統安裝 Python。"
    Write-Host "1. Windows: 從 https://www.python.org/ 下載並安裝 Python"
    Write-Host "2. macOS/Linux: 請執行系統相關的安裝命令 (如: brew install python3)"
    Exit 1
}

Write-Host "$PythonCommand 已安裝"

$TempDir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
$VenvDir = Join-Path $TempDir "venv"
$ScriptPath = Join-Path $TempDir "networktest.py"

New-Item -ItemType Directory -Path $TempDir | Out-Null

try {
    Write-Host "正在建立臨時 Python 虛擬環境..."
    & $PythonCommand -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        throw "無法建立 Python 虛擬環境"
    }

    $VenvPython = if ($IsWin) {
        Join-Path $VenvDir "Scripts/python.exe"
    } else {
        Join-Path $VenvDir "bin/python"
    }

    # 檢查並安裝必要的依賴項
    $RequiredPackages = @("requests", "tqdm", "speedtest-cli")
    foreach ($Package in $RequiredPackages) {
        & $VenvPython -m pip show $Package *> $null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "正在安裝 $Package..."
            & $VenvPython -m pip install $Package
            if ($LASTEXITCODE -ne 0) {
                throw "無法安裝 $Package"
            }
        } else {
            Write-Host "$Package 已安裝"
        }
    }

    # 執行 Python 腳本
    $URL = "https://raw.githubusercontent.com/OH4MA/NetworkTest_Script/main/networktest.py"
    Invoke-WebRequest -Uri $URL -OutFile $ScriptPath
    & $VenvPython $ScriptPath
    if ($LASTEXITCODE -ne 0) {
        throw "Python 網路測試腳本執行失敗"
    }
} catch {
    Write-Host "無法執行 Python 網路測試腳本: $_"
    Exit 1
} finally {
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir
    }
}
