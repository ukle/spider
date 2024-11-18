from bs4 import BeautifulSoup
import requests
import asyncio

from dive_into_one_item import dive_into

# 发送HTTP请求，获取网页内容
url = "https://www.hnmuseum.com/zh-hans/gallery/list/9853/11"
response = requests.get(url)

# 检查请求是否成功
if response.status_code == 200:
    # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, 'html.parser')
    # 提取下一级的地址
    links = soup.find_all('a', class_='more_img')
    for link in links:
        href = 'https://www.hnmuseum.com' + link.get('href')
        print(href)
        asyncio.run(dive_into(href))

else:
    print("Failed to retrieve the webpage")
