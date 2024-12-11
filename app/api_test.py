'''
Description: 
Author: beallhuang
Date: 2024-04-12 15:39:05
LastEditTime: 2024-05-07 15:23:59
LastEditors: beallhuang
'''
# -*- coding: utf-8 -*-
"""
@File    : api_test.py
@Time    : 2023/12/22 18:42
@Author  : beall
@Email   : beallhuang@163.com
@Software: PyCharm
"""
import json
import sys
import requests
import asyncio
import pandas as pd
import time
# from retry import retry
import aiohttp
from multiprocessing import Pool, Manager, cpu_count, Process
# from base_function.connect_database import ImpalaConnect
# from base_function.thread_api import count_time
from loguru import logger


def detect_price_batch():
    # df = ImpalaConnect().read_sql('''
    # select *, uuid() as uuid from  dc_ods.pic_price_belle
    # where 1=1 
    # and create_time between '2024-04-29 00:00:00' and '2024-04-29 23:59:59'
    # -- and price is not null
    # -- and partition_date = 20240412
    # order by uuid limit 1000

    # ''')
    df = pd.read_excel('/home/huang.biao/ClassyVision/ocr测验数据20221213/test_ocr.xlsx', sheet_name='test_ocr')
    df = df[df['fiter'] == 0][2000:]
    img_col = [i for i in df.columns if '图片' in i or 'img' in i][0]
    url_list = [i.replace('_430x430q90.jpg', '_430x430q90.jpg') for i in df[img_col]]
    url = f'http://127.0.0.1:7001/detect_price'
    web = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps({'url': url_list}))
    if web.status_code == 200:
        print(web.json())

# @retry(tries=3, delay=0.1)
async def async_request(arg: str, sem: asyncio.Semaphore):
    async with aiohttp.ClientSession() as session:
        async with sem:
            async with session.get(arg, timeout=None) as response:
                res = await response.text()
                return res


async def main(*keywords):
    task_list = []
    sem = asyncio.Semaphore(50)
    for url in keywords[0]:
        task = asyncio.create_task(async_request(url, sem))
        task_list.append(task)
    done, pending = await asyncio.wait(task_list, timeout=None)
    # 得到执行结果
    for done_task in done:
        res = json.loads(done_task.result().strip())
        if res['msg']:
            keywords[1][res['msg']['url']] = res['msg']['price']


def do(*keywords):
    asyncio.run(main(*keywords))



def detect_price_batch_async():
    # df = ImpalaConnect().read_sql('''
    # select nid
    # , price
    # , null as test_price  
    # , view_price
    # , img                            
    # from  dc_ods.pic_price_belle
    # where 1=1 
    # and create_time between '2024-04-29 00:00:00' and '2024-04-29 23:59:59'
    # -- and partition_date = 20240412
    # -- order by uuid() limit 100
                                  
    # ''')
    df = pd.read_csv('test_ocr_raw.csv')[:100]
    df['view_price'] = df['view_price'].astype('str')
    start_time = time.time()
    img_col = [i for i in df.columns if '图片' in i or 'img' in i][0]
    # df[img_col] = df[img_col].apply(lambda x: 'https://inner-oss.bellecdn.com/files/analy/' + '/'.join(x.split('/')[-2:]).replace('_430x430q90.jpg', ''))
    url_list = [f"http://127.0.0.1:7001/detect_price?url={i}&raw_price={v}" if len(v.strip()) > 0
                else f"http://127.0.0.1:7001/detect_price?url={i}" for i, v in zip(df[img_col], df['view_price'])]
    result_dct = {}
    do(url_list, result_dct)

    df['test_price'] = df['img'].map(result_dct)
    df['fiter'] = [f'=IFERROR(IF(ABS(INT(B{i + 2}) - INT(C{i + 2})) < 2, 1, 0), 1)' for i in range(df.shape[0])]
    df.to_csv('test_ocr.csv', index=False)
    logger.info(f'任务完成, 总耗时: {time.time() - start_time}s')
    


if __name__ == '__main__':
    detect_price_batch()
    # detect_price_batch_async()





