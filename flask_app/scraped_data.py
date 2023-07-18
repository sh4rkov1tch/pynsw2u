import json

def load(search_term: str, path = '../final_scrape.json') -> dict:
    with open(path, 'r') as f:
        games = json.load(f)
        return {k:v for k,v in games.items() if search_term.lower() in k.lower()}
