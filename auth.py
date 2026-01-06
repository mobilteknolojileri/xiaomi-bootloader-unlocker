"""
Authentication module for Xiaomi account login.
Handles secure authentication with Xiaomi's API.
"""

import base64
import hashlib
import json
from urllib.parse import urlparse, parse_qs, quote
from getpass import getpass

import requests

BASE_URL = "https://account.xiaomi.com"
SID = "18n_bbs_global"
USER_AGENT = "okhttp/4.12.0"


def parse_response(response: requests.Response) -> dict:
    """Parse Xiaomi API response, removing the callback prefix."""
    return json.loads(response.text[11:])


def authenticate_user() -> str:
    """
    Authenticate user with Xiaomi account.
    
    Returns:
        str: The service token for authenticated session.
    
    Raises:
        SystemExit: If authentication fails after user cancellation.
    """
    headers = {"User-Agent": USER_AGENT}
    
    while True:
        cookies = {}
        username = input("Xiaomi account (email or phone): ")
        password = getpass("Password: ")
        hashed_password = hashlib.md5(password.encode()).hexdigest().upper()
        
        try:
            # Step 1: Get login parameters
            response = requests.get(
                f"{BASE_URL}/pass/serviceLogin",
                params={'sid': SID, '_json': True},
                headers=headers,
                cookies=cookies
            )
            cookies.update(response.cookies.get_dict())
            
            # Step 2: Authenticate with credentials
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
            
            # Handle authentication errors
            if result.get("code") == 70016:
                print("❌ Incorrect username or password. Please try again.\n")
                continue
            
            if 'notificationUrl' in result:
                print("⚠️ Account verification required (2FA enabled). Please disable it.\n")
                continue
            
            # Step 3: Generate client signature
            nonce = result['nonce']
            ssecurity = result['ssecurity']
            client_sign = base64.b64encode(
                hashlib.sha1(f"nonce={nonce}&{ssecurity}".encode()).digest()
            ).decode()
            
            # Step 4: Get final authentication token
            result['location'] += f"&clientSign={quote(client_sign)}"
            final_cookies = requests.get(
                result['location'],
                headers=headers,
                cookies=cookies
            ).cookies.get_dict()
            
            token = final_cookies.get("new_bbs_serviceToken")
            
            if token:
                print("✅ Login successful.\n")
                return token
            else:
                print("❌ Login failed. Please try again.\n")
                
        except requests.RequestException as e:
            print(f"[Network Error] {e}\n")
        except (KeyError, json.JSONDecodeError) as e:
            print(f"[Parse Error] Invalid response from server: {e}\n")
        except Exception as e:
            print(f"[Error] {e}\n")