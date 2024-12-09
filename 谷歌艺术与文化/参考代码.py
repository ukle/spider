import asyncio
import random
import numpy as np
import requests
import cv2
from io import BytesIO
from PIL import Image
from pyppeteer_stealth import stealth  # 模拟浏览器指纹， 避免网站检测
from pyppeteer import launcher, launch

launcher.DEFAULT_ARGS.remove("--enable-automation")  # 取消自动设置默认参数， 避免网站检测


class LoginSimulator:
    def __init__(self):
        self.browser = None
        self.page = None
        self.agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/114.0.0.0 " \
                     "Safari/537.36 "  # RandomAgent.gen_agent() 随机生成User-Agent
        self.proxies = None  # RandomProxies.gen_proxies() 随机生成proxies

    async def init_broswer(self, config=None):
        self.browser = await launch(headless=False, dumpio=True, autoClose=False,
                           args=['--no-sandbox', '--window-size=1920,1080', '--disable-infobars'])

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
        await self.page.setViewport({'width': 1100, "height": 768})  # 设置窗口大小,部分网页会检测窗口大小
        await self.page.goto(url)

    async def send_account(self, username, password, uncss, pwcss, submitcss, login_by_pw_css=None):
        if login_by_pw_css:
            # 点击元素， 选择密码登录
            await self.page.click(login_by_pw_css)
        # 清空输入框
        await self.page.evaluate(f'''document.querySelector("{uncss}").value=""''')
        await self.page.evaluate(f'''document.querySelector("{pwcss}").value=""''')
        # 输入账号密码
        await self.page.type(uncss, username)
        await self.page.type(pwcss, password)
        # 等待输入结束后点击确认登录
        await self.page.waitFor(1000)
        await self.page.click(submitcss)
        await self.page.waitFor(1000)

    async def save_verify_image(self, bgcss, blockcss, block_image_path="block_image.png",
                                bg_image_path="bg_image.png"):
        # 获取验证码图片和滑块图片的网址
        bg_src = await self.page.Jeval(bgcss, "node => node.getAttribute('src')")
        block_src = await self.page.Jeval(blockcss, "node => node.getAttribute('src')")
        # 保存图片
        Image.open(BytesIO(requests.get(block_src).content)).save(block_image_path)
        Image.open(BytesIO(requests.get(bg_src).content)).save(bg_image_path)

    def denosing_image(self, image_file):
        """
        usage: 去除滑块的黑边
        :param image_file:  block image file path
        :return:
        """
        print("将滑块图片边缘去噪...")
        image = cv2.imread(image_file, 1)
        # 去噪：中值滤波，去除黑色边际可能含有的噪声干扰
        img = cv2.medianBlur(image, 5)
        # 阈值化图片
        _, binary_img = cv2.threshold(img, 15, 255, cv2.THRESH_BINARY)
        # 将阈值化后的图片转为灰度图像 BGR to gray
        binary_img = cv2.cvtColor(binary_img, cv2.COLOR_BGR2GRAY)
        x, y = binary_img.shape
        edges_y = []
        edges_x = []
        for i in range(x):
            for j in range(y):
                if binary_img[i][j] == 255:
                    edges_y.append(j)
                    edges_x.append(i)
        left = min(edges_x)
        right = max(edges_x)
        width = right - left
        bottom = min(edges_y)
        top = max(edges_y)
        height = top - bottom
        pre1_picture = image[left:left + width, bottom:bottom + height]
        # cv2.imwrite("./block_after.png", pre1_picture) # 保存去除黑边后的图片
        return pre1_picture

    def _dichotomy(self, res):
        """
        二分法获取最相似的点来求取distance
        :param res:
        :return:
        """
        run = 1
        L = 0
        R = 1
        loc = []
        while run < 20:
            run += 1
            threshold = (R + L) / 2
            if threshold < 0:
                raise ValueError("threshold can't be a negative")
            loc = np.where(res >= threshold)
            if len(loc[1]) > 1:
                L += (R - L) / 2
            elif len(loc[1]) == 1:
                break
            elif len(loc[1]) < 1:
                R -= (R - L) / 2
        return loc[1][0]

    async def match_block_with_bg(self, bg_image_path, block_image_path):
        """
        usage: 匹配滑块验证码缺口所在位置
        bg_image_path: 背景图片路径
        block_image_path: 滑块图片路径
        cv2.matchTemplate(img, template, method)
            参数一是需要匹配的图像，参数二是匹配图像的模板，参数三是进行匹配的方法，有下面的6种
            TM_SQDIFF：计算平方不同，计算出来的值越小，越相关
            TM_CCORR：计算相关性，计算出来的值越大，越相关
            TM_CCOEFF：计算相关系数，计算出来的值越大，越相关
            TM_SQDIFF_NORMED：计算归一化平方不同，计算出来的值越接近0，越相关
            TM_CCORR_NORMED：计算归一化相关性，计算出来的值越接近1，越相关
            TM_CCOEFF_NORMED：计算归一化相关系数，计算出来的值越接近1，越相关
            返回的结果是一个灰度图像，每一个像素值表示了此区域与模板的匹配程度
        """
        gray_bg_image = cv2.imread(bg_image_path, 0)
        denosing_block_image_data = self.denosing_image(block_image_path)  # 将滑块去噪去黑边
        gray_block_image = cv2.cvtColor(denosing_block_image_data, cv2.COLOR_BGR2GRAY)
        # 将滑块颜色加深，缺口通常是加了20左右的灰色阴影
        for i in range(len(gray_block_image)):
            for j in range(len(gray_block_image[0])):
                gray_block_image[i][j] -= 20
        result_image = cv2.matchTemplate(gray_bg_image, gray_block_image, cv2.TM_CCOEFF_NORMED)

        # 匹配最相似区域方法1：二分法
        distance = self._dichotomy(result_image)

        # 匹配最相似区域方法2：cv2.minMaxLoc()
        # minl最小相似区域，maxl 最大相似区域
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_image)  # 返回4个值：最小相似值，最大相似值， 最小相似区域， 最大相似区域
        (startx, starty) = max_loc
        # 以最大相似区域为起点坐标，在背景图片上按滑块大小绘出相似区域
        cv2.rectangle(gray_bg_image, (startx, starty),
                      (startx + gray_block_image.shape[0], startx + gray_block_image.shape[1]),
                      (255, 0, 0), 2)
        # cv2.imshow("Result", img_gray) # show 绘制了相似区域的背景图片，按0结束显示继续运行
        # cv2.waitKey(0)
        cv2.imwrite("./result_bg.png", gray_bg_image)  # 保存绘制好的结果图
        distance1 = startx
        print(f"distance: {distance}, {distance1}")
        return distance

    def get_tracks(self, distance, seconds, easse_func):
        """
        模拟加速过程获得多段路径
        :param distance:
        :param seconds:
        :param easse_func:
        :return:
        """
        print("模拟变速滑动过程，获得多段路径。")
        distance += 20
        tracks = [0]
        offsets = [0]
        for t in np.arange(0.0, seconds, 0.1):
            ease = easse_func
            offset = round(ease(t / seconds) * distance)  # 四舍五入
            tracks.append(offset - offsets[-1])
            offsets.append(offset)
        tracks.extend([-3, -2, -3, -2, -2, -2, -2, -1, -1, -1, -1])
        return tracks

    async def slider2gap(self, distance, block_pat, zoom, timeout=5000):
        url = self.page.url  # 保存当前网址，用于判断是否验证成功
        print("开始滑动...")
        await self.page.waitFor(1000)
        tracks = self.get_tracks((distance + 7) * zoom, random.randint(2, 4), self.change_speed)
        # await self.page.hover(block_pat)
        # 获取滑块的初始位置
        js = '''() =>{
            return {
             x: document.querySelector("%s").getBoundingClientRect().x,
             y: document.querySelector("%s").getBoundingClientRect().y,
             width: document.querySelector("%s").getBoundingClientRect().width,
             height: document.querySelector("%s").getBoundingClientRect().height
             }}
            ''' % (block_pat, block_pat, block_pat, block_pat)
        btn_position = await self.page.evaluate(js)
        x = btn_position['x'] + btn_position['width'] / 2
        y = btn_position['y'] + btn_position['height'] / 2

        await self.page.mouse.move(x, y)
        await self.page.mouse.down()
        dist = 0
        for d in tracks:
            dist += d
            await self.page.mouse.move(x + dist, y)
            await self.page.waitFor(random.randint(100, 500))
        await self.page.mouse.up()
        await self.page.waitFor(timeout)
        # await self.page.reload()
        # await self.page.waitFor(1000)
        current_url = self.page.url
        if current_url == url:
            print("fail...")
            return False
        else:
            print("Success")
            return True

    def change_speed(self, x):
        # 滑动速度曲线
        return 1 - pow(1 - x, 4)

    async def request_file_after_login(self, req_url):
        await self.page.goto(req_url)
        content = await self.page.content()
        print(content)
        return content


async def main():
    username = "xxxxx"
    password = "xxxxxxxx"
    ZhiHu = LoginSimulator()
    login_url = "https://www.zhihu.com/signin?next=%2F"
    login_by_pw_css = "div[class='SignFlow-tab']"  # 选择密码登录模块
    uncss = "input[name='username']"  # 账号输入框
    pwcss = "input[name='password']"  # 密码输入框
    submitcss = "button[type='submit']"  # 确认登录框
    bgcss = '.yidun_bg-img'  # 背景图片所在的标签css索引路径
    blockcss = '.yidun_jigsaw'  # 滑块所在标签的索引路径
    bg_image_path = "bg_image.png"
    block_image_path = "block_image.png"
    target_url = "https://www.zhihu.com/people/xxxxxxx"  # 需要登录才能浏览的网页

    await ZhiHu.init_broswer()
    # 初始化登录页面，设置一些反反爬操作
    await ZhiHu.init_page(login_url)
    # 验证网页是否在限定时间内跳转到目标网页,检查跳转的网页是否有指定的模块
    await ZhiHu.page.waitForSelector("div[class='SignFlow-tabs']")
    # 输入账号密码，并点击确认登录
    await ZhiHu.send_account(username=username, password=password, login_by_pw_css=login_by_pw_css, uncss=uncss,
                             pwcss=pwcss,
                             submitcss=submitcss)
    # 等待验证码弹出
    verify_img = await ZhiHu.page.waitForSelector(".yidun_bg-img")
    if verify_img:
        # 如果验证失败，刷新验证码重新验证，最多验证5次，超过5次，可能是识别算法不适用
        for i in range(5):
            print(f"=========第 {i} 次=========")
            await ZhiHu.save_verify_image(bgcss=bgcss, blockcss=blockcss)
            distance = await ZhiHu.match_block_with_bg(bg_image_path=bg_image_path, block_image_path=block_image_path)
            res = await ZhiHu.slider2gap(distance, "div.yidun_slider.yidun_slider--hover", 1)
            if res:
                break
        else:
            print("verify fail...")
    await ZhiHu.request_file_after_login(target_url)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

