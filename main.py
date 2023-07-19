from html.parser import HTMLParser
from bs4 import BeautifulSoup, NavigableString

from concurrent import futures
from requests_ip_rotator import ApiGateway

import requests as rq 
import json
import re

import os
from shutil import rmtree

from random import choice

with open('useragents.txt', 'r') as ua:
    HEADERS = []
    for line in ua.readlines():
          HEADERS.append({'User-Agent': line.strip()})
TEMPFOLDER = './temp'

g = ApiGateway("https://nsw2u.net/")
g.start()
s = rq.Session()
s.mount('https://nsw2u.net', g)

class GameLinkParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
        self.grab_data = False
        self.re = re.compile(r'(-nsp)|(-nsz)|(-xci)')
    
    def handle_starttag(self, tag, attrs): 
        if tag == 'a':
            for name, value in attrs:
                if name == 'href' and self.re.search(value): 
                    self.grab_data = True
                    self.links.append([None, value,])

    def handle_data(self, data):
        if self.grab_data == True:
            self.links[len(self.links) - 1][0] = data
            self.grab_data = False

def parse_popular_game_links() -> list:
    url = "https://nsw2u.net/switch-posts"
    soup = BeautifulSoup(s.get(url).content.decode(), features="lxml")
    tab = soup.find_all('td')
    tab = [t for t in tab if 'Zelda' in str(tab)][2]

    
    hd = choice(HEADERS)
    gl_parser = GameLinkParser()
    links = tab.find_all('a')
    for link in links:
        gl_parser.feed(s.get(link.attrs['href'].replace('.com', '.net'), headers=hd).content.decode())

    parser_links = [link for link in gl_parser.links if link[0] != None and link[0] != '\n']
    for _,link in parser_links:
        link.replace('.com', '.net')
    return parser_links
    
def parse_tables(html: str) -> dict:
    soup = BeautifulSoup(html, features="lxml")
    rows = [r for r in soup('tr') if 'ouo' in str(r) and 3 <= len(r.find_all('td')) <= 4]
    ret = {}
    reg = re.compile(r'(KB)|(MB)|(GB)')

    for row in rows:
        cells = row.find_all('td')

        try:
            if len(cells) == 3:
                links = cells[2].find_all('a')
                filetype = cells[0].string.split(' ')[-1].lower()
                title = " ".join(cells[0].string.split(' ')[:-1])
            else:
                links = cells[3].find_all('a')
                filetype = cells[1].string.lower()
                title = cells[0].string

            size_elem = row.find_all(string=reg)[0]
        except: continue

        ret[title] = {
            'filetype': filetype.strip(),
            'size': size_elem.strip(),
            'links': { link.string.lower().strip():link.attrs['href'] for link in links }
        }
        print(json.dumps(ret[title], indent=2))
    return ret

def scrape_game_page(link: str) -> dict:
    game = {}
    print(f'\tParsing {link}')
    res = None
    try:
        
        hd = choice(HEADERS)
        res = s.get(link, headers=hd, allow_redirects=True)
    except Exception as e:    
        print(f'\tCould not make request, {e}')
    try:
        game = parse_tables(res.content.decode())
    except Exception as e:
        print(f'\tCould not parse HTML, {e}')

    return game

def scrape_chunk(chunk: list):
    games = {}
    for title, link in chunk[1]:
        games[title] = scrape_game_page(link)
    
    with open(f'temp/scrape-{chunk[0]}.json', 'w') as f:
        json.dump(games, f)

def main():
    
    if os.path.exists(TEMPFOLDER):
        rmtree(TEMPFOLDER)

    os.mkdir(TEMPFOLDER)

    url = 'https://nsw2u.net/switch-posts'
    gl_parser = GameLinkParser()
    
    hd = choice(HEADERS)
    res = s.get(url, headers=hd)
    gl_parser.feed(res.content.decode())
    
    for i in range(2, 7):     
        hd = choice(HEADERS)
        res = s.get(url + f'-{i}', headers=hd)
        gl_parser.feed(res.content.decode())
    
    links = gl_parser.links
    links += parse_popular_game_links()
    
    chunk_size = 200
    links_chunked = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]
    links_chunked_enum = list(enumerate(links_chunked))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(scrape_chunk, links_chunked_enum)

    print("Gluing JSON chunks") 
    games = {}
    for file in os.listdir(TEMPFOLDER):
        with open(os.path.join(TEMPFOLDER, file), 'r') as f:
            games.update(json.load(f))
    games = {k:v for k,v in games.items() if v != {}}

    with open('final_scrape.json', 'w') as o:
        json.dump(games, o, indent=2)
    
    rmtree(TEMPFOLDER)
    g.shutdown()
if __name__ == '__main__': main()
