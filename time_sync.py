"""
Time synchronization module.
Provides accurate Beijing time synchronization using NTP servers.
"""

import time
from datetime import datetime, timezone, timedelta
from typing import Optional

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


def get_initial_beijing_time() -> Optional[datetime]:
    """
    Get the current Beijing time from NTP servers.
    
    Returns:
        datetime: Current Beijing time if successful, None if all servers failed.
    """
    client = ntplib.NTPClient()
    
    for server in NTP_SERVERS:
        try:
            print(Fore.YELLOW + "\n[Sync] " + Fore.WHITE + f"Connecting to {server}...")
            response = client.request(server, version=3)
            ntp_time = datetime.fromtimestamp(response.tx_time, timezone.utc)
            beijing_time = ntp_time.astimezone(BEIJING_TZ)
            print(Fore.GREEN + "[Sync] " + Fore.WHITE + f"Beijing time: {beijing_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
            return beijing_time
        except ntplib.NTPException as e:
            print(Fore.RED + f"[Sync] " + Fore.WHITE + f"{server} failed: {e}")
        except Exception as e:
            print(Fore.RED + f"[Sync] " + Fore.WHITE + f"{server} error: {e}")
    
    print(Fore.RED + "[Error] " + Fore.WHITE + "Could not connect to any NTP server.")
    return None


def get_synchronized_beijing_time(start_beijing_time: datetime, start_timestamp: float) -> datetime:
    """
    Calculate the current Beijing time based on elapsed local time.
    
    Args:
        start_beijing_time: The initial synchronized Beijing time.
        start_timestamp: The local timestamp when sync occurred.
        
    Returns:
        datetime: Current estimated Beijing time.
    """
    elapsed = time.time() - start_timestamp
    current_time = start_beijing_time + timedelta(seconds=elapsed)
    return current_time


def wait_until_target_time(
    start_beijing_time: datetime,
    start_timestamp: float,
    feed_time_shift: float
) -> None:
    """
    Wait until the target time before midnight.
    
    Args:
        start_beijing_time: The initial synchronized Beijing time.
        start_timestamp: The local timestamp when sync occurred.
        feed_time_shift: Delay in milliseconds before midnight.
    """
    feed_time_shift_seconds = feed_time_shift / 1000
    next_day = start_beijing_time + timedelta(days=1)
    
    print(Fore.CYAN + "\n[Scheduler] " + Fore.WHITE + "Preparing bootloader unlock request")
    print(Fore.CYAN + "[Config] " + Fore.WHITE + f"Delay: {feed_time_shift:.2f} ms before midnight")
    
    target_time = next_day.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=feed_time_shift_seconds)
    print(Fore.CYAN + "[Target] " + Fore.WHITE + f"Will send at: {target_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(Fore.YELLOW + "\n⏳ Waiting... Do not close this window.\n")

    while True:
        current_time = get_synchronized_beijing_time(start_beijing_time, start_timestamp)
        time_diff = target_time - current_time

        if time_diff.total_seconds() > 1:
            time.sleep(min(1.0, time_diff.total_seconds() - 1))
        elif current_time >= target_time:
            print(Fore.GREEN + f"[Trigger] " + Fore.WHITE + f"Target time reached: {current_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
            print(Fore.CYAN + "[Action] " + Fore.WHITE + "Sending request...\n")
            break
        else:
            time.sleep(0.0001)