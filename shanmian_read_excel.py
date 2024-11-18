import openpyxl

from shanmian_download import file_downloand


def read_xlsx_excel(url, sheet_name):
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
        # 定义表格存储每一行数据
        title = row[0].value
        image = row[1].value
        if image is not None:
            file_downloand(image, title + ".jpg")


if __name__ == '__main__':
    read_xlsx_excel(url='.\扇面.xlsx', sheet_name='Sheet')