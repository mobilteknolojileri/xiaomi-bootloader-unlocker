import requests
import json
import hashlib
import base64
import time
import os
from urllib.parse import urlparse, parse_qs, quote
from getpass import getpass

BASE_URL = "https://account.xiaomi.com"
SID = "18n_bbs_global"
USER_AGENT = "okhttp/4.12.0"

def parse_response(response):
    return json.loads(response.text[11:])

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def authenticate_user():
    headers = {"User-Agent": USER_AGENT}
    
    while True:
        cookies = {}
        username = input("Xiaomi hesabı (e-posta veya telefon): ")
        password = getpass("Şifre: ")
        hashed_password = hashlib.md5(password.encode()).hexdigest().upper()
        
        try:
            response = requests.get(
                f"{BASE_URL}/pass/serviceLogin",
                params={'sid': SID, '_json': True},
                headers=headers,
                cookies=cookies
            )
            cookies.update(response.cookies.get_dict())
            
            data = {k: v[0] for k, v in parse_qs(urlparse(parse_response(response)['location']).query).items()}
            data.update({'user': username, 'hash': hashed_password})
            
            response = requests.post(
                f"{BASE_URL}/pass/serviceLoginAuth2",
                data=data,
                headers=headers,
                cookies=cookies
            )
            cookies.update(response.cookies.get_dict())
            
            result = parse_response(response)
            
            if result.get("code") == 70016:
                print("❌ Hatalı kullanıcı adı veya şifre. Lütfen tekrar deneyin.")
                time.sleep(0.7)
                clear_screen()
                continue
            
            if 'notificationUrl' in result:
                print("⚠️ Hesap doğrulama gerekiyor (2FA etkin). Devre dışı bırakın.")
                time.sleep(0.9)
                clear_screen()
                continue
            
            nonce = result['nonce']
            ssecurity = result['ssecurity']
            client_sign = base64.b64encode(
                hashlib.sha1(f"nonce={nonce}&{ssecurity}".encode()).digest()
            ).decode()
            
            result['location'] += f"&clientSign={quote(client_sign)}"
            final_cookies = requests.get(
                result['location'],
                headers=headers,
                cookies=cookies
            ).cookies.get_dict()
            
            token = final_cookies.get("new_bbs_serviceToken")
            
            if token:
                print("✅ Giriş başarılı.")
                return token
            else:
                print("❌ Giriş başarısız. Tekrar deneyin.")
                time.sleep(0.7)
                clear_screen()
                
        except Exception as e:
            print(f"[Giriş hatası] {e}. Tekrar deneniyor.")
            time.sleep(0.7)
            clear_screen()