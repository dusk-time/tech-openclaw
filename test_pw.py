import asyncio
from playwright.async_api import async_playwright

async def test():
    p = await async_playwright().start()
    b = await p.chromium.launch(headless=False)
    page = await b.new_page()
    await page.goto('https://example.com')
    print(f'Title: {await page.title()}')
    await page.screenshot(path='test.png')
    print('Screenshot saved')
    await b.close()
    await p.stop()

asyncio.run(test())
