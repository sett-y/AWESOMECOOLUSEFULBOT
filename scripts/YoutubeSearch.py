from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def youtubeSearch(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Dnt": "1",
            "Sec-Ch-Ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Ch-Ua-Platform-Version": "10.0.0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        await page.set_extra_http_headers(headers)

        if await page.goto(url):
            print("scraping")
        else:
            print("problem accessing page")

        await page.wait_for_load_state('networkidle')
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(6000)
        print("page loaded")

        html = BeautifulSoup(await page.content(), 'html.parser')
        thumbnails = html.find_all('img', {'class': 'yt-core-image yt-core-image--fill-parent-height yt-core-image--fill-parent-width yt-core-image--content-mode-scale-aspect-fill yt-core-image--loaded'})
        thumbnailList = []

        # need to limit this or the scraping itself
        for img in thumbnails:
            #src = img['src']
            thumbnailList.append(img['src'])
            print(img['src'])
        
        return thumbnailList