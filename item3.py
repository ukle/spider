import asyncio

from bs4 import BeautifulSoup
from pyppeteer import launch


async def main():
    browser = await launch(headless=True)  # 无头模式
    page = await browser.newPage()
    await page.goto('https://www.hnmuseum.com/gallery/node/9853/1')

    # 等待页面加载
    await page.waitForSelector('img')  # 等待图片元素加载

    # 获取页面源代码
    html = await page.content()

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html, 'html.parser')

    # 提取数据，例如所有图片链接
    image = soup.find('img', id='imageP').get('src')
    print(image)

    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
