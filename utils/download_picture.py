# -*- coding: utf-8 -*-
"""
@File    : download_picture.py.py
@Time    : 2023/12/22 14:53
@Author  : beall
@Email   : beallhuang@163.com
@Software: PyCharm
"""


def download_pic():
    from thread_api import ThreadApi, download_image
    import pandas as pd

    df = pd.read_excel(r"C:\Users\Beall\Downloads\query-impala-182222.xlsx", engine='openpyxl')

    url_list = [(r'D:\study\ClassyVision\data\cache_p', i, v) for i, v in zip(df['nid'], df['img'])]

    thread = ThreadApi(url_list, download_image, threadNum=10)
    thread.main()


def inverse(img=True, txt=True):
    import cv2
    import os

    if img:
        for i in os.listdir(r'D:\study\ClassyVision\data\shibie\images'):
            img = cv2.imread(os.path.join(r'D:\study\ClassyVision\data\shibie\images', i))

            # 计算最大灰度值
            max_value = 255

            # 颜色反转
            img_inverse = max_value - img

            # 保存反转后的图像
            print(os.path.join(r'D:\study\ClassyVision\data\shibie\images',
                               i.split('.')[0] + 'inverse.' + i.split('.')[1]))
            cv2.imwrite(
                os.path.join(r'D:\study\ClassyVision\data\shibie\images',
                             i.split('.')[0] + 'inverse.' + i.split('.')[1]),
                img_inverse)

    if txt:
        for i in os.listdir(r'D:\study\ClassyVision\data\shibie\labels'):
            print(os.path.join(r'D:\study\ClassyVision\data\shibie\labels',
                               i.split('.')[0] + 'inverse.' + i.split('.')[1]))
            with open(os.path.join(r'D:\study\ClassyVision\data\shibie\labels', i), 'r', encoding='utf-8') as fl:
                with open(os.path.join(r'D:\study\ClassyVision\data\shibie\labels',
                                       i.split('.')[0] + 'inverse.' + i.split('.')[1]), 'w') as fw:
                    fw.write(fl.read())

# inverse(txt=True, img=False)
download_pic()