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
url = 'http://apis.baidu.com/idl_baidu/ocridcard/ocridcard'
import pytesseract
from PIL import Image

#手动输入值确定卷子类型,默认只有选择题
s=1
'''
第一类卷子：
上边缘：350~450
下边缘：1411~1450
机读卡填土面积：50*10
x:[(90,160,270,350.410),(510,560,680,760,840),(930,1025,1120,1200,1280),(1360,1460,1550,1630,1730)]
y:[(500,520,560,610,650,680),(720,760,800,850,880,930),(950,1000,1030,1080,1130,1170),(1190,1220,1280,1325,1365,1405)]
'''

xt1=[0,90,220,350,470,610,700,830,940,1070,1200,1300,1430,1540,1660,1790,1890,2015,2240,2270,2400]
yt1=[900,1000,1070,1140,1210,1300,1375,1450,1500,1580,1650,1750,1810,1880,1950,2150]

testnumx=[0,350,465,575,690,800,920]
IDnumx=[0,345,460,575,690,800,913,1025,1135,1243,1356,1469,1582,1691,1804,1920,2033,2146,2400]
answernumx=[0,244,2350,717,941,1190,1410,1668,1900,2152,2400]
y1num=[0,480,770]
y2num=[2250,2440,2700]

Answer=[]
#两种卷子统一规格
width1=2400
height1=2800

#卷子model0判题
def judgey0(y):
    if (y / 5 < 1):
        return  y + 1
    elif y / 5 < 2 and y/5>=1:
        return y % 5 + 20 + 1
    else:
        return y % 5 + 40 + 1
def judgex0(x):
    if(x%5==1):
        return 'A'
    elif(x%5==2):
        return 'B'
    elif(x%5==3):
        return 'C'
    elif(x%5==4):
        return 'D'
def judge0(x,y):
    if x/5<1 :
        #print(judgey0(y))
        return (judgey0(y),judgex0(x))
    elif x/5<2 and x/5>=1:
        #print(judgey0(y)+5)
        return (judgey0(y)+5,judgex0(x))
    elif x/5<3 and x/5>=2:
       # print(judgey0(y)+10)
        return (judgey0(y)+10,judgex0(x))
    else:
        #print(judgey0(y)+15)
        return (judgey0(y)+15,judgex0(x))


# 加载图片，将它转换为灰阶，轻度模糊，然后边缘检测。
image = cv2.imread("D:/Python/www/duka/image/ceshi.jpg")
#转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#高斯滤波
blurred = cv2.GaussianBlur(gray, (3, 3), 0)
#自适应二值化方法
blurred=cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,51,2)
blurred=cv2.copyMakeBorder(blurred,5,5,5,5,cv2.BORDER_CONSTANT,value=(255,255,255))
edged = cv2.Canny(blurred, 10, 100)

'''
#hough transform
lines = cv2.HoughLinesP(edged,1,np.pi/180,30,minLineLength=5,maxLineGap=20)
lines1 = lines[:,0,:]#提取为二维
for x1,y1,x2,y2 in lines1[:]:
    cv2.line(image,(x1,y1),(x2,y2),(255,0,0),1)

thresh = cv2.threshold(blurred, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
plt.subplot(122),plt.imshow(thresh)
plt.xticks([]),plt.yticks([])
plt.show()

'''
'''
gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
ret,binary=cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
contours=cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(image,contours,-1,(0,0,255),3)
cv2.imshow("img",image)
cv2.waitKey(0)
'''

# 从边缘图中寻找轮廓，然后初始化答题卡对应的轮廓
'''
findContours
image -- 要查找轮廓的原图像
mode -- 轮廓的检索模式，它有四种模式：
     cv2.RETR_EXTERNAL  表示只检测外轮廓                                  
     cv2.RETR_LIST 检测的轮廓不建立等级关系
     cv2.RETR_CCOMP 建立两个等级的轮廓，上面的一层为外边界，里面的一层为内孔的边界信息。如果内孔内还有一个连通物体，
              这个物体的边界也在顶层。
     cv2.RETR_TREE 建立一个等级树结构的轮廓。
method --  轮廓的近似办法：
     cv2.CHAIN_APPROX_NONE 存储所有的轮廓点，相邻的两个点的像素位置差不超过1，即max （abs (x1 - x2), abs(y2 - y1) == 1
     cv2.CHAIN_APPROX_SIMPLE压缩水平方向，垂直方向，对角线方向的元素，只保留该方向的终点坐标，例如一个矩形轮廓只需
                       4个点来保存轮廓信息
      cv2.CHAIN_APPROX_TC89_L1，CV_CHAIN_APPROX_TC89_KCOS使用teh-Chinl chain 近似算法
'''
cnts = cv2.findContours(edged, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
# cnts = cnts[0] if imutils.is_cv2() else cnts[1]
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
            
# 对原始图像和灰度图都进行四点透视变换
#cv2.drawContours(image, c, -1, (0, 0, 255), 5, lineType=0)
newimage=image.copy()
for i in docCnt:
    cv2.circle(newimage, (i[0][0],i[0][1]), 50, (255, 0, 0), -1)

plt.figure()
plt.subplot(131)
plt.imshow(image,cmap='gray')
#加上这句就隐藏坐标了
#plt.xticks([]), plt.yticks([])
plt.subplot(132)
plt.imshow(blurred,cmap = 'gray')
#plt.grid()
#plt.subplot(122),plt.plot([(0),(1000)])
#plt.xticks([]), plt.yticks([])
plt.subplot(133)
plt.imshow(newimage,cmap = 'gray')
#plt.grid()
#plt.subplot(122),plt.plot([(0),(1000)])
#plt.xticks([]), plt.yticks([])
# plt.show() # 控制显示


paper = four_point_transform(image, docCnt.reshape(4, 2))
warped = four_point_transform(gray, docCnt.reshape(4, 2))

# 对灰度图应用二值化算法
thresh=cv2.adaptiveThreshold(warped,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,53,2)
threshtmmp=thresh

#图形转换为标准方块
'''
插值方法
INTER_NEAREST - 最邻近插值
INTER_LINEAR - 双线性插值，这是默认的方法）
INTER_AREA - resampling using pixel area relation. It may be a preferred method for image decimation, as it gives moire’-free results. But when the image is zoomed, it is similar to the INTER_NEAREST method.
INTER_CUBIC - 4x4像素邻域的双立方插值
INTER_LANCZOS4 - 8x8像素邻域的Lanczos插值
'''
    # cv2.imwrite("D:/Python/www/duka/1.jpg",ChQImg)
#卷子类型为1
if s==1:
    thresh = cv2.resize(thresh, (width1, height1), cv2.INTER_LANCZOS4)
    paper = cv2.resize(paper, (width1, height1), cv2.INTER_LANCZOS4)

    # paper 用来标记边缘检测，所以建一个来保存
    paperorign = paper
    warped = cv2.resize(warped, (width1, height1), cv2.INTER_LANCZOS4)
    ChQImg = cv2.blur(thresh, (23, 23))

    '''
    参数说明
    第一个参数 src    指原图像，原图像应该是灰度图。
    第二个参数 x      指用来对像素值进行分类的阈值。
    第三个参数 y      指当像素值高于（有时是小于）阈值时应该被赋予的新的像素值
    第四个参数 Methods  指，不同的不同的阈值方法，这些方法包括：
                •cv2.THRESH_BINARY        
                •cv2.THRESH_BINARY_INV    
                •cv2.THRESH_TRUNC        
                •cv2.THRESH_TOZERO        
                •cv2.THRESH_TOZERO_INV    
    '''
    ChQImg = cv2.threshold(ChQImg, 100, 225, cv2.THRESH_BINARY)[1]

    NumImg=cv2.blur(thresh,(15,15))
    NumImg=cv2.threshold(NumImg, 170, 255, cv2.THRESH_BINARY)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    NumImg2 = cv2.dilate(warped, kernel)
    # NumImg2=cv2.adaptiveThreshold(ChQImg2,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,5,2)
    NumImg2 = cv2.erode(NumImg2, kernel2)
    # NumImg2 = cv2.threshold(ChQImg2, 200, 225, cv2.THRESH_BINARY)[1]
    NumImg2 = cv2.adaptiveThreshold(NumImg2, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 23, 2)
    # ChQImg2 = cv2.threshold(ChQImg2, 200, 225, cv2.THRESH_BINARY)[1]
    NumImg2=NumImg2-NumImg
    NumImg2=cv2.blur(NumImg2,(5,5))
    NumImg2=cv2.threshold(NumImg2,170,255,cv2.THRESH_BINARY)[1]

    
    # 实验发现用边缘检测根本不靠谱……
    # 确定选择题答题区
    # ChQImg=thresh[450:height0,0:width0]
    # 在二值图像中查找轮廓，然后初始化题目对应的轮廓列表
    cnts = cv2.findContours(ChQImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    '''
    检测用边缘绘制
    cv2.drawContours(paper, cnts[1], -1, (0, 0, 255), 10, lineType=0)
    '''
    # cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    cnts = cnts[1] if imutils.is_cv3() else cnts[0]
    questionCnts = []

    cv2.imwrite("D:/Python/www/duka/1.jpg",ChQImg)

    # cv2.namedWindow("ceshi",0);
    # cv2.resizeWindow("ceshi", 480, 640);
    # cv2.imshow("ceshi", ChQImg)
    # cv2.waitKey(0)

    # 对每一个轮廓进行循环处理
    for c in cnts:
        # 计算轮廓的边界框，然后利用边界框数据计算宽高比
        (x, y, w, h) = cv2.boundingRect(c)
        questionCnts.append(c)
        if (w > 60 & h > 20)and y>900 and y<2000:
            questionCnts.append(c)
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.drawContours(paper, c, -1, (0, 0, 255), 5, lineType=0)
            cv2.circle(paper, (cX, cY), 7, (255, 255, 255), -1)
            Answer.append((cX, cY))

cv2.imwrite("D:/Python/www/duka/1.jpg",paper)

#答案选择输出
print(Answer)
IDAnswer=[]
for i in Answer:
    for j in range(0,len(xt1)-1):
        if i[0]>xt1[j] and i[0]<xt1[j+1]:
            for k in range(0,len(yt1)-1):
                if i[1]>yt1[k] and i[1]<yt1[k+1]:
                    judge0(j,k)
                    IDAnswer.append(judge0(j,k))

    #print(i)
'''
newx1=[]
newy1=[]
for i in xt1:
    a=i%10
    if(a>5):
        i=(int(i/10))*10+10
    else:
        i=(int(i/10))*10
    newx1.append(i)
for i in yt1:
    a = i % 10
    if (a > 5):
        i = (int(i / 10)) * 10 + 10
    else:
        i = (int(i / 10)) * 10
    newy1.append(i)
newx1=list(set(newx1))
newy1=list(set(newy1))
newx1.sort()
newy1.sort()
print(Answer)
print(newx1)
print(len(newx1))
print(newy1)
print(len(newy1))
t.sort()
print(t)
'''
IDAnswer.sort()
print(IDAnswer)
# print(len(IDAnswer))


# get(data)
# print(getid)
# with open("D:/Python/www/duka/source/test.txt", "w") as f:
#     f.write(str(IDAnswer)+'\n')
#     f.write(str(getid)+'\n')

# plt.figure()
# plt.subplot(131)
# plt.imshow(warped,cmap='gray')
# #加上这句就隐藏坐标了
# #plt.xticks([]), plt.yticks([])
# plt.subplot(132)
# plt.imshow(ChQImg,cmap = 'gray')
# plt.subplot(133)
# plt.imshow(NumImg,cmap = 'gray')
# #plt.grid()
# #plt.subplot(122),plt.plot([(0),(1000)])
# #plt.xticks([]), plt.yticks([])
# plt.show()

# plt.figure()
# plt.imshow(paper,cmap='gray')
# #加上这句就隐藏坐标了
# #plt.xticks([]), plt.yticks([])

# #plt.grid()
# #plt.subplot(122),plt.plot([(0),(1000)])
# #plt.xticks([]), plt.yticks([])
# plt.show()

