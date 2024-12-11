import requests
import PIL.Image as img
import threading
import queue
import os
import time
import re

headers = {
    # 'authority': 'img.alicdn.com',
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


class ThreadApi(object):
    def __init__(self, item_list, func, threadNum=5, queue_order=1):
        """
        :param item_list: 并发对象列表
        :param func: 工作函数对象
        :param threadNum: 并发数，默认 5
        :param queue_order: 1 先进先出; 0 后进先出, 默认为1
        """
        self.item_list = item_list
        self.func = func
        self.queue_order = queue_order
        if queue_order:
            self.q = queue.Queue()  # 先进先出
        else:
            self.q = queue.LifoQueue()  # 后进先出
        self.threadNum = threadNum
        self.lock = threading.Lock()

    def worker(self):
        while not self.q.empty():
            try:
                item = self.q.get_nowait()  # 获得任务
                # with self.lock:
                self.func(item)
            except Exception as e:
                print(e)

    def main(self):
        threads = []
        for task in self.item_list:
            self.q.put_nowait(task)
        for i in range(self.threadNum):
            thread = threading.Thread(target=self.worker)
            thread.setDaemon(True)  # 设置守护进程
            thread.start()
            threads.append(thread)
        for thread in threads:  # 线程阻塞
            thread.join()


def download_image(img_url, quality=18):
    if img_url[2]:
        print(f'下载图片 {img_url[2]}')
        suffix = re.sub('/?.*=.*', '', img_url[2]).split(".")[-1]
        suffix = suffix if suffix else 'jpg'
        img_path = f'{img_url[0]}/{img_url[1]}.{suffix}'
        url = 'https:' + img_url[2] if 'http' not in img_url[2] else img_url[2]
        for _ in range(20):
            r = requests.get(url, headers=headers, stream=True)
            if r.status_code == 200:
                open(img_path, 'wb').write(r.content)  # 将内容写入图片
                # pic = img.open(img_path)
                # pic = pic.resize((800, 800))  # 设置大小
                # pic = pic.convert('RGB')
                # if isinstance(quality, int):
                #     pic.save(img_path, quality=quality)  # quality 压缩图片质量大小，默认75
                # else:
                #     pic.save(img_path)
                # pic.close()
                break
            else:
                pass
            del r


if __name__ == '__main__':
    def work(url):
        requests.get(url)


    url_list = ['http://www.baidu.com' for i in range(100)]
    thread = ThreadApi(url_list, work, threadNum=10)
    thread.main()
