import asyncio
from pyppeteer import launch
from pyquery import PyQuery as pq

async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('https://www.hnmuseum.com/gallery/node/9853/1')
    doc = pq(await page.content())
    print(doc)
    
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())