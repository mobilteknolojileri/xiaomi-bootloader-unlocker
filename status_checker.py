"""
Status checker module.
Checks the current unlock status of the user's account.
"""

import json
from colorama import Fore

from http_session import HTTP11Session

STATUS_CHECK_URL = "https://sgp-api.buy.mi.com/bbs/api/global/user/bl-switch/state"


def check_unlock_status(session: HTTP11Session, cookie_value: str, device_id: str) -> bool:
    """
    Check the current bootloader unlock status.
    
    Args:
        session: The HTTP session instance.
        cookie_value: The authentication cookie.
        device_id: The generated device ID.
        
    Returns:
        bool: True if ready to proceed, False otherwise.
    """
    try:
        headers = {
            "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
        }
        
        response = session.make_request('GET', STATUS_CHECK_URL, headers=headers)
        
        if response is None:
            print(Fore.RED + "[Error] " + Fore.WHITE + "Could not retrieve unlock status.")
            return False

        response_data = json.loads(response.data.decode('utf-8'))
        response.release_conn()

        # Check for expired session
        if response_data.get("code") == 100004:
            print(Fore.RED + "[Error] " + Fore.WHITE + "Session expired. Please login again.")
            input("\nPress Enter to exit...")
            exit()

        data = response_data.get("data", {})
        is_pass = data.get("is_pass")
        button_state = data.get("button_state")
        deadline_format = data.get("deadline_format", "")

        if is_pass == 4:
            if button_state == 1:
                print(Fore.GREEN + "[Account] " + Fore.WHITE + "Ready to apply for unlock.")
                return True

            elif button_state == 2:
                print(Fore.YELLOW + "[Account] " + Fore.WHITE + f"Application blocked until {deadline_format}.")
                response = input(f"Do you want to continue anyway? (" + Fore.CYAN + "yes/no" + Fore.RESET + "): ")
                if response.lower() in ['y', 'yes']:
                    return True
                else:
                    input("\nPress Enter to exit...")
                    exit()
                    
            elif button_state == 3:
                print(Fore.YELLOW + "[Account] " + Fore.WHITE + "Account is newer than 30 days.")
                response = input(f"Do you want to continue anyway? (" + Fore.CYAN + "yes/no" + Fore.RESET + "): ")
                if response.lower() in ['y', 'yes']:
                    return True
                else:
                    input("\nPress Enter to exit...")
                    exit()
                    
        elif is_pass == 1:
            print(Fore.GREEN + "[Account] " + Fore.WHITE + f"Already approved! Can unlock until {deadline_format}.")
            input("\nPress Enter to exit...")
            exit()
        else:
            print(Fore.YELLOW + "[Account] " + Fore.WHITE + "Unknown account status.")
            input("\nPress Enter to exit...")
            exit()
            
    except json.JSONDecodeError as e:
        print(Fore.RED + f"[Error] " + Fore.WHITE + f"Failed to parse status response: {e}")
        return False
    except Exception as e:
        print(Fore.RED + f"[Error] " + Fore.WHITE + f"Status check failed: {e}")
        return False