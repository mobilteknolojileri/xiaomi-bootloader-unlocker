import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_feed_time_configuration():
    while True:
        try:
            print("Bootloader başvurusu gece yarısından önce gönderilecek.")
            print("Örnek: 200 ms gecikme = 23:59:59.800'de başvuru gönderir")
            feed_time = float(input("\nGecikme süresi (milisaniye): "))
            clear_screen()
            return feed_time
        except ValueError:
            print("Lütfen geçerli bir sayı girin.")