import cv2, os
from utils.parameters import a_path


def bianhuan():
    def access_pixels(img):
        # print(frame.shape)  #shape内包含三个元素：按顺序为高、宽、通道数
        height = img.shape[0]
        weight = img.shape[1]

        a = b = 0
        for row in range(height):
            for col in range(weight):  # 遍历宽
                dd = img.item(row, col)  # 遍历像素点的值exit
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

    def readname():
        rname = os.listdir(a_path.images_path)
        return rname

    rname = readname()
    for i in rname:
        r_path = a_path.images_path + str(i)
        # print(r_path)
        img = cv2.imread(r_path)
        try:
            img = huiduhua(img)
            img = access_pixels(img)
        except Exception as e:
            pass
        else:
            cv2.imwrite(r_path, img)


if __name__ == '__main__':
    bianhuan()
