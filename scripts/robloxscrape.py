from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random

limit = 0
async def get_gamedata(id='') -> str:
    global limit
    rand = False
    if id == '':
        rand = True
        id = random.randint(16454399300, 17262338236)
    url =f"https://www.roblox.com/games/{id}"

    async with async_playwright() as p:
        try:
        #launch browser
            browser = await p.chromium.launch(headless=True)
        except Exception as e:
            print(f"Unable to launch browser: {e}")
        page = await browser.new_page()

        if await page.goto(url):
            print(f"Scraping Roblox page gameID:{id}...")
        else:
            print("Scraping unsuccessful")
        #waits for js to actually generate html
        await page.wait_for_load_state('networkidle')

        html = BeautifulSoup(await page.content(), 'html.parser')
        if html.find('h4', class_='error-message') is not None:
            if rand == True and limit != 10:
                limit += 1
                return await get_gamedata()
            else:
                return 1
        #print(html)
        data = []
        player_count = html.find("p", {'class': 'text-lead font-caption-body'})
        player_count = player_count.contents[0]
        game_name = html.find("h1", {'class': 'game-name'})
        game_name = game_name.contents[0]
        game_thumbnail = html.find("span", {'class': 'thumbnail-2d-container carousel-item carousel-item-active-out'})
        game_link = url
        try:
            game_thumbnail = game_thumbnail.find("img", {'class': ''})
            game_thumbnail = game_thumbnail['src']
        except:
            print('No Thumbnail')
            game_thumbnail = 'https://t7.rbxcdn.com/180DAY-57443971b3b446cb6440e98718617428'
        data.append(game_name)
        data.append(player_count)
        data.append(game_thumbnail)
        data.append(game_link)
        await browser.close()
        print("Scraping Complete")
        return data