import asyncio
import os
import time

from bs4 import BeautifulSoup
from pyppeteer_stealth import stealth  # 模拟浏览器指纹， 避免网站检测
from pyppeteer import launcher, launch

# launcher.DEFAULT_ARGS.remove("--enable-automation")  # 取消自动设置默认参数， 避免网站检测


class LoginSimulator:
    def __init__(self):
        self.browser = None
        self.page = None
        self.agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/114.0.0.0 " \
                     "Safari/537.36 "  # RandomAgent.gen_agent() 随机生成User-Agent
        self.proxies = None  # RandomProxies.gen_proxies() 随机生成proxies

    async def init_browser(self, config=None):
        self.browser = await launch(headless=False, dumpio=True, autoClose=False, userDataDir='F:\\temp',
                               args=['--no-sandbox', '--window-size=1920,1080', '--disable-infobars', ])  # 进入有头模式

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
        await self.page.waitFor(1000)

    async def init_second_page(self, url):
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
        await self.page.waitFor(1000)

    async def send_account(self, url, uncss, submitcss):
        # 清空输入框
        await self.page.evaluate(f'''document.querySelector("{uncss}").value=""''')
        # 输入账号密码
        await self.page.type(uncss, url)
        # 等待输入结束后点击确认登录
        await self.page.waitFor(1000)
        await self.page.click(submitcss)
        await self.page.waitFor(1000)


def get_url_id(url):
    ahead = url.split('?')[0]
    subs = ahead.split('/')
    return subs[len(subs) - 1]

async def dezoomify_page_download(url):
    Dezoomify = LoginSimulator()
    target_url = "https://dezoomify.ophir.dev/"
    uncss = "input[id='url']"  # 输入框
    submitcss = "input[class='button']"  # 提交

    await Dezoomify.init_browser()
    # 跳到 Dezoomify
    await Dezoomify.init_page(target_url)

    # 验证网页是否在限定时间内跳转到目标网页,检查跳转的网页是否有指定的模块
    await Dezoomify.page.waitForSelector("input[id='url']")
    # 输入解析地址
    await Dezoomify.send_account(url=url, uncss=uncss, submitcss=submitcss)

    Dezoomify.page.waitFor(2000)

    # 等待下载按钮弹出
    download_btn = await Dezoomify.page.waitForSelector("a[class='button']")
    if download_btn:
        time.sleep(2)
        await Dezoomify.page.click("a[class='button']")
        time.sleep(2)

        # 打开谷歌艺术的页面，获取标题等数据
        await Dezoomify.init_second_page(url)
        # 获取页面源代码
        html = await Dezoomify.page.content()
        # print(html)

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        url_id = get_url_id(url)
        lis = soup.find('div', id='metadata-' + url_id).next.find_all('li')
        f = open('扇面名称列表.txt', "a", encoding='utf-8')
        for index, li in enumerate(lis):
            if index == 0:
                # 创建txt文件，文件名为
                title = li.text.strip()
                t = time.strftime("%Y%m%d%H%M%S", time.localtime())
                title = title.replace('标题: ', '').replace('\n', '') + str(t) + str('.jpg')

                # 重命名文件
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
        await Dezoomify.browser.close()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(dezoomify_page_download('https://artsandculture.google.com/asset/%E8%83%8C%E9%9D%A2/FgFghicvPD7JUw?childAssetId=7QGJ1IAMe-sFkg'))

