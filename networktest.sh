#!/bin/bash
set -euo pipefail

# 檢查 Python 是否安裝
if ! command -v python3 &>/dev/null; then
    echo "Python3未安裝，可依照作業系統使用以下指令安裝:"
    echo "1. Debian/Ubuntu: sudo apt update && sudo apt install python3"
    echo "2. CentOS/Red Hat: sudo yum install python3"
    echo "3. macOS (使用HomeBrew): brew install python3"
    exit 1
fi

echo "Python3已安裝"

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "正在建立臨時 Python 虛擬環境..."
if ! python3 -m venv "$TEMP_DIR/venv"; then
    echo "無法建立 Python 虛擬環境，請確認已安裝 venv 模組。"
    echo "Debian/Ubuntu 可嘗試: sudo apt install python3-venv"
    exit 1
fi

VENV_PYTHON="$TEMP_DIR/venv/bin/python"

# 檢查並安裝必要的依賴項
REQUIRED_PACKAGES=(requests tqdm speedtest-cli)
for PACKAGE in "${REQUIRED_PACKAGES[@]}"; do
    if ! "$VENV_PYTHON" -m pip show "$PACKAGE" &>/dev/null; then
        echo "正在安裝 $PACKAGE..."
        "$VENV_PYTHON" -m pip install "$PACKAGE"
    else
        echo "$PACKAGE 已安裝"
    fi
done

# 線上執行 Python 腳本
URL="https://raw.githubusercontent.com/OH4MA/NetworkTest_Script/main/networktest.py"

if ! curl -fsSL "$URL" | "$VENV_PYTHON" -; then
    echo "無法執行 Python 網路測試腳本"
    exit 1
fi
