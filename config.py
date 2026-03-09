"""
Configuration module for feed time settings.
"""

DEFAULT_FEED_TIME_MS = 100


def get_feed_time_configuration() -> float:
    """
    Get the feed time delay configuration from user input.
    
    Returns:
        float: The delay time in milliseconds.
    """
    while True:
        try:
            print("The bootloader application will be sent before midnight (Beijing Time).")
            print(f"Example: 200 ms delay = sends application at 23:59:59.800\n")
            print(f"Default delay: {DEFAULT_FEED_TIME_MS} ms")
            user_input = input("Enter delay in milliseconds (or press Enter for default): ").strip()
            
            if user_input == "":
                feed_time = float(DEFAULT_FEED_TIME_MS)
                print(f"[Config] Using default: {feed_time} ms\n")
            else:
                feed_time = float(user_input)
                print(f"[Config] Using custom: {feed_time} ms\n")
            
            return feed_time
        except ValueError:
            print("⚠️ Please enter a valid number.\n")