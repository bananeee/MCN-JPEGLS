from cv2 import cv2
import numpy as np
from regular import encoder
from matplotlib import pyplot as plt

img = cv2.imread("anh.jpg",0)
cv2.imshow("img",img)
cv2.waitKey(0)
temp = []

for i in range(0,img.shape[0]):
    tempCol = []
    for j in range(0,img.shape[1]):
        tempCol.append(int(img[i][j]))
    temp.append(tempCol)
# print(type(img[0][0]))
error_encoder = encoder(temp)
# print(error_encoder)

                       