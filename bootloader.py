"""
Bootloader unlock module.
Handles the main unlock application logic with BURST mode (multi-threaded requests).
"""

import json
import time
import threading

from colorama import init, Fore, Style

from device import generate_device_id
from http_session import HTTP11Session
from status_checker import check_unlock_status
from time_sync import get_initial_beijing_time, get_synchronized_beijing_time, wait_until_target_time

init(autoreset=True)

APPLY_URL = "https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth"
BURST_COUNT = 30
BURST_INTERVAL = 0.015  # seconds between each thread (15ms)


def print_header() -> None:
    """Print the application header."""
    print(Style.BRIGHT + Fore.CYAN + "=" * 60)
    print(Style.BRIGHT + Fore.CYAN + "        Xiaomi Bootloader Unlock Tool")
    print(Style.BRIGHT + Fore.CYAN + "           BURST MODE - 10 Threads")
    print(Style.BRIGHT + Fore.CYAN + "=" * 60 + Style.RESET_ALL)
    print()


def request_worker(
    session: HTTP11Session,
    url: str,
    headers: dict,
    start_beijing_time,
    start_timestamp: float,
    thread_id: int,
    cookie_value: str,
    device_id: str
) -> None:
    """
    Worker function for each burst thread.
    
    Args:
        session: The HTTP session instance.
        url: The API endpoint URL.
        headers: Request headers.
        start_beijing_time: The initial synchronized Beijing time.
        start_timestamp: The local timestamp when sync occurred.
        thread_id: The thread identifier.
        cookie_value: The authentication cookie.
        device_id: The generated device ID.
    """
    try:
        request_time = get_synchronized_beijing_time(start_beijing_time, start_timestamp)
        print(f"🚀 Thread-{thread_id} gönderildi: {request_time.strftime('%H:%M:%S.%f')}")

        response = session.make_request('POST', url, headers=headers)
        if response is None:
            print(Fore.RED + f"   Thread-{thread_id}: Bağlantı hatası")
            return

        response_data = response.data
        response.release_conn()
        json_response = json.loads(response_data.decode('utf-8'))
        code = json_response.get("code")
        data = json_response.get("data", {})

        if code == 0:
            apply_result = data.get("apply_result")
            if apply_result == 1:
                print(Style.BRIGHT + Fore.GREEN + f"\n✅ [BAŞARILI] Başvuru ONAYLANDI! (Thread-{thread_id})" + Style.RESET_ALL)
                check_unlock_status(session, cookie_value, device_id)
            elif apply_result == 3:
                deadline = data.get("deadline_format", "?")
                print(Fore.YELLOW + f"   Thread-{thread_id}: Limit doldu, {deadline} tarihinde tekrar dene.")
            elif apply_result == 4:
                deadline = data.get("deadline_format", "?")
                print(Fore.YELLOW + f"   Thread-{thread_id}: Engelli, {deadline} tarihine kadar.")
        elif code == 100001:
            print(Fore.RED + f"   Thread-{thread_id}: İstek hatası (100001)")
        elif code == 100003:
            print(Fore.GREEN + f"   Thread-{thread_id}: Muhtemelen onaylandı (100003), kontrol ediliyor...")
            check_unlock_status(session, cookie_value, device_id)
        elif code is not None:
            print(Fore.YELLOW + f"   Thread-{thread_id}: Bilinmeyen kod: {code}")
        else:
            print(Fore.RED + f"   Thread-{thread_id}: Yanıt kodu yok")

    except Exception:
        pass


def run_bootloader_unlock(cookie_value: str, feed_time_shift: float) -> None:
    """
    Run the bootloader unlock process with BURST mode.
    
    Args:
        cookie_value: The authentication token.
        feed_time_shift: The delay in milliseconds before midnight.
    """
    print_header()

    device_id = generate_device_id()
    session = HTTP11Session()

    if not check_unlock_status(session, cookie_value, device_id):
        return

    start_beijing_time = get_initial_beijing_time()
    if start_beijing_time is None:
        print(Fore.RED + "[Error] " + Fore.WHITE + "Pekin zamanı belirlenemedi.")
        input("\nKapatmak için Enter'a bas...")
        exit()

    start_timestamp = time.time()
    wait_until_target_time(start_beijing_time, start_timestamp, feed_time_shift)

    headers = {
        "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
    }

    print(Style.BRIGHT + Fore.YELLOW + f"\n🔥 BURST MODE: {BURST_COUNT} paralel istek gönderiliyor..." + Style.RESET_ALL)

    threads = []
    for i in range(BURST_COUNT):
        t = threading.Thread(
            target=request_worker,
            args=(session, APPLY_URL, headers, start_beijing_time, start_timestamp, i + 1, cookie_value, device_id)
        )
        t.start()
        threads.append(t)
        time.sleep(BURST_INTERVAL)

    for t in threads:
        t.join()

    print(Style.BRIGHT + Fore.CYAN + "\n" + "=" * 60)
    print("İşlem tamamlandı. Sonuçları yukarıdan kontrol edin.")
    print("=" * 60 + Style.RESET_ALL)
    input("\nKapatmak için Enter'a bas...")
