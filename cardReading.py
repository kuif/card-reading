# -*- coding: utf-8 -*-
# @Author: [FENG] <1161634940@qq.com>
# @Date:   2020-05-12 12:35:58
# @Last Modified by:   [FENG] <1161634940@qq.com>
# @Last Modified time: 2020-05-15 15:35:56

from imutils.perspective import four_point_transform
import imutils
import cv2
import matplotlib.pyplot as plt
import sys, urllib, json
import csv
import os
import re
import time
from PIL import Image

class cardReading(object):

    def reading(self, url, count):
        # 加载图片，将它转换为灰阶，轻度模糊，然后边缘检测。
        image = cv2.imread(url)

        #转换为灰度图像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #高斯滤波
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        #自适应二值化方法
        blurred=cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,51,2)
        blurred=cv2.copyMakeBorder(blurred,5,5,5,5,cv2.BORDER_CONSTANT,value=(255,255,255))
        edged = cv2.Canny(blurred, 10, 100)

        cnts = cv2.findContours(edged, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[1] if imutils.is_cv3() else cnts[0]
        docCnt = None
        # 确保至少有一个轮廓被找到
        if len(cnts) > 0:
            # 将轮廓按大小降序排序
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

            # 对排序后的轮廓循环处理
            for c in cnts:
                # 获取近似的轮廓
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                # 如果近似轮廓有四个顶点，那么就认为找到了答题卡
                if len(approx) == 4:
                    docCnt = approx
                    break

        # 对右下角坐标点进行处理
        bottom_left = bottom_right = None
        for x in range(0, len(docCnt)):
            doc = list(docCnt[x][0]);
            doc.append(x)
            if doc[0] < 1000 and doc[1] > 1500:
                bottom_left = doc

            if doc[0] > 1000 and doc[1] > 1500:
                bottom_right = doc

        if bottom_left is not None and bottom_right is not None:
            # print(bottom_left, bottom_right)
            if abs(bottom_right[1] - bottom_left[1]) > 70:
                # print(111111)
                docCnt[bottom_right[2]][0][1] = bottom_right[1] + 70
            else:
                # print(222222)
                docCnt[bottom_right[2]][0][0] = bottom_right[0] + 70

        newimage=image.copy()
        for i in docCnt:
            cv2.circle(newimage, (i[0][0],i[0][1]), 50, (255, 0, 0), -1)

        paper = four_point_transform(image, docCnt.reshape(4, 2))
        warped = four_point_transform(gray, docCnt.reshape(4, 2))
        # 对灰度图应用二值化算法
        thresh=cv2.adaptiveThreshold(warped,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,53,2)
        threshtmmp=thresh

        thresh = cv2.resize(thresh, (5000, 7000), cv2.INTER_LANCZOS4)
        fImage = cv2.resize(paper, (5000, 7000), cv2.INTER_LANCZOS4)
        # paper 用来标记边缘检测，所以建一个来保存
        paperorign = paper
        warped = cv2.resize(warped, (5000, 7000), cv2.INTER_LANCZOS4)

        ChQImg = cv2.blur(thresh, (30, 30))
        ChQImg = cv2.threshold(ChQImg, 40, 225, cv2.THRESH_BINARY)[1]

        NumImg=cv2.blur(thresh,(15,15)) # 新的二值化图
        NumImg=cv2.threshold(NumImg, 170, 255, cv2.THRESH_BINARY)[1]

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
        cnts = cnts[1] if imutils.is_cv3() else cnts[0]

        questionCnts = []
        Answer = []

        for c in cnts:
            # 计算轮廓的边界框，然后利用边界框数据计算宽高比
            (x, y, w, h) = cv2.boundingRect(c)
            if ((y>3320 and y<5400) or (y>2016 and y<3011)) and x > 400 and x < 4730 and w > 70 and h > 30:
                M = cv2.moments(c)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                #绘制中心及其轮廓
                cv2.drawContours(fImage, c, -1, (0, 0, 255), 5, lineType=0)
                cv2.circle(fImage, (cX, cY), 7, (255, 255, 255), -1)
                #保存题目坐标信息
                Answer.append((cX, cY))


        xt0=[0,700,1140,1585,2030,2470,2910,3355,3790,4240,4690,5000]
        yt0=[2144,2250,2344,2440,2540,2630,2730,2830,2920,3020,3115]

        xt1=[0,570,730,880,1025,1175,1445,1600,1745,1900,2050,2330,2470,2620,2780,2930,3090,3230,3390,3540,3700,3880,4030,4180,4335,4490,5000]
        yt1=[3500,3620,3740,3865,3975,4140,4300,4400,4530,4645,4800,4960,5080,5200,5310,5440]

        student = []
        IDAnswer = []
        for i in Answer:
            if i[1] > yt0[0] and i[1] < yt0[-1]:
                student.append(i)
            else :
                for j in range(0,len(xt1)-1):
                    if i[0]>xt1[j] and i[0]<xt1[j+1]:
                        for k in range(0,len(yt1)-1):
                            if i[1]>yt1[k] and i[1]<yt1[k+1]:
                                option = self.judge0(j, k, i[0], i[1])
                                IDAnswer.append(option)

        xuehao = '';
        for i in self.bubble_sort(student):
            for k in range(0,len(yt0)-1):
                if i[1]>yt0[k] and i[1]<yt0[k+1]:
                    xuehao += str(k)
               
        IDAnswer=[]
        for i in Answer:
            for j in range(0,len(xt1)-1):
                if i[0]>xt1[j] and i[0]<xt1[j+1]:
                    for k in range(0,len(yt1)-1):
                        if i[1]>yt1[k] and i[1]<yt1[k+1]:
                            option = self.judge0(j, k, i[0], i[1])
                            IDAnswer.append(option)


        IDAnswer.sort()
        newIDAnswer = {'学号': str(xuehao)};
        for x in IDAnswer:
            if x[0] <= 60:
                if x[0] not in newIDAnswer:
                    newIDAnswer[x[0]] = x[1]
                else :
                    newIDAnswer[x[0]] = newIDAnswer[x[0]] + x[1]

        # print(xuehao)
        # print(newIDAnswer)
        return newIDAnswer

    # 冒泡排序
    def bubble_sort(self, list):
        count = len(list)
        for i in range(count):
            for j in range(i + 1, count):
                if list[i] > list[j]:
                    list[i], list[j] = list[j], list[i]
        return list

    #卷子model0判题
    def judgey0(self, y):
        if (y / 5 < 1):
            return  y + 1
        elif y / 5 < 2 and y/5>=1:
            return y % 5 + 25 + 1
        else:
            return y % 5 + 45 + 1

    # 获取选项
    def judgex(self, x, y=1):
        letter = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return letter[x%(5*y)-1]

    def print_all_file_path(self, init_file_path, keyword='jpg'):
        url = []
        for cur_dir, sub_dir, included_file in os.walk(init_file_path):
            if included_file:
                for file in included_file:
                    if re.search(keyword, file):
                        url.append(cur_dir + "\\" + file)
        return url

    def judge0(self, x, y, m, n):
        # score = 20
        if n > 4140 and n < 4800:
            if x/5<1 :
                num = self.judgey0(y)
            elif x/5<2 and x/5>=1:
                num = self.judgey0(y)+5
            elif x/5<4 and x/5>=2:
                num = self.judgey0(y)+10
            else:
                num = self.judgey0(y)+15
        else:
            if x/5<1 :
                num = self.judgey0(y)
            elif x/5<2 and x/5>=1:
                num = self.judgey0(y)+5
            elif x/5<3 and x/5>=2:
                num = self.judgey0(y)+10
            elif x/5<4 and x/5>=3:
                num = self.judgey0(y)+15
            else:
                num = self.judgey0(y)+20

        if m > 2050 and m < 3720 and n > 4140 and n < 4800:
            option = self.judgex(x, 2)
        else:
            option = self.judgex(x, 1)

        return [num, option]

    
if __name__=="__main__":
    cardReading = cardReading()
    # url = ['./image/1.jpg', './image/2.jpg', './image/3.jpg', './image/4.jpg']
    url = cardReading.print_all_file_path("./card");

    # for x in range(0,len(url)):
    # #     # print(url[x])
    #     aaaa = cardReading.reading(url[x], x)
    #     print(aaaa)

    with open('names.csv', 'w') as csvfile:
        fieldnames = list(range(1, 61))
        fieldnames.insert(0,'学号')    

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader() # 注意有写header操作
    
        for x in range(0,len(url)):
            # print(url[x])
            aaaa = cardReading.reading(url[x], x)
            writer.writerow(aaaa)
            print(aaaa)
            # if x == len(url)-1:
            #     print('已全部读取');
            #     for i in range(0,3):
            #         time.sleep(1)
            #         print('即将关闭...%2d.....' % (3-i));

