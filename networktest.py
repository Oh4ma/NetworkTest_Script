import importlib
import json
import re
import sys
import platform
from time import time

requests = None
tqdm = None
speedtest = None

def check_dependencies():
    global requests, tqdm, speedtest

    missing_dependencies = []
    dependencies = (
        ("requests", "requests"),
        ("tqdm", "tqdm"),
        ("speedtest", "speedtest-cli"),
    )

    loaded_modules = {}
    for import_name, package_name in dependencies:
        try:
            loaded_modules[import_name] = importlib.import_module(import_name)
        except ImportError:
            missing_dependencies.append(package_name)

    if missing_dependencies:
        print("缺少以下依賴項，請安裝後再執行:")
        for dep in missing_dependencies:
            print(f"- {dep}")
        print("\n建議使用 networktest.sh 或 networktest.ps1 執行，腳本會自動建立虛擬環境。")
        sys.exit(1)

    requests = loaded_modules["requests"]
    tqdm = loaded_modules["tqdm"].tqdm
    speedtest = loaded_modules["speedtest"]

def fetch_current_ip_info():
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        response.raise_for_status()
        data = response.json()
        ip = data.get("ip", "未知")
        city = data.get("city", "未知")
        country = data.get("country", "未知")
        isp = data.get("org", "未知")
        return ip, city, country, isp
    except Exception as e:
        print(f"取得目前網路資訊失敗: {e}")
        return "未知", "未知", "未知", "未知"

def fetch_endpoints(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"沒拿到GCP的節點: {e}")
        return None

def extract_urls_and_regions(endpoints_data):
    try:
        endpoints = json.loads(endpoints_data)
        return [
            (region, endpoint["URL"].rstrip("/") + "/api/ping")
            for region, endpoint in endpoints.items()
            if isinstance(endpoint, dict) and endpoint.get("URL")
        ]
    except json.JSONDecodeError:
        urls_and_regions = []
        endpoint_pattern = re.compile(r'"([a-z0-9-]+)": \{[^}]*?URL:\s+"(https?://[^"]+)"')
        matches = endpoint_pattern.findall(endpoints_data)
        for region, url in matches:
            clean_url = re.sub(r'/$', '', url)
            urls_and_regions.append((region, clean_url + "/api/ping"))
        return urls_and_regions

def check_https(url, attempts=5):
    try:
        total_time = 0
        for _ in range(attempts):
            start_time = time()
            response = requests.get(url, timeout=5)
            elapsed_time = (time() - start_time) * 1000 
            if response.status_code == 200:
                total_time += elapsed_time
            else:
                return None
        return total_time / attempts
    except Exception:
        return None

def network_speed_test():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  
        upload_speed = st.upload() / 1_000_000 
        return download_speed, upload_speed
    except Exception as e:
        print(f"網路測速失敗: {e}")
        return None, None

def main():
    check_dependencies()

    os_info = platform.platform()
    print(f"作業系統: {os_info}\n")

    ip, city, country, isp = fetch_current_ip_info()
    print(f"目前IP: {ip}")
    print(f"位置: {city}, {country}")
    print(f"ISP: {isp}\n")

    # 尋找GCP節點
    endpoints_url = "https://global.gcping.com/api/endpoints"
    endpoints_data = fetch_endpoints(endpoints_url)

    if not endpoints_data:
        return

    urls_and_regions = extract_urls_and_regions(endpoints_data)
    if not urls_and_regions:
        print("沒有取得可測試的 GCP 節點")
        return

    results = []
    with tqdm(total=len(urls_and_regions) + 1, desc="進度") as progress:
        for region, url in urls_and_regions:
            response_time = check_https(url)
            if response_time is not None:
                results.append((region, response_time))
            progress.update(1)

        download_speed, upload_speed = network_speed_test()
        progress.update(1)

    sorted_results = sorted(results, key=lambda x: x[1])

    print("\nGoogle Cloud Platform節點延遲測試結果(延遲僅供參考):")
    for region, response_time in sorted_results:
        print(f"{region} - {response_time:.2f} ms")

    if download_speed is not None and upload_speed is not None:
        print("\n網路測速結果:")
        print(f"下載速度: {download_speed:.2f} Mbps")
        print(f"上傳速度: {upload_speed:.2f} Mbps")

if __name__ == "__main__":
    main()
