import asyncio

from bs4 import BeautifulSoup
from pyppeteer import launch


async def dive_into(goto_url):
    browser = await launch(headless=True)  # 无头模式
    page = await browser.newPage()
    await page.goto(goto_url)

    await page.waitFor(5000)

    # 获取页面源代码
    html = await page.content()
    print(html)

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html, 'html.parser')

    # 提取数据，
    title = soup.find('h1', class_='EReoAc').text
    print(title)

    await browser.close()


asyncio.get_event_loop().run_until_complete(dive_into('https://artsandculture.google.com/asset/%E8%83%8C%E9%9D%A2/FgFghicvPD7JUw?childAssetId=7QGJ1IAMe-sFkg'))
