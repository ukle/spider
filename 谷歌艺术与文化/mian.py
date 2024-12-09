import asyncio

import openpyxl

from 谷歌艺术与文化.dezoomify_download import dezoomify_page_download

def get_all_url(url, sheet_name):
    '''
    读取xlsx格式文件
    参数：
        url:文件路径
        sheet_name:表名
    返回：
        data:表格中的数据
    '''
    # 使用openpyxl加载指定路径的Excel文件并得到对应的workbook对象
    workbook = openpyxl.load_workbook(url, data_only=True)
    # 根据指定表名获取表格并得到对应的sheet对象
    sheet = workbook[sheet_name]
    # 遍历表格的每一行
    for row in sheet.rows:
        url = row[0].value
        if url.find('https://') == -1:
            url = 'https://artsandculture.google.com' + url
        # 跳转到每一个url地址，进行下载
        loop = asyncio.new_event_loop()
        loop.run_until_complete(dezoomify_page_download(url))

if __name__ == '__main__':
    # 读取扇面2里面的url数据
    get_all_url(url='.\扇面2.xlsx', sheet_name='Sheet1')
    # url = 'https://artsandculture.google.com/asset/正面/DAHADPrPfYI8gQ?childAssetId\u003dIAHHMz-vk-P1pQ'
    # 跳转到每一个url地址，进行下载
    # loop = asyncio.new_event_loop()
    # loop.run_until_complete(dezoomify_page_download(url))
