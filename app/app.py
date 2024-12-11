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
from utils.parameters import a_path
from detect import detect
from detect_s import detect_s
from bianhuan import bianhuan
from utils.thread_api import ThreadApi, download_image
import time
from flask import Flask, request as req, render_template
from gevent import pywsgi
import shutil
import json
import os

os.chdir(a_path.root_path)
app = Flask(__name__, static_folder='..', static_url_path='')


def clear(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        os.mkdir(path)
    else:
        os.mkdir(path)


def l_clear():
    clear(os.path.join(a_path.project, a_path.name))
    clear(a_path.get_path)
    clear(a_path.images_path)
    clear(a_path.labels_path)
    clear(a_path.price_path)


@app.after_request
def disable_caching(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Expires'] = '-1'
    response.headers['Pragma'] = 'no-cache'
    return response


@app.route('/detect_price', methods=['POST'])
def detect_price():
    try:

        img_path = json.loads(req.get_data().decode('utf-8'))["url"]
        start_time = time.time()
        # 每次运行前清空exp文件夹
        l_clear()

        url_list = [(a_path.get_path, i, v) for i, v in enumerate(img_path)]
        thread = ThreadApi(url_list, download_image, threadNum=20)
        thread.main()

        yolo_start_time = time.time()

        # 定位、切割
        detect()
        # 图像变换
        # bianhuan()
        # 识别
        detect_s()
    except Exception as e:
        return json.dumps({'code': 400, 'error': str(e), 'total_time': f"{round((time.time() - start_time), 2)} s", })
    else:
        return json.dumps({
            'code': 200,
            'total_time': f"{round((time.time() - start_time), 2)} s",
            'download_picture_time': f"{round((yolo_start_time - start_time), 2)} s",
            '点击链接查看结果：': f'http://127.0.0.1:7001?random={time.time()}'})


# 定义根路径的路由
@app.route("/")
def index():
    images = []

    # 遍历目录下的文件
    path_list = os.listdir(a_path.get_path)
    path_list = [i for i in path_list if i.lower().endswith(('jpg', 'jpeg', 'png', 'gif'))]
    path_list.sort(key=lambda x: int(x.split('.')[0]))
    for filename in path_list:
        with open(os.path.join(a_path.root_path, a_path.project, a_path.name, 'price.txt'), 'r') as fl:
            price_dct = {}
            for line in fl.readlines():
                if len(line.strip().split('\t')) == 2:
                    price_dct[line.strip().split('\t')[0]] = line.strip().split('\t')[1]
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            images.append(
                {'path': a_path.images_path + filename, 'path_input': a_path.get_path + filename,
                 'name': filename, 'price': price_dct.get(filename.split('.')[0])})

    return render_template("index.html", images=images)


if __name__ == '__main__':
    # app.run(host='127.0.0.1', port=7001, debug=True)

    pywsgi.WSGIServer(('0.0.0.0', 7001), app).serve_forever()
