# -*- coding: utf-8 -*-
"""
@File    : app.py.py
@Time    : 2023/12/22 17:27
@Author  : beall
@Email   : beallhuang@163.com
@Software: PyCharm
"""
import sys
sys.path.append(r'../../ClassyVision')
import json
import time
from fastapi import FastAPI
from detect_single import detect
from detect_s import detect_s_single as detect_s
from bianhuan_single import bianhuan

app = FastAPI()



@app.get('/detect_price')
def detect_price(url, raw_price=None):
    try:
        assert url is not None, "url is None"
        t0 = time.time()

        # 定位、切割
        img = detect(url)
        # 图像变换
        # img = bianhuan(img)
        # 识别
        price = detect_s(img)

        if raw_price:
            try:
                raw_price = float(raw_price)

                if 0.35 * raw_price <= price/10 <= 1.1 * raw_price:
                    price = price/10
                elif 0.35 * raw_price <= price/100 <= 1.1 * raw_price:
                    price = price/100
            except Exception as e:
                pass

    except Exception as e:
        return {'code': 400,
                'msg': {},
                'error': str(e)}
    else:
        return {'code': 200,
                'msg': {
                    'total_time': f"{round((time.time() - t0), 2)} s",
                    'price': str(price),
                    'raw_price': str(raw_price),
                    'url': url},
                'error': None}


@app.get('/')
def root():
    return {'code': 200, 'msg': '请访问 /detect_price?url=图片url 获取价格!&raw_price=页面价'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app="app_single_image:app", host="0.0.0.0", port=7001, workers=3)
