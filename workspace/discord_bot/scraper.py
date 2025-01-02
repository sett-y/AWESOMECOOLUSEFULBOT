"""idea: wrap program in single function that runs different functions based on string
passed as argument. this is to preserve the session throughout all the functions"""
#reminder: randomize request rates to seem human
import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import re
#import time

#ghetto enum
player1,player2,player3,player4,player5,player6,\
player7,player8,player9,player10=0,1,2,3,4,5,6,7,8,9

headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Dnt": "1",
        "Priority": "u=0, i",
        "Referer": "https://www.dotabuff.com/",
        "Sec-Ch-Ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Windows",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    }


async def player_id_to_url(id):
    pass


async def match_id_to_url(id):
    pass


#scrapes page data
async def fetch_page(url, session):
    async with session.get(url) as response:
        print("response object created")
        return await response.text()


#scrapes user profile and returns array of match ids
#can be reused for multiple commands potentially
async def return_matchids(url, session, lim):
    html = await fetch_page(url, session)
    print("user profile scraped")
    soup = BeautifulSoup(html, "html.parser")
    #need to find 5 a.won/a.lost elements and trim those to only /matches/XXXXXXXXXX
    match = soup.find_all('a',class_=["won","lost"],limit=lim)
    #convert ResultSet object to string for regex ops
    text = str(match)
    regpattern = r'/matches/(\d{10})'
    ids = re.findall(regpattern, text)
    print("returning match id html")
    return ids


#dont need ids just need to scrape first part of profileF UcK
#REWRITE
#scrape the recent match page data directly from user profile, as that has
#all the data needed for a brief summary
async def fetch_matches(ids, session):
    mid = []
    fullMatchList = []
    for i in enumerate(ids):
        mStr = "https://www.dotabuff.com/matches/" + str(ids[i])
        mid.append(mStr)
        print(f"match {i}: {mid[i]}")
    #now the list mid[] has the urls for the first 5 matches on the user's profile
    for i, m in enumerate(mid):
        #fullMatchList.append(display_multiple(m, session))
        print(f"appending parsed match #{i}")
    return fullMatchList
    

#parse user profile into displayable chunks (declare dictionary?)
async def parse_profile(url, session):
    html = await fetch_page(url, session)
    soup = BeautifulSoup(html, "html.parser")
    #r-row elements each contain a top hero's datas
    x = soup.find_all(class_='r-row')
    #each y is an individual r-row aka a single hero
    for y in x:
        try:
            heroes = []
            #for z in y.find_all('div',class_='r-row'):
            tophero = {
                "name": y.find(['div, a'],class_='r-none-mobile').text.strip(),
                "time": y.find('time').text.strip()
            }
            heroes.append(tophero)    
        except: continue
    
    #gets profile header data
    primary = soup.find('div',class_='header-content')
    #no need to loop, not dealing with multiple of similar elements like players or heroes
    total1 = primary.find(class_='wins').text.strip()
    total2 = primary.find(class_='losses').text.strip()
    total1 = total1.replace(',','')
    total2 = total2.replace(',','')
    total3 = int(total1) + int(total2)
    data = {
        "heroes": heroes,
        "name": primary.find('h1').text.strip(),
        "lastMatch": primary.find('time').text.strip(),
        "totalMatches": total3,
        #^ isnumeric? might have strange behavior on non immortal number ranks, needs testing
        "rank": primary.find(class_='leaderboard-rank-value').text.strip()
        
        }
    wr = primary.find_all('dd')
    for w in wr:
        if '%' in w.text.strip():
            data["winrate"] = w.text.strip()
    return data
        

#displays single match in detail
#id param returned from return_matchids
async def get_match_info(id, session):
    url = "https://www.dotabuff.com/matches/" + str(id)
    sides = ["radiant","dire"]
    html = await fetch_page(url, session)
    soup = BeautifulSoup(html, "html.parser")
    #ALL tr elements are now in x
    xydata = []
    for i in range(0,2):
        #add radiant or dire to beginning of dict
        xydata.append(sides[i])
        x = soup.find_all('tr',class_=f"faction-{sides[i]}")
        xdata = []
        #therefore y is individual tr elements (individual heroes)
        for y in x:
            try:
                #hero items
                items = []
                for z in y.find_all('div', class_='match-item-with-time'):
                    try:
                        #pack dict containing item and item time into items list
                        iset = {
                            #no .text() needed because title directly references a value
                            "name": z.find('img')['title'],
                            "time": z.find('span',class_="overlay-text bottom left").text.strip()
                        }
                        items.append(iset)
                    except: continue

                #data
                ydata = {
                    'name': y.find('a', class_=f'player-{sides[i]}').text.strip(),
                    'hero': y.find('span', class_=f'color-faction-{sides[i]}').text.strip(),
                    'lane_outcome': y.find('acronym', class_='lane-outcome').text.strip(),
                    'gold': y.find('td', class_='color-stat-gold').text.strip(),
                    'k': y.find_all('td', class_='tf-r')[0].text.strip(),
                    'd': y.find_all('td', class_='tf-r')[1].text.strip(),
                    'a': y.find_all('td', class_='tf-r')[2].text.strip(),
                    #{"name":,"time":}
                    'items': items
                }

                xdata.append(ydata)
            except: break
        
        xydata.append(xdata)
    return xydata
    

async def main():
    async with ClientSession(headers=headers) as session: 
        #placeholder user profile
        url = "https://www.dotabuff.com/players/392565237"
        #match = await return_matchids(url, session, 5)

        id = "8020934599"
        #m = return_matchids(392565237 ,session, 1)
        matchRadiant = await get_match_info(id, session)
        #matchRadiant is a list of dictionaries, each holding player data
        for x in matchRadiant:
            print(x)
        print('\n')
        
        print(matchRadiant)
        print('\n')

        profile = await parse_profile(url, session)
        print(profile)
        for p in profile["heroes"]:
            print(p)


        #print(f"match ids: {match}")
        
        print("\ndone")
        #headless browser to avoid blocking
        """async with async_playwright as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            #do scraping

            await browser.close()
        print("scraping complete.")"""

if __name__ == '__main__':
    asyncio.run(main())

#commands:
#recent: shows image of x recent matches
#match: shows detailed match data
#profile: display user profile info
#meta: shows top meta heroes (sort by role)