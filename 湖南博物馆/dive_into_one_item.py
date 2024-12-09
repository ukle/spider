import asyncio

from bs4 import BeautifulSoup
from pyppeteer import launch

from shanmian_write_excel import shanmian_excel_aw


async def dive_into(goto_url):
    browser = await launch(headless=True)  # 无头模式
    page = await browser.newPage()
    await page.goto(goto_url)

    # 等待页面加载
    await page.waitForSelector('img')  # 等待图片元素加载

    # 获取页面源代码
    html = await page.content()
    # print(html)

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html, 'html.parser')

    # 提取数据，例如所有图片链接
    image = soup.find('img', id='imageP').get('src')
    title = soup.find('h1', id='page-title').text
    # 提取下一级的地址
    description = soup.find_all('p')[0].text

    data = [[title, image, description]]
    file_path = '扇面.xlsx'
    shanmian_excel_aw(data, file_path)

    await browser.close()


# asyncio.get_event_loop().run_until_complete(dive_into('https://www.hnmuseum.com/gallery/node/9853/0'))
