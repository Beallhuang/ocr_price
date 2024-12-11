# -*- coding: utf-8 -*-
"""
@File    : main.py
@Time    : 2024/1/23 1:20
@Author  : beall
@Email   : beallhuang@163.com
@Software: PyCharm
"""
import json
import requests
from paddleocr import PaddleOCR
from utils.parameters import opt2, a_path
import os
import cv2
import time
# import easyocr
from io import BufferedReader, BytesIO
import re
import numpy as np

opt = opt2()
# reader = easyocr.Reader(['en'], gpu=True)
reader = PaddleOCR(lang='en', cls=False, use_angle_cls=False, use_gpu=False)
source, save_result = opt.source, opt.save_result
price_txt_path = os.path.join(a_path.root_path, a_path.project, a_path.name, 'price.txt')


def detect_s():
    for i in os.listdir(source):
        if i.endswith(('jpg', 'jpeg', 'png', 'gif')):
            start_time = time.time()
            try:
                # result = reader.readtext(os.path.abspath(os.path.join(source, i)), detail=0,
                #                          allowlist='0123456789.', batch_size=20)
                # price = [float(i) for i in re.findall(r'[0-9\.]+', '\n'.join(result))]
                result = reader.ocr(os.path.abspath(os.path.join(source, i)), det=False, cls=False)
                price = [float(re.search(r'[0-9\.]+', i[0][0])[0]) for i in result]
                price = max(price)
            except Exception as e:
                price = None
            print(i, price, f"total time: {round(time.time() - start_time, 2)}s")
            if save_result:
                with open(price_txt_path, 'a') as f:
                    f.write(str(i).split('.')[0] + '\t' + str(price) + '\n')


def detect_s_single(img):
    start_time = time.time()
    try:
        # result = reader.readtext(img, detail=0, allowlist='0123456789.')
        # price = [float(i) for i in re.findall(r'[0-9\.]+', '\n'.join(result))]
        result = reader.ocr(img, det=False, cls=False)
        price = [float(re.search(r'[0-9\.]+', i[0][0])[0]) for i in result]
        price = max(price)
    except Exception as e:
        price = None
    print(price, f"total time: {round(time.time() - start_time, 2)}s")
    return price


if __name__ == '__main__':
    import re
    for i in range(0, 999):
        try:
            start_time = time.time()
            img = cv2.imread(rf'/home/huang.biao/ClassyVision/runs/detect/exe_20240511185817/images/{i}.jpg')
            # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换颜色表示顺序
            # img = np.array(img)
            result = reader.ocr(img, det=False, cls=False)
            price = max([float(re.search(r'[0-9\.]+', i[0][0])[0]) for i in result])
            print(price, f"total time: {round(time.time() - start_time, 2)}s")
        except Exception as e:
            print(e)
