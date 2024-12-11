import os
import time
import shutil

time_str = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

r_path = r'/home/huang.biao/ClassyVision/runs/detect/exe_20240511212524/cache'


def remove_file(path, remove_list=[]):
    if os.path.exists(path):
        for i in os.listdir(path):
            if i not in remove_list:
                print(f'删除: {os.path.join(path, i)}')
                os.remove(os.path.join(path, i))


lst = ['296', '398', '420', '703', '868']
lst = [str(i) + '.jpg' for i in lst]
# remove_file(r_path, lst)
file_list = set([i.split('.')[0] for i in os.listdir(r_path)])
for file in file_list:
    img_path = os.path.abspath(os.path.join(r_path, f'{file}.jpg'))
    move_img_path = os.path.join('./dingwei/images', f'{file}_{time_str}.jpg')
    txt_path = os.path.abspath(os.path.join(r_path, f'{file}.txt'))
    move_txt_path = os.path.join('./dingwei/labels', f'{file}_{time_str}.txt')
    if os.path.exists(img_path) and os.path.exists(txt_path):
        print('Moving', img_path, move_img_path)
        shutil.move(img_path, move_img_path)
        print('Moving', txt_path, move_txt_path)
        shutil.move(txt_path, move_txt_path)
