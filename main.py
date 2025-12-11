import subprocess
import sys
import os
import importlib


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    clear_screen()

    from auth import authenticate_user
    from config import get_feed_time_configuration
    from bootloader import run_bootloader_unlock

    token = authenticate_user()
    feed_time_shift = get_feed_time_configuration()
    run_bootloader_unlock(token, feed_time_shift)


if __name__ == "__main__":
    main()
