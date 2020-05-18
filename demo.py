# -*- coding: utf-8 -*-
# @Author: [FENG] <1161634940@qq.com>
# @Date:   2020-04-27 11:25:05
# @Last Modified by:   [FENG] <1161634940@qq.com>
# @Last Modified time: 2020-05-17 15:42:21
# -*- coding: utf-8 -*-

from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import matplotlib.pyplot as plt
import sys, urllib, json
import urllib.request
import urllib.parse
import base64
import csv
url = 'http://apis.baidu.com/idl_baidu/ocridcard/ocridcard'
import pytesseract
from PIL import Image


# 加载图片，将它转换为灰阶，轻度模糊，然后边缘检测。
image = cv2.imread("D:/Python/www/duka/image/demo.jpg")

#转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#高斯滤波
blurred = cv2.GaussianBlur(gray, (3, 3), 0)
#自适应二值化方法
blurred=cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,51,2)
blurred=cv2.copyMakeBorder(blurred,5,5,5,5,cv2.BORDER_CONSTANT,value=(255,255,255))
edged = cv2.Canny(blurred, 10, 100)

thresh = cv2.resize(blurred, (5000, 7000), cv2.INTER_LANCZOS4)
fImage = cv2.resize(image, (5000, 7000), cv2.INTER_LANCZOS4)

ChQImg = cv2.blur(thresh, (50, 50))
ChQImg = cv2.threshold(ChQImg, 20, 225, cv2.THRESH_BINARY)[1]


NumImg=cv2.blur(thresh,(15,15)) # 新的二值化图
NumImg=cv2.threshold(NumImg, 100, 255, cv2.THRESH_BINARY)[1]


kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
NumImg2 = cv2.dilate(thresh, kernel) # 

kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
NumImg2 = cv2.erode(NumImg2, kernel2)

# NumImg2 = cv2.threshold(ChQImg2, 200, 225, cv2.THRESH_BINARY)[1]
NumImg2 = cv2.adaptiveThreshold(NumImg2, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 23, 2)
# ChQImg2 = cv2.threshold(ChQImg2, 200, 225, cv2.THRESH_BINARY)[1]
NumImg2=NumImg2-NumImg
NumImg2=cv2.blur(NumImg2,(5,5))
NumImg2=cv2.threshold(NumImg2,170,255,cv2.THRESH_BINARY)[1]

# 在二值图像中查找轮廓
cnts = cv2.findContours(ChQImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
'''
检测用边缘绘制
cv2.drawContours(paper, cnts[1], -1, (0, 0, 255), 10, lineType=0)
'''
# cnts = cnts[0] if imutils.is_cv2() else cnts[1]
cnts = cnts[1] if imutils.is_cv3() else cnts[0]
questionCnts = []
Answer = []

# cv2.namedWindow("ceshi",0);
# cv2.resizeWindow("ceshi", 480, 640);
# cv2.imshow("ceshi", ChQImg)
# cv2.waitKey(0)

# cv2.imwrite("D:/Python/www/duka/2.jpg",ChQImg)

for c in cnts:
	# 计算轮廓的边界框，然后利用边界框数据计算宽高比
	(x, y, w, h) = cv2.boundingRect(c)
	if ((y>3500 and y<5440) or (y>2110 and y<3140)) and x > 400 and w > 60 and h > 20:
	# if (w > 60 & h > 20)and y>900 and y<2000:
	    M = cv2.moments(c)
	    cX = int(M["m10"] / M["m00"])
	    cY = int(M["m01"] / M["m00"])
	    #绘制中心及其轮廓
	    cv2.drawContours(fImage, c, -1, (0, 0, 255), 5, lineType=0)
	    cv2.circle(fImage, (cX, cY), 7, (255, 255, 255), -1)
	    #保存题目坐标信息
	    Answer.append((cX, cY))


# cv2.namedWindow("ceshi",0);
# cv2.resizeWindow("ceshi", 480, 640);
# cv2.imshow("ceshi", fImage)
# cv2.waitKey(0)
# cv2.imwrite("D:/Python/www/duka/2.jpg",fImage)

xt0=[0,700,1140,1585,2030,2470,2910,3355,3790,4240,4690,5000]
yt0=[2144,2250,2344,2440,2540,2630,2730,2830,2920,3020,3115]

xt1=[0,570,730,880,1025,1175,1445,1600,1745,1900,2050,2330,2470,2620,2780,2930,3090,3230,3390,3540,3700,3880,4030,4180,4335,4490,5000]
yt1=[3500,3620,3740,3865,3975,4140,4300,4400,4530,4645,4800,4960,5080,5200,5310,5440]

#卷子model0判题
def judgey0(y):
    if (y / 5 < 1):
        return  y + 1
    elif y / 5 < 2 and y/5>=1:
        return y % 5 + 25 + 1
    else:
        return y % 5 + 45 + 1

# 获取选项
def judgex(x, y=1):
    letter = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return letter[x%(5*y)-1]

def judge0(x, y, m, n):
    # score = 20
    if n > 4140 and n < 4800:
        if x/5<1 :
            # print(judgey0(y))
            num = judgey0(y)
        elif x/5<2 and x/5>=1:
            # print(judgey0(y)+5)
            num = judgey0(y)+5
        elif x/5<4 and x/5>=2:
            # print(judgey0(y)+10)
            num = judgey0(y)+10
        else:
            # print(judgey0(y)+15)
            num = judgey0(y)+15
    else:
        if x/5<1 :
            # print(judgey0(y))
            num = judgey0(y)
        elif x/5<2 and x/5>=1:
            # print(judgey0(y)+5)
            num = judgey0(y)+5
        elif x/5<3 and x/5>=2:
            # print(judgey0(y)+10)
            num = judgey0(y)+10
        elif x/5<4 and x/5>=3:
            # print(judgey0(y)+15)
            num = judgey0(y)+15
        else:
            # print(judgey0(y)+20)
            num = judgey0(y)+20

    if m > 2050 and m < 3720 and n > 4140 and n < 4800:
        # print(judgex1(x))
        option = judgex(x, 2)
    else:
        # print(judgex0(x))
        option = judgex(x, 1)

    return [num, option]

    
#答案选择输出
# print(len(Answer))
# print(Answer[0])

student = ''
IDAnswer = []
for i in Answer:
    if i[1] > yt0[0] and i[1] < yt0[-1]:
        for j in range(0,len(xt0)-1):
            if i[0]>xt0[j] and i[0]<xt0[j+1]:
                for k in range(0,len(yt0)-1):
                    if i[1]>yt0[k] and i[1]<yt0[k+1]:
                        student = str(k) + student
    else :
        for j in range(0,len(xt1)-1):
            if i[0]>xt1[j] and i[0]<xt1[j+1]:
                for k in range(0,len(yt1)-1):
                    if i[1]>yt1[k] and i[1]<yt1[k+1]:
                        option = judge0(j, k, i[0], i[1])
                        IDAnswer.append(option)

IDAnswer=[]
for i in Answer:
    for j in range(0,len(xt1)-1):
        if i[0]>xt1[j] and i[0]<xt1[j+1]:
            for k in range(0,len(yt1)-1):
                if i[1]>yt1[k] and i[1]<yt1[k+1]:
                	option = judge0(j, k, i[0], i[1])
                	IDAnswer.append(option)


IDAnswer.sort()
newIDAnswer = {'学号':student};
for x in IDAnswer:
    if x[0] <= 60:
        if x[0] not in newIDAnswer:
            newIDAnswer[x[0]] = x[1]
        else :
            newIDAnswer[x[0]] = newIDAnswer[x[0]] + x[1]

print(student)
print(newIDAnswer)

# import csv

# with open('names.csv', 'w') as csvfile:
#     fieldnames = list(newIDAnswer.keys())
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#     writer.writeheader() # 注意有写header操作
#     writer.writerow(newIDAnswer)
#     # writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
#     # writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})