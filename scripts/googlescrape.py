from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random
async def get_search(search_term) -> str:
    search_term = search_term
    async with async_playwright() as p:
        try:
        #launch browser
            browser = await p.chromium.launch(headless=True)
        except Exception as e:
            print(f"Unable to launch browser: {e}")
        page = await browser.new_page()
        url = f'https://www.google.com/search?q={search_term}'
        if await page.goto(url):
            print(f"Scraping page...")
        else:
            print("Scraping unsuccessful")
        #waits for js to actually generate html
        await page.wait_for_load_state('networkidle')

        html = BeautifulSoup(await page.content(), 'html.parser')
        #title = html.find_all('h3', {'class': 'LC20lb MBeuO DKV0Md'})
        indv_html = html.find_all('span', {'jscontroller': 'msmzHf'})
        data = []
        for i in range(len(indv_html)):
            title_url = indv_html[i].find('a', {'jsname': 'UWckNb'})
            title = indv_html[i].find('h3', {'class': 'LC20lb MBeuO DKV0Md'})
            result_dict = {'title': title.contents[0], 'url': title_url['href']}
            data.append(result_dict)
        await browser.close()
        print("Scraping Complete")
        return data