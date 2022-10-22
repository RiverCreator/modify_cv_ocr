# -*- coding:utf-8 -*-

import os
from glob import glob
shuzi=[]
path = '/Users/apple/Desktop/OCR'

path_list = os.listdir(path)
for filename in image_files:
    f = open(os.path.join(path, filename), 'rb')
