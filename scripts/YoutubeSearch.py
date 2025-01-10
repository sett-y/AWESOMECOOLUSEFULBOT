from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def youtubeSearch(url):
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        if await page.goto(url):
            print("scraping")
        else:
            print("problem accessing page")

        await page.wait_for_load_state('networkidle')

        html = BeautifulSoup(await page.content(), 'html.parser')
        thumbnails = html.find_all('img', {'class': 'yt-simple-endpoint inline-block style-scope ytd-thumbnail'})
        thumbnailList = []

        for img in thumbnails:
            #src = img['src']
            thumbnailList.append(img['src'])