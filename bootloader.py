import time
import json
from colorama import init, Fore, Style
from time_sync import get_initial_beijing_time, get_synchronized_beijing_time, wait_until_target_time
from http_session import HTTP11Session
from device import generate_device_id
from status_checker import check_unlock_status

init(autoreset=True)

APPLY_URL = "https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth"

def print_header():
    print(Style.BRIGHT + Fore.BLUE + "=" * 60 + Fore.RESET)
    print(Style.BRIGHT + Fore.BLUE + "Xiaomi Bootloader Unlock Tool" + Fore.RESET)
    print(Style.BRIGHT + Fore.BLUE + "=" * 60 + Fore.RESET)
    print("")

def process_apply_response(json_response, session, cookie_value, device_id):
    code = json_response.get("code")
    data = json_response.get("data", {})

    if code == 0:
        apply_result = data.get("apply_result")

        if apply_result == 1:
            print(Fore.GREEN + f"[Durum]: " + Fore.RESET +
                  f"Başvuru onaylandı, durum kontrol ediliyor...")
            check_unlock_status(session, cookie_value, device_id)

        elif apply_result == 3:
            deadline_format = data.get("deadline_format", "Belirtilmemiş")
            print(Fore.GREEN + f"[Durum]: " + Fore.RESET +
                  f"Başvuru yapılamadı, başvuru limiti aşıldı, {deadline_format} (Ay/Gün) tarihinde tekrar deneyin.")
            input(f"Kapatmak için Enter tuşuna basın...")
            exit()

        elif apply_result == 4:
            deadline_format = data.get("deadline_format", "Belirtilmemiş")
            print(Fore.GREEN + f"[Durum]: " + Fore.RESET +
                  f"Başvuru yapılamadı, {deadline_format} (Ay/Gün) tarihine kadar başvuru engeli var.")
            input(f"Kapatmak için Enter tuşuna basın...")
            exit()

    elif code == 100001:
        print(Fore.GREEN + f"[Durum]: " + Fore.RESET +
              f"Başvuru reddedildi, istek hatası.")
        print(Fore.GREEN + f"[TAM YANIT]: " + Fore.RESET + f"{json_response}")

    elif code == 100003:
        print(Fore.GREEN + f"[Durum]: " + Fore.RESET +
              f"Başvuru muhtemelen onaylandı, durum kontrol ediliyor...")
        print(Fore.GREEN + f"[Tam yanıt]: " + Fore.RESET + f"{json_response}")
        check_unlock_status(session, cookie_value, device_id)

    elif code is not None:
        print(Fore.GREEN + f"[Durum]: " + Fore.RESET +
              f"Bilinmeyen başvuru durumu: {code}")
        print(Fore.GREEN + f"[Tam yanıt]: " + Fore.RESET + f"{json_response}")
    else:
        print(Fore.GREEN + f"[Hata]: " + Fore.RESET +
              f"Yanıt gerekli kodu içermiyor.")
        print(Fore.GREEN + f"[Tam yanıt]: " + Fore.RESET + f"{json_response}")


def run_bootloader_unlock(cookie_value, feed_time_shift):
    print_header()

    device_id = generate_device_id()
    session = HTTP11Session()

    if not check_unlock_status(session, cookie_value, device_id):
        return

    start_beijing_time = get_initial_beijing_time()
    if start_beijing_time is None:
        print(f"Başlangıç zamanı belirlenemedi. Kapatmak için Enter tuşuna basın...")
        input()
        exit()

    start_timestamp = time.time()
    wait_until_target_time(
        start_beijing_time, start_timestamp, feed_time_shift)

    headers = {
        "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
    }

    try:
        while True:
            request_time = get_synchronized_beijing_time(
                start_beijing_time, start_timestamp)
            print(Fore.GREEN + f"[İstek]: " + Fore.RESET +
                  f"{request_time.strftime('%Y-%m-%d %H:%M:%S.%f')} (UTC+8) zamanında istek gönderiliyor")

            response = session.make_request('POST', APPLY_URL, headers=headers)
            if response is None:
                continue

            response_time = get_synchronized_beijing_time(
                start_beijing_time, start_timestamp)
            print(Fore.GREEN + f"[Yanıt]: " + Fore.RESET +
                  f"{response_time.strftime('%Y-%m-%d %H:%M:%S.%f')} (UTC+8) zamanında yanıt alındı")

            try:
                response_data = response.data
                response.release_conn()
                json_response = json.loads(response_data.decode('utf-8'))
                process_apply_response(
                    json_response, session, cookie_value, device_id)

            except json.JSONDecodeError:
                print(Fore.GREEN + f"[Hata]: " +
                      Fore.RESET + f"JSON yanıtı çözümlenemedi.")
                print(Fore.GREEN + f"[Sunucu yanıtı]: " +
                      Fore.RESET + f"{response_data}")
            except Exception as e:
                print(Fore.GREEN +
                      f"[Yanıt işleme hatası]: " + Fore.RESET + f"{e}")
                continue

    except Exception as e:
        print(Fore.GREEN + f"[İstek hatası]: " + Fore.RESET + f"{e}")
        input(f"Kapatmak için Enter tuşuna basın...")
        exit()
