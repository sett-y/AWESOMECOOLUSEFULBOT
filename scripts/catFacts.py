from playwright.async_api import async_playwright


url = "https://catfact.ninja/fact"

async def get_fact() -> str:
    async with async_playwright() as p:
        try:
        #launch browser
            browser = await p.chromium.launch(headless=True)
        except Exception as e:
            print(f"unable to launch browser: {e}")
        page = await browser.new_page()
        if await page.goto(url):
            print("scraping page...")
        else:
            print("scraping unsuccessful")

        #waits for js to actually generate html
        await page.wait_for_load_state('networkidle')

        html = await page.content()
        #print(html)

        await browser.close()


    htmlsplit1 = html.split('fact":"')
    htmlsplit2 = htmlsplit1[1].split('","length')
    finalHtml = htmlsplit2[0]
    return finalHtml