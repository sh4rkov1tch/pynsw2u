import requests
import json
from main import scrape_game_page

def main():
    urls = [
        "https://nsw2u.net/broforce-switch-nsp",
    ]
    for url in urls:
        res = scrape_game_page(url, False)
        if res == {}:
            print(f"KO - {url}")
        else:
            print(f"OK - {url}")
            print(json.dumps(res, indent=2))

if __name__ == '__main__': main() 
