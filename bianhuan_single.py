import cv2, os
from utils.parameters import a_path


def bianhuan(img=None):
    def access_pixels(img):
        # print(frame.shape)  #shape内包含三个元素：按顺序为高、宽、通道数
        height = img.shape[0]
        weight = img.shape[1]

        a = b = 0
        for row in range(height):
            for col in range(weight):  # 遍历宽
                dd = img.item(row, col)  # 遍历像素点的值
                if dd <= 128:
                    a += 1
                else:
                    b += 1

        # print(a,b)
        for row in range(height):  # 遍历高
            for col in range(weight):
                # 判断黑白像素谁多，如果黑色多则像素翻转
                if a >= b:
                    pv = img[row, col]
                    img[row, col] = 255 - pv  # 全部像素取反，实现一个反向效果
                else:
                    pass
        return img

    def huiduhua(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # ret, img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return img

    try:
        img0 = huiduhua(img)
        img0 = access_pixels(img0)
    except Exception as e:
        return img
    else:
        return img0


if __name__ == '__main__':
    bianhuan()
