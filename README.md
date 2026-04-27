# 網路測試腳本
短時間測太多次會被 Speedtest 暫時拒絕訪問，但 GCP 節點延遲測試依舊可用。

腳本會自動建立臨時 Python 虛擬環境並安裝必要套件，執行完畢後會清除，不會修改系統 Python 套件。

**需求**
- Python 3
- Linux 若無法建立虛擬環境，請先安裝 `python3-venv`

**Linux/MacOS**
```
curl -sL https://raw.githubusercontent.com/OH4MA/NetworkTest_Script/main/networktest.sh | bash
```

**Windows Powershell/或Linux和MacOS的Powershell**
```
Invoke-Expression (Invoke-WebRequest -Uri "https://raw.githubusercontent.com/OH4MA/NetworkTest_Script/main/networktest.ps1" -UseBasicParsing).Content
```

Powered by Google Cloud Platform and  Ookla Speedtest

Made by LIU MINKAI
