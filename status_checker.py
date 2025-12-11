import json
from colorama import Fore

STATUS_CHECK_URL = "https://sgp-api.buy.mi.com/bbs/api/global/user/bl-switch/state"

def check_unlock_status(session, cookie_value, device_id):
    try:
        headers = {
            "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
        }
        
        response = session.make_request('GET', STATUS_CHECK_URL, headers=headers)
        
        if response is None:
            print(f"[Hata] Kilit açma durumu alınamadı.")
            return False

        response_data = json.loads(response.data.decode('utf-8'))
        response.release_conn()

        if response_data.get("code") == 100004:
            print(f"[Hata] Cookie süresi doldu, güncellenmesi gerekiyor!")
            input(f"Kapatmak için Enter tuşuna basın...")
            exit()

        data = response_data.get("data", {})
        is_pass = data.get("is_pass")
        button_state = data.get("button_state")
        deadline_format = data.get("deadline_format", "")

        if is_pass == 4:
            if button_state == 1:
                print(Fore.GREEN + f"[Hesap durumu]: " + Fore.RESET + f"başvuru yapılabilir.")
                return True

            elif button_state == 2:
                print(Fore.GREEN + f"[Hesap durumu]: " + Fore.RESET + f"başvuru engeli {deadline_format} (Ay/Gün) tarihine kadar.")
                status_response = input(f"Devam etmek ister misiniz (" + Fore.BLUE + f"Evet/Hayır" + Fore.RESET + f")?: ")
                if status_response.lower() in ['e', 'evet', 'y', 'yes']:
                    return True
                else:
                    input(f"Kapatmak için Enter tuşuna basın...")
                    exit()
                    
            elif button_state == 3:
                print(Fore.GREEN + f"[Hesap durumu]: " + Fore.RESET + f"hesap 30 günden daha yeni oluşturulmuş.")
                status_response = input(f"Devam etmek ister misiniz (" + Fore.BLUE + f"Evet/Hayır" + Fore.RESET + f")?: ")
                if status_response.lower() in ['e', 'evet', 'y', 'yes']:
                    return True
                else:
                    input(f"Kapatmak için Enter tuşuna basın...")
                    exit()
                    
        elif is_pass == 1:
            print(Fore.GREEN + f"[Hesap durumu]: " + Fore.RESET + f"başvuru onaylandı, {deadline_format} tarihine kadar kilit açılabilir.")
            input(f"Kapatmak için Enter tuşuna basın...")
            exit()
        else:
            print(Fore.GREEN + f"[Hesap durumu]: " + Fore.RESET + f"bilinmeyen durum.")
            input(f"Kapatmak için Enter tuşuna basın...")
            exit()
            
    except Exception as e:
        print(f"[Durum kontrol hatası] {e}")
        return False