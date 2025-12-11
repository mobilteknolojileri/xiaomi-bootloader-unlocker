import time
from datetime import datetime, timezone, timedelta
import ntplib
import pytz
from colorama import Fore

NTP_SERVERS = [
    "ntp0.ntp-servers.net",
    "ntp1.ntp-servers.net",
    "ntp2.ntp-servers.net",
    "ntp3.ntp-servers.net",
    "ntp4.ntp-servers.net",
    "ntp5.ntp-servers.net",
    "ntp6.ntp-servers.net"
]

BEIJING_TZ = pytz.timezone("Asia/Shanghai")

def get_initial_beijing_time():
    client = ntplib.NTPClient()
    
    for server in NTP_SERVERS:
        try:
            print(Fore.YELLOW + f"\nPekin'deki mevcut zaman belirleniyor" + Fore.RESET)
            response = client.request(server, version=3)
            ntp_time = datetime.fromtimestamp(response.tx_time, timezone.utc)
            beijing_time = ntp_time.astimezone(BEIJING_TZ)
            print(Fore.GREEN + f"[Pekin zamanı]: " + Fore.RESET + f"{beijing_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
            return beijing_time
        except Exception as e:
            print(f"{server} bağlantı hatası: {e}")
    
    print(f"Hiçbir NTP sunucusuna bağlanılamadı.")
    return None

def get_synchronized_beijing_time(start_beijing_time, start_timestamp):
    elapsed = time.time() - start_timestamp
    current_time = start_beijing_time + timedelta(seconds=elapsed)
    return current_time

def wait_until_target_time(start_beijing_time, start_timestamp, feed_time_shift):
    feed_time_shift_seconds = feed_time_shift / 1000
    next_day = start_beijing_time + timedelta(days=1)
    
    print(Fore.YELLOW + f"\nBootloader kilit açma başvurusu yapılıyor" + Fore.RESET)
    print(Fore.GREEN + f"[Belirtilen gecikme]: " + Fore.RESET + f"{feed_time_shift:.2f} ms.")
    
    target_time = next_day.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=feed_time_shift_seconds)
    print(Fore.GREEN + f"[Bekleniyor]: " + Fore.RESET + f"{target_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f"Lütfen pencereyi kapatmayın...")

    while True:
        current_time = get_synchronized_beijing_time(start_beijing_time, start_timestamp)
        time_diff = target_time - current_time

        if time_diff.total_seconds() > 1:
            time.sleep(min(1.0, time_diff.total_seconds() - 1))
        elif current_time >= target_time:
            print(f"Zaman ulaşıldı: {current_time.strftime('%Y-%m-%d %H:%M:%S.%f')}. İstek gönderiliyor...")
            break
        else:
            time.sleep(0.0001)