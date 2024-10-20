import time

import requests

if __name__ == '__main__':
    while True:
        print(requests.get("https://aetheranime.onrender.com/"))
        time.sleep(60)