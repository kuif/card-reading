# -*- coding: utf-8 -*-
# @Author: [FENG] <1161634940@qq.com>
# @Date:   2020-04-27 11:25:05
# @Last Modified by:   [FENG] <1161634940@qq.com>
# @Last Modified time: 2020-05-17 17:39:30
# -*- coding: utf-8 -*-

import imutils
import cv2
import csv

# 加载图片，将它转换为灰阶，轻度模糊，然后二值化处理。
image = cv2.imread("./image/demo1.jpg")

#转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#高斯滤波
blurred = cv2.GaussianBlur(gray, (3, 3), 0)
#自适应二值化方法
blurred = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,51,2)

#重塑可能用到的图像
thresh = cv2.resize(blurred, (5000, 7000), cv2.INTER_LANCZOS4)
fImage = cv2.resize(image, (5000, 7000), cv2.INTER_LANCZOS4)
#均值滤波
ChQImg = cv2.blur(thresh, (40, 40))
#二进制二值化
ChQImg = cv2.threshold(ChQImg, 30, 225, cv2.THRESH_BINARY)[1]

questionCnts = []
Answer = []

#在二值图像中查找轮廓
cnts = cv2.findContours(ChQImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#用边缘检测绘制
cnts = cnts[1] if imutils.is_cv3() else cnts[0]
for c in cnts:
    # 计算轮廓的边界框，然后利用边界框数据计算宽高比
    (x, y, w, h) = cv2.boundingRect(c)
    if (w > 60 & h > 20) and x>370 and x<4700 and y>3390 and y<4100:
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        #绘制中心及其轮廓
        cv2.drawContours(fImage, c, -1, (0, 0, 255), 5, lineType=0)
        cv2.circle(fImage, (cX, cY), 7, (255, 255, 255), -1)
        #保存题目坐标信息
        Answer.append((cX, cY))

xt1=[0,580,740,885,1036,1190,1460,1610,1765,1915,2060,2345,2500,2640,2800,2965,3110,3260,3410,3560,3720,3890,4045,4190,4345,4510,5000]
yt1=[3390,3590,3710,3825,3935,4100]

#题号换行
def judgey(y):
    if (y / 5 < 1):
        return  y + 1
    elif y / 5 < 2 and y/5>=1:
        return y % 5 + 25 + 1
    else:
        return y % 5 + 45 + 1

#获取选项
def judgex(x, y=1):
    letter = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return letter[x%(5*y)-1]

#获取题号
def judge0(x, y, m, n):
    if x/5<1 :
        num = judgey(y)
    elif x/5<2 and x/5>=1:
        num = judgey(y)+5
    elif x/5<3 and x/5>=2:
        num = judgey(y)+10
    elif x/5<4 and x/5>=3:
        num = judgey(y)+15
    else:
        num = judgey(y)+20
      
    option = judgex(x)

    return [num, option]


IDAnswer = []
# 循环判断坐标点
for i in Answer:
    for j in range(0,len(xt1)-1):
        if i[0]>xt1[j] and i[0]<xt1[j+1]:
            for k in range(0,len(yt1)-1):
                if i[1]>yt1[k] and i[1]<yt1[k+1]:
                    option = judge0(j, k, i[0], i[1])
                    IDAnswer.append(option)
        
IDAnswer.sort()
print(IDAnswer);