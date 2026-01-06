"""
Bootloader unlock module.
Handles the main unlock application logic and response processing.
"""

import json
import time

from colorama import init, Fore, Style

from device import generate_device_id
from http_session import HTTP11Session
from status_checker import check_unlock_status
from time_sync import get_initial_beijing_time, get_synchronized_beijing_time, wait_until_target_time

init(autoreset=True)

APPLY_URL = "https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth"


def print_header() -> None:
    """Print the application header."""
    print(Style.BRIGHT + Fore.CYAN + "=" * 60)
    print(Style.BRIGHT + Fore.CYAN + "        Xiaomi Bootloader Unlock Tool")
    print(Style.BRIGHT + Fore.CYAN + "=" * 60 + Style.RESET_ALL)
    print()


def process_apply_response(
    json_response: dict,
    session: HTTP11Session,
    cookie_value: str,
    device_id: str
) -> None:
    """
    Process the bootloader unlock application response.
    
    Args:
        json_response: The JSON response from the API.
        session: The HTTP session instance.
        cookie_value: The authentication cookie.
        device_id: The generated device ID.
    """
    code = json_response.get("code")
    data = json_response.get("data", {})

    if code == 0:
        apply_result = data.get("apply_result")

        if apply_result == 1:
            print(Fore.GREEN + "[Status] " + Fore.WHITE + "Application approved, checking status...")
            check_unlock_status(session, cookie_value, device_id)

        elif apply_result == 3:
            deadline = data.get("deadline_format", "Not specified")
            print(Fore.YELLOW + "[Status] " + Fore.WHITE + f"Application failed - limit exceeded. Try again on {deadline}.")
            input("\nPress Enter to exit...")
            exit()

        elif apply_result == 4:
            deadline = data.get("deadline_format", "Not specified")
            print(Fore.YELLOW + "[Status] " + Fore.WHITE + f"Application blocked until {deadline}.")
            input("\nPress Enter to exit...")
            exit()

    elif code == 100001:
        print(Fore.RED + "[Error] " + Fore.WHITE + "Application rejected - request error.")
        print(Fore.YELLOW + f"[Debug] {json_response}")

    elif code == 100003:
        print(Fore.GREEN + "[Status] " + Fore.WHITE + "Application probably approved, checking status...")
        check_unlock_status(session, cookie_value, device_id)

    elif code is not None:
        print(Fore.YELLOW + f"[Status] " + Fore.WHITE + f"Unknown status code: {code}")
        print(Fore.YELLOW + f"[Debug] {json_response}")
    else:
        print(Fore.RED + "[Error] " + Fore.WHITE + "Response missing required code.")
        print(Fore.YELLOW + f"[Debug] {json_response}")


def run_bootloader_unlock(cookie_value: str, feed_time_shift: float) -> None:
    """
    Run the bootloader unlock process.
    
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
        print(Fore.RED + "[Error] " + Fore.WHITE + "Could not determine Beijing time.")
        input("\nPress Enter to exit...")
        exit()

    start_timestamp = time.time()
    wait_until_target_time(start_beijing_time, start_timestamp, feed_time_shift)

    headers = {
        "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
    }

    try:
        while True:
            request_time = get_synchronized_beijing_time(start_beijing_time, start_timestamp)
            print(Fore.CYAN + "[Request] " + Fore.WHITE + f"Sending at {request_time.strftime('%Y-%m-%d %H:%M:%S.%f')} (UTC+8)")

            response = session.make_request('POST', APPLY_URL, headers=headers)
            if response is None:
                continue

            response_time = get_synchronized_beijing_time(start_beijing_time, start_timestamp)
            print(Fore.CYAN + "[Response] " + Fore.WHITE + f"Received at {response_time.strftime('%Y-%m-%d %H:%M:%S.%f')} (UTC+8)")

            try:
                response_data = response.data
                response.release_conn()
                json_response = json.loads(response_data.decode('utf-8'))
                process_apply_response(json_response, session, cookie_value, device_id)

            except json.JSONDecodeError:
                print(Fore.RED + "[Error] " + Fore.WHITE + "Failed to parse JSON response.")
                print(Fore.YELLOW + f"[Raw] {response_data}")
            except Exception as e:
                print(Fore.RED + f"[Error] " + Fore.WHITE + f"Response processing failed: {e}")
                continue

    except Exception as e:
        print(Fore.RED + f"[Error] " + Fore.WHITE + f"Request failed: {e}")
        input("\nPress Enter to exit...")
        exit()
