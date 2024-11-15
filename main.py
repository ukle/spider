from bs4 import BeautifulSoup
import requests

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
        title = link.next.get('alt')
        print(title)
        href = 'https://www.hnmuseum.com' + link.get('href')

        print(href)
        # item = requests.get(href)

        # https://www.hnmuseum.com/gallery/node/9853/1
    # 提取网页标题
    title = soup.title.text
    print(title)


else:
    print("Failed to retrieve the webpage")
