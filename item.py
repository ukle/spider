from bs4 import BeautifulSoup
import requests

# 发送HTTP请求，获取网页内容
url = "https://www.hnmuseum.com/gallery/node/9853/1"
response = requests.get(url)

# 检查请求是否成功
if response.status_code == 200:
    # 使用BeautifulSoup解析网页内容
    # print(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 提取下一级的地址
    elements = soup.find_all('p')
    for element in elements:
        print(element)
    elements2 = soup.find_all('img')
    for element in elements2:
        print(element)



else:
    print("Failed to retrieve the webpage")
