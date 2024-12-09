import asyncio
import os
import time
from bs4 import BeautifulSoup
from pyppeteer_stealth import stealth  # 模拟浏览器指纹， 避免网站检测
from pyppeteer import launcher, launch

launcher.DEFAULT_ARGS.remove("--enable-automation")  # 取消自动设置默认参数， 避免网站检测

class LocalBrowser:
    def __init__(self):
        self.browser = None
        self.page = None
        self.agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/114.0.0.0 " \
                     "Safari/537.36 "  # RandomAgent.gen_agent() 随机生成User-Agent
        self.proxies = None  # RandomProxies.gen_proxies() 随机生成proxies

    async def close(self):
        self.browser.close()

    async def init_browser(self, config=None):
        self.browser = await launch(headless=False, dumpio=True, autoClose=False,
                               args=['--no-sandbox', '--window-size=1920,1080', '--disable-infobars'])  # 进入有头模式

    async def init_page(self, url):
        """
        url: 目标url
        selector: xpath选择器用于确认是否成功跳转到url
        """
        self.page = await self.browser.newPage()
        await stealth(self.page)  # 反浏览器指纹检测
        await self.page.setUserAgent(self.agent)
        # js 注入，防止网站检测navigator.webdriver
        await self.page.evaluateOnNewDocument(
            '() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }')
        # await self.page.setViewport({'width': 1100, "height": 768})  # 设置窗口大小,部分网页会检测窗口大小
        await self.page.goto(url)

def get_url_id(url):
    ahead = url.split('?')[0]
    subs = ahead.split('/')
    return subs[len(subs) - 1]

async def get_url_title(url):
    googleArt = LocalBrowser()
    url_id = get_url_id(url)
    await googleArt.init_browser()
    # 初始化登录页面，设置一些反反爬操作
    await googleArt.init_page(url)

    # 获取页面源代码
    html = await googleArt.page.content()
    # print(html)

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find('div', id='metadata-' + url_id).next.find_all('li')
    f = open('扇面名称列表.txt' , "a", encoding='utf-8')
    for index, li in enumerate(lis):
        if index == 0:
            # 创建txt文件，文件名为
            title = li.text.strip()
            t = time.strftime("%Y%m%d%H%M%S", time.localtime())
            title = title.replace('标题: ', '').replace('\n', '') + str(t) + str('.jpg')

            srcDir = 'C:\\Users\\Administrator\\Downloads\\dezoomify-result.jpg'
            dstDir = 'C:\\Users\\Administrator\\PycharmProjects\\PythonProject\\文心情缘\\' + title
            os.rename(srcDir, dstDir)

            print(title)
            f.write(title + '\n')
        else:
            desc = li.text.strip()
            f.write(desc + '\n')
            print(desc)

    f.write('===================================================' + '\n')
    await googleArt.page.close()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(get_url_title('https://artsandculture.google.com/asset/%E8%83%8C%E9%9D%A2/FgFghicvPD7JUw?childAssetId=7QGJ1IAMe-sFkg'))

