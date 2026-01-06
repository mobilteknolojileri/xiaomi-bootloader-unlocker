"""
Device ID generation module.
"""

import hashlib
import random
import time


def generate_device_id() -> str:
    """
    Generate a unique device ID using SHA1 hash.
    
    Returns:
        str: A 40-character uppercase hexadecimal device ID.
    """
    random_data = f"{random.random()}-{time.time()}"
    device_id = hashlib.sha1(random_data.encode('utf-8')).hexdigest().upper()
    return device_id