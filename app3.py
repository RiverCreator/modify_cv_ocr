import re

import os
import cv2

from model_post_type import ocr as OCR
from model_postE_invoice import ocr as ocr_E
from model_postM_invoice import ocr as ocr_M
from apphelper.image import union_rbox
from application.invoice_e import invoice_e
from application.invoice_m import invoice_m
import os
import numpy as np

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


# allowed_extension = ['jpg','png','JPG']


def getPhoto():
    path_photo = r'test'  # 所有photo所在的文件夹目录
    #
    files_list = os.listdir(path_photo)  # 得到文件夹下的所有文件名称，存在字符串列表
    return files_list


# 去章处理方法
def remove_stamp(path, file_name):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if (img is None): return False
    B_channel, G_channel, R_channel = cv2.split(img)  # 注意cv2.split()返回通道顺序
    _, RedThresh = cv2.threshold(R_channel, 170, 355, cv2.THRESH_BINARY)
    cv2.imwrite(r'E:\program\opencv\invoice-master\test'.format(file_name), RedThresh)

    return True


def Recognition_invoice(path, file_name):
    '''
    识别发票类别
    :param none:
    :return: 发票类别
    '''
    if (remove_stamp(path, file_name) is False): return 3
    img1 = r'E:\program\opencv\invoice-master\test'.format(file_name)

    img1 = cv2.imread(img1)
    result_type = OCR(img1)
    result_type = union_rbox(result_type, 0.2)

    # print(result_type)

    if len(result_type) > 0:
        N = len(result_type)
        for i in range(N):
            txt = result_type[i]['text'].replace(' ', '')
            txt = txt.replace(' ', '')
            type_1 = re.findall('电子普通', txt)
            type_2 = re.findall('普通发票', txt)
            type_3 = re.findall('专用发票', txt)
            if type_1 == None:
                type_1 = []
            if type_2 == None:
                type_2 = []
            if type_3 == None:
                type_3 = []
        if len(type_1) > 0:
            return 1
        else:
            return 2
    elif len(result_type) == 0:
        return 2


def remove_black(img):
    threshold = 40  # 阈值
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转换为灰度图像

    nrow = gray.shape[0]  # 获取图片尺寸
    ncol = gray.shape[1]
    print(gray.shape)
    colc = gray[:, int(1 / 2 * ncol)]  # 无法区分黑色区域超过一半的情况
    rowc = gray[int(1 / 2 * nrow), :]

    rowflag = np.argwhere(rowc > threshold)
    colflag = np.argwhere(colc > threshold)

    left, bottom, right, top = rowflag[0, 0], colflag[-1, 0], rowflag[-1, 0], colflag[0, 0]
    return img[left:right, top:bottom]
    # cv2.imshow('name', gray[left:right, top:bottom])  # 效果展示
    # cv2.waitKey()


def remove_black2(image):
    img = cv2.medianBlur(image, 5)  # 中值滤波，去除黑色边际中可能含有的噪声干扰
    b = cv2.threshold(img, 40, 255, cv2.THRESH_BINARY)  # 调整裁剪效果
    binary_image = b[1]  # 二值图--具有三通道
    binary_image = cv2.cvtColor(binary_image, cv2.COLOR_BGR2GRAY)
    print(binary_image.shape)  # 改为单通道

    x = binary_image.shape[0]
    print("高度x=", x)
    y = binary_image.shape[1]
    print("宽度y=", y)
    edges_x = []
    edges_y = []
    for i in range(x):
        for j in range(y):
            if binary_image[i][j] == 255:
                edges_x.append(i)
                edges_y.append(j)

    left = min(edges_x)  # 左边界
    right = max(edges_x)  # 右边界
    width = right - left  # 宽度
    bottom = min(edges_y)  # 底部
    top = max(edges_y)  # 顶部
    height = top - bottom  # 高度

    pre1_picture = image[left:left + width, bottom:bottom + height]  # 图片截取
    return pre1_picture


def match_ans(ans_txt, res_txt):
    ans_file = open(ans_txt, mode='r')
    res_file = open(res_txt, mode='r')
    ans = ans_file.readlines()
    res = res_file.readlines()
    print(res)
    all_true = 0
    all_digits = 0
    invoice_right = 0
    for i in range(len(ans)):
        print('第' + str(i + 1) + '组')
        print('  正确数据为：' + ans[i])
        print('  识别数据为：' + res[i])
        ans_ = ans[i].split('  ')
        res_ = res[i].split(' ')
        print(ans_)
        print(res_)
        single_true = 0
        single_digits = 0

        for j in range(len(ans_)):
            mn = min(len(ans_[j]), len(res_[j]))
            single_digits += len(res_[j])
            for k in range(0, mn):
                if ans_[j][k] != '\n' and ans_[j][k] == res_[j][k]:
                    single_true += 1

        print('字符数：' + str(single_digits - 1) + ', 正确数: ' + str(single_true))
        if (single_digits-1 == single_true):
            print("该张发票全对！")
            invoice_right += 1
        all_true += single_true
        all_digits += single_digits - 1
    print('总字符数为：' + str(all_digits) + ', 正确字符数为：' + str(all_true) + ', 最终准确率为：' + str(
        all_true / all_digits))
    print('总发票数为: ' + str(len(ans)) + ', 正确发票数为：' + str(invoice_right) + ', 最终正确率为：' + str(
        invoice_right / len(ans)))


files_list = getPhoto()
upload_path = r"test"
# files_list.remove('.ipynb_checkpoints')
# print(files_list)
files_list.sort(key=lambda x: int(x.split('.')[0]))
# print(files_list)
file_handle = open('result.txt', mode='w+')
for file_name in files_list:
    whole_path = os.path.join(upload_path, file_name)
    # Recognition_invoice1 = Recognition_invoice(whole_path, file_name)
    # if (Recognition_invoice1 is not 3):
    print(whole_path)
    img = cv2.imread(whole_path)
    # img = remove_black2(img)
    h, w = img.shape[:2]
    print(img.shape)
    # img=cv2.resize(img,(w,int(w*0.67)),interpolation=cv2.INTER_CUBIC)
    img = cv2.resize(img, (w, int(w * 0.67)), interpolation=cv2.INTER_NEAREST)
    # img=img[0:int(0.3*h),int(w*0.5):w]
    # cv2.imshow("test",img)
    # cv2.waitKey()
    # if Recognition_invoice1 == 1:
    result = ocr_E(img)
    print("result:", result)
    res = invoice_e(result)
    res = res.res
    # elif Recognition_invoice1 == 2:
    #     result = ocr_M(img)
    #     res = invoice_m(result)
    #     res = res.res
    # else:
    #     res = []
    print(file_name)
    print(res)
    code = res.get('发票代码', "").ljust(13, ' ')
    num = res.get('发票号码', "").ljust(9, ' ')
    time = "".join(list(filter(str.isdigit, res.get('开票日期', ""))))
    checkcode = res.get('校验码', "").ljust(20, ' ')
    print(code + num + time + checkcode)
    # file_handle.writelines([file_name.ljust(20, ' '), code, num,time, '\n'])
    file_handle.writelines([code[0:12] + " " + num, time, '\n'])
file_handle.close()
match_ans("ans.txt", "result.txt")
