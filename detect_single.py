import argparse
import time, os
from pathlib import Path
import cv2
import torch
import numpy as np
import torch.backends.cudnn as cudnn
from numpy import random
from utils.parameters import opt, a_path
import requests
from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages, letterbox
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized

# 获取参数信息
opt = opt()

source, weights, view_img, save_img, imgsz, save_txt = opt.source, opt.weights, opt.view_img, opt.save_img, opt.img_size, opt.save_txt
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
    'cache-control': 'max-age=0',
    'if-modified-since': 'Wed, 28 Sep 2022 10:16:17 GMT',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}
# Initialize
set_logging()
# 获取设备
device = select_device(opt.device)
# 如果设备为gpu，使用Float16
half = device.type != 'cpu'  # half precision only supported on CUDA

# Load model
# 加载Float32模型，确保用户设定的输入图片分辨率能整除32(如不能则调整为能整除并返回)
model = attempt_load(weights, map_location=device)  # load FP32 model
stride = int(model.stride.max())  # model stride
imgsz = check_img_size(imgsz, s=stride)  # check img_size
if half:
    model.half()  # to FP16

# Get names and colors
# 获取类别名字
names = model.module.names if hasattr(model, 'module') else model.names
# 设置画框的颜色
colors = [[random.randint(0, 1) for _ in range(3)] for _ in names]
# Run inference
if device.type != 'cpu':
    model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # 进行一次前向推理,测试程序是否正常


def detect(url=None, img_size=imgsz, stride=stride):
    """
    path 图片/视频路径
    img 进行resize+pad之后的图片
    img0 原size图片
    cap 当读取图片时为None，读取视频时为视频源
    """
    if 'http' in url:
        response = requests.get(url, headers=headers, timeout=10)
        img_array = np.array(bytearray(response.content), dtype=np.uint8)
        im0s = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    elif isinstance(url, np.ndarray):
        im0s = url
    else:
        im0s = cv2.imread(url)
    assert im0s is not None, 'Image Not Found: ' + url

    # Padded resize
    img = letterbox(im0s, img_size, stride=stride)[0]

    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)

    cap = None
    t0 = time.time()
    img = torch.from_numpy(img).to(device)
    # 图片也设置为Float16
    img = img.half() if half else img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    # 没有batch_size的话则在最前面添加一个轴
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # Inference
    t1 = time_synchronized()
    """
    前向传播 返回pred的shape是(1, num_boxes, 5+num_class)
    h,w为传入网络图片的长和宽，注意dataset在检测时使用了矩形推理，所以这里h不一定等于w
    num_boxes = h/32 * w/32 + h/16 * w/16 + h/8 * w/8
    pred[..., 0:4]为预测框坐标
    预测框坐标为xywh(中心点+宽长)格式
    pred[..., 4]为objectness置信度
    pred[..., 5:-1]为分类结果
    """
    pred = model(img, augment=opt.augment)[0]

    # Apply NMS
    """
    pred:前向传播的输出
    conf_thres:置信度阈值
    iou_thres:iou阈值
    classes:是否只保留特定的类别
    agnostic:进行nms是否也去除不同类别之间的框
    经过nms之后，预测框格式：xywh-->xyxy(左上角右下角)
    pred是一个列表list[torch.tensor]，长度为batch_size
    每一个torch.tensor的shape为(num_boxes, 6),内容为box+conf+cls
    """
    pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, classes=opt.classes, agnostic=opt.agnostic_nms)
    t2 = time_synchronized()

    # 对每一张图片作处理
    for i, det in enumerate(pred):  # detections per image
        # 如果输入源是webcam，则batch_size不为1，取出dataset中的一张图片
        p, s, im0 = url, '', im0s

        # 设置打印信息(图片长宽)
        s += '%gx%g ' % img.shape[2:]  # print string
        gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh

        aa = 0
        if len(det):
            # Rescale boxes from img_size to im0 size
            # 调整预测框的坐标：基于resize+pad的图片的坐标-->基于原size图片的坐标
            # 此时坐标格式为xyxy
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

            # Print results
            # 打印检测到的类别数量
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()  # detections per class
                s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
            det = sorted(det, key=lambda d: d[-2], reverse=False)  
                 
            # Write results
            # 保存预测结果
            for *xyxy, conf, cls in reversed(det[-1:]):
                if save_img:  # Write to file
                    # 将xyxy(左上角+右下角)格式转为xywh(中心点+宽长)格式，并除上w，h做归一化，转化为列表再保存
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                    # 在原图上画框
                    aa = 1
                    # print(xywh)
                    line = (cls, *xywh, conf) if opt.save_conf else (cls, *xywh)  # label format
                    sp = im0.shape
                    # 获取坐标
                    left = int((float(xywh[0]) * sp[1]) - (float(xywh[2]) * sp[1] / 2))
                    upper = int((float(xywh[1]) * sp[0]) - (float(xywh[3]) * sp[0] / 2))
                    right = int((float(xywh[0]) * sp[1]) + (float(xywh[2]) * sp[1] / 2))
                    lower = int((float(xywh[1]) * sp[0]) + (float(xywh[3]) * sp[0] / 2))
                    # 裁剪
                    im0 = im0[upper:lower, left:right]

        if save_img & aa == 1:
            if im0.shape[0] > 0:
                print(f'Done. ({time.time() - t0:.3f}s)')
                return im0


if __name__ == '__main__':
    # 打印参数
    # opt.list_all_member()

    detect(url='https://img.alicdn.com/bao/uploaded/i3/2428721558/O1CN01jzv8NA1NNbsQH3Me6_!!2428721558.jpg')
