import os
from ocr import ocr
import time
import shutil
import numpy as np
from PIL import Image
from glob import glob
import cv2
import re


def single_pic_proc(image_file):
    # image = cv2.imread(image_file)
    image = np.array(Image.open(image_file).convert('RGB'))
    # image = np.array(image)
    result, image_framed = ocr(image)
    return result,image_framed



if __name__ == '__main__':
    image_files = glob('./test_images/*.*')
    result_dir = './test_result'
    for image_file in (image_files):
        t = time.time()
        result, image_framed = single_pic_proc(image_file)
        output_file = os.path.join(result_dir, image_file.split('/')[-1])
        txt_file = os.path.join(result_dir, image_file.split('/')[-1].split('.')[0]+'.txt')
        print(txt_file)
        txt_f = open(txt_file, 'w')
        cv2.imshow("result",image_framed)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # Image.fromarray(image_framed).save(output_file)
        shuzi=[[] for i in range(len(result))]
        for key in result:

            string = result[key][1]
            store=re.findall(r"\d+\.?\d*", string)
            if(len(store)!=0):
                txt_f.write(store[0]+'\n')
                shuzi.append(store[0])
                print(store[0])
        txt_f.close()
    compare = []
    with open('1.txt', 'r') as f:
        for line in f:
            compare.append(list(line.strip('\n').split('  ')))

