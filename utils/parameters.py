r'''
Author: beallhuang beallhuang@163.com
Date: 2023-12-15 15:08:32
LastEditors: beallhuang beallhuang@163.com
LastEditTime: 2023-12-15 16:19:23
FilePath: \ClassyVision\utils\parameters.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import os
import time


class a_path():
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    time_str = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    name = f'exe_{time_str}'
    project = rf'runs/detect'
    images_path = f'{project}/{name}/images/'
    get_path = f'{project}/{name}/cache/'
    labels_path = f'{project}/{name}/labels/'
    price_path = f'{project}/{name}/price/'


class opt(object):
    def __init__(self):
        self.source = a_path.get_path
        self.agnostic_nms = False
        self.augment = False
        self.classes = None
        self.conf_thres = 0.05 # raw conf_thres=0.35
        self.device = '0' # raw device='0'
        self.exist_ok = False
        self.img_size = 384 # raw img_size=384
        self.iou_thres = 0.25 # raw iou_thres=0.25
        self.name = a_path.name
        self.project = a_path.project
        self.save_conf = False
        self.save_img = True
        self.view_img = False
        self.save_txt = True
        # self.weights = rf'{a_path.root_path}/weights/dingwei.pt'
        self.weights = rf'{a_path.root_path}/runs/train/exp2/weights/last.pt'

    def list_all_member(self):
        for name, value in vars(self).items():
            print('%s=%s' % (name, value))


class opt2(object):
    def __init__(self):
        self.source = a_path.images_path
        self.agnostic_nms = False
        self.augment = False
        self.classes = None
        self.conf_thres = 0.35
        self.device = '0'
        self.exist_ok = False
        self.img_size = 384
        self.iou_thres = 0.45
        self.name = a_path.name
        self.project = a_path.project
        self.save_conf = False
        self.save_txt = False
        self.save_result = True
        self.view_img = False
        self.weights = rf'{a_path.root_path}/weights/shibie.pt'

    def list_all_member(self):
        for name, value in vars(self).items():
            print('%s=%s' % (name, value))
