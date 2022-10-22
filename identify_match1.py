import os
from my_custom_ocr import ocr
import numpy as np
from PIL import Image
from glob import glob
import cv2 as cv


def single_pic_proc(image_file):
    image = np.array(Image.open(image_file).convert('RGB'))
    h, w = image.shape[:2]
    if h > w:
        image = cv.rotate(image, cv.ROTATE_90_COUNTERCLOCKWISE)
    h, w = image.shape[:2]
    h_c, w_c = int(h / 3), int(w / 2)
    img_ROI = image[0:h_c, w_c:w]
    result, image_framed = ocr(img_ROI)
    return result, image_framed

# 读取txt文件每一行的内容，并存储在列表中
file = open('src.txt')
res_file = open("result.txt", 'w+')

num_date_checknum_all = []
for line in file.readlines():
    curLine = line.strip().split("  ")
    num_date_checknum_all.append(curLine[0:3])

def add_to_file(nums):
    str = ''
    for i in range(len(nums)):
        str += nums[i]
        if i < len(nums) - 1:
            str += '  '
    res_file.write(str + '\n')

def final_match():
    file1 = open('src.txt')
    res_file1 = open("result.txt")
    ans = file1.readlines()
    results = res_file1.readlines()
    # print(ans)  #测试用的
    # print(results)

    all_true = 0  # 最后成功匹配的数字个数
    all_digit = 0  # 总的数字个数
    for i in range(len(ans)):
        print('第' + str(i + 1) + '组')
        print('    原始数据：' + ans[i])
        print('    识别数据：' + results[i])

        an = ans[i].split('  ')
        res = results[i].split('  ')

        single_true = 0
        single_digit = 0
        for j in range(len(an)):
            mn = min(len(an[j]), len(res[j]))
            single_digit += len(res[j])
            for k in range(0, mn):
                if an[j][k] != '\n' and an[j][k] == res[j][k]:
                    single_true += 1

        print('字符数：' + str(single_digit - 1) + ', 正确数: ' + str(single_true) + '\n')
        all_true += single_true
        all_digit += single_digit - 1

    print('总字符数为：' + str(all_digit) + ', 正确字符数为：' + str(all_true) + ', 最终正确率为：' + str(all_true / all_digit))

if __name__ == '__main__':
    image_files = glob('./test_images/*.*')  #获取文件 test_images 目录中的所有图片文件 这是一个图片路径数组
    for i in range(len(image_files)):    #将文件名的格式统一化
        image_files[i] = image_files[i].replace('\\', '/')
    print(image_files)
    image_files.sort(key=lambda x: x.split('/')[-1].split('.')[0])
    print(image_files)
    result_dir = 'test_result'
    index = 0
    # 正确张数统计
    right_counts = 0
    # 准确个数统计
    accuracy_counts = 0
    for image_file in image_files:
        result, image_framed = single_pic_proc(image_file)   #result 中存储的是图片中区域的坐标和相应区块中的识别结果， image_framed 是对图片区域进行标记后的图片
        nums = [' '] * 3
        for i in range(len(result)):
            if len(result[i]) < 2:
                continue
            sgn = False
            has_num = False
            t = result[i][1]
            if '代' in t or '号' in t or '期' in t or '日' in t:
                sgn = True

            if sgn:       #为了防止前面的文字标志和后面的数字分开  所以要将它们分开
                for k in t:
                    if k.isdigit():
                        has_num = True
                if not has_num:
                    t += result[i + 1][1]
                #print(t)

                num = ''       #获取出里面的有效数字
                st = 0
                ed = 0
                for j in range(len(t)):
                    if t[j].isdigit():
                        st = j
                        break
                for j in range(len(t) - 1, -1, -1):
                    if t[j].isdigit():
                        ed = j
                        break
                for j in range(st, ed + 1):
                    if t[j].isdigit():
                        num += t[j]
                    if t[j].encode("utf-8").isalpha():   #encode("utf-8") 是为了不将中文也算作英文字符
                        num += '3'
                #print(num)  # 输出提取到的相应的数字
                # for c in t:    //这样会把中间为字母的数据缩短，不便于判别
                #     if c.isdigit():
                #         num += c
                if '代' in t:
                    nums[0] = num
                if '号' in t:
                    nums[1] = num
                if '期' in t or '日' in t:
                    nums[2] = num
        #print(nums)
        if len(nums) == 3:
            add_to_file(nums)
        index = index + 1
        print(image_file + '  处理完成')
        # cv.imshow('The', image_framed)
        # cv.waitKey(0)
    file.close()
    res_file.close()
    #调用校对函数
    final_match()



