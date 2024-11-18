import os  # 导入os库
import urllib  # 导入urllib库

def file_downloand(image_url, file_name):  #######文件下载
    if os.path.exists("文件路径") == False:  # 判断是否存在文件

        # 文件基准路径
        basedir = os.path.abspath(os.path.dirname(__file__))
        # 下载到服务器的地址
        file_path = os.path.join(basedir, './湖南博物馆扇里扇外扇面展')

        try:
            # 如果没有这个path则直接创建
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            urllib.request.urlretrieve(image_url, filename=file_path + "/" + file_name)
            print("成功下载文件")
        except IOError as exception_first:  # 设置抛出异常
            print(1, exception_first)

        except Exception as exception_second:  # 设置抛出异常
            print(2, exception_second)
    else:
        print("文件已经存在！")

if __name__ == '__main__':
    file_downloand('https://www.hnmuseum.com/sites/default/files/2307002.jpg', '居廉 海棠蜜蜂图扇页.jpg')