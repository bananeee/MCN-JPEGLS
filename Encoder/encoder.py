import matplotlib.pyplot as plt
import sys
import getopt
import random
import cv2
import numpy as np
from bitstring import BitArray, BitStream
import matplotlib
matplotlib.use('TkAgg')


class Encoder:
    MAXVAL = 255
    MAX_C = 127
    MIN_C = -128
    RESET = 64
    RANGE = 256
    SIGN = 0
    T1 = 3
    T2 = 7
    T3 = 21
    Ra = Rb = Rc = Rd = 0
    EOLine = 0
    A, N, Nn = [0] * 367, [0] * 367, [0] * 367
    B, C = [0] * 365, [0] * 365
    RUNindex = RUNval = RUNcnt = 0
    D, Q = [0] * 3, [0] * 3
    q = 0
    Px = Rx = 0
    Errval = MErrval = EMErrval = 0
    ImgArr, ErrvalArr, MErrvalArr, EMErrvalArr, kArr = [], [], [], [], []
    k = TEMP = 0
    Buffer = BitArray()
    
    f = open('test2', 'ab')

    ImgWidth = 0
    ImgHeight = 0

    originalImage = []

    haveCorrectPrediction = True
    haveGraph = True
    haveErrorMaping = True
    inputFile = ""
    outputFile = ""

    def __init__(self, argv):
        # try:
        #     opts, args = getopt.getopt(argv, "hcgi:o:")
        # except getopt.GetoptError:
        #     print('test.py -i <inputfile> -o <outputfile>')
        #     sys.exit(2)
        # for opt, arg in opts:
        #     if opt == '-h':
        #         print('test.py -i <inputfile> -o <outputfile>')
        #         sys.exit()
        #     elif opt in ("-i"):
        #         self.inputFile = arg
        #     elif opt in ("-o"):
        #         self.outputFile = arg
        #     elif opt in ("-c"):
        #         self.haveCorrectPrediction = False
        #     elif opt in ("-g"):
        #         self.haveGraph = False
        #     elif opt in ("-m"):
        #         self.haveErrorMaping = False

        # Initiate
        for i in range(0, 365):
            self.A[i] = 4
            self.N[i] = 1
            self.B[i] = self.Nn[i] = self.C[i] = 0
        self.A[365] = self.A[366] = 4
        self.N[365] = self.N[366] = 1

    def convertImageToArr(self):
        """
        docstring
        """
        img = cv2.imread("food.jpg", 0)

        self.ImgHeight = img.shape[0]
        self.ImgWidth = img.shape[1]

        for i in range(0, self.ImgHeight):
            tempCol = []
            for j in range(0, self.ImgWidth):
                # tempCol.append(random.randint(0, 100))
                tempCol.append(int(img[i][j]))
            self.originalImage.append(tempCol)
        
        # self.originalImage = [[1, 0, 0, 0, 2],
        #                       [5, 2, 0, 6, 1],
        #                       [4, 5, 3, 7, 6]]
        # self.ImgHeight = 3
        # self.ImgWidth = 5
        
        # self.ImgHeight = 1000
        # self.ImgWidth = 1000
        
        # for i in range(0, self.ImgHeight):
        #     tempCol = []
        #     for j in range(0, self.ImgWidth):
        #         tempCol.append(random.randint(0, 100))
        #         # tempCol.append(int(img[i][j]))
        #     self.originalImage.append(tempCol)
            
        # print(self.originalImage)

    def quantizeGradient(self):
        """
        docstring
        """
        for i in range(0, 3):
            if self.D[i] <= -self.T3:
                self.Q[i] = -4
            elif self.D[i] <= -self.T2:
                self.Q[i] = -3
            elif self.D[i] <= -self.T1:
                self.Q[i] = -2
            elif self.D[i] < 0:
                self.Q[i] = -1
            elif self.D[i] <= 0:
                self.Q[i] = 0
            elif self.D[i] < self.T1:
                self.Q[i] = 1
            elif self.D[i] < self.T2:
                self.Q[i] = 2
            elif self.D[i] < self.T3:
                self.Q[i] = 3
            else:
                self.Q[i] = 4

    def mergeQuantizedGradient(self):
        """
        docstring
        """
        if self.Q[0] < 0:
            self.Q[0] = -self.Q[0]
            self.Q[1] = -self.Q[1]
            self.Q[2] = -self.Q[2]
            self.SIGN = -1
        elif self.Q[0] == 0:
            if self.Q[1] < 0:
                self.Q[1] = -self.Q[1]
                self.Q[2] = -self.Q[2]
                self.SIGN = -1
            elif self.Q[1] == 0 and self.Q[2] < 0:
                self.Q[2] = -self.Q[2]
                self.SIGN = -1
            else:
                self.SIGN = 1
        else:
            self.SIGN = 1

        self.q = 81 * self.Q[0] + 9 * self.Q[1] + self.Q[2]

    def predictMED(self):
        """
        docstring
        """
        if self.Rc > max(self.Ra, self.Rb):
            self.Px = min(self.Ra, self.Rb)
        elif self.Rc < min(self.Ra, self.Rb):
            self.Px = max(self.Ra, self.Rb)
        else:
            self.Px = self.Ra + self.Rb - self.Rc

    def correctPrediction(self):
        """
        docstring
        """
        if self.SIGN == 1:
            self.Px = self.Px + self.C[self.q]
        else:
            self.Px = self.Px - self.C[self.q]

        if self.Px > self.MAXVAL:
            self.Px = self.MAXVAL
        elif self.Px < 0:
            self.Px = 0

    def computeError(self):
        """
        docstring
        """
        self.Errval = self.Rx - self.Px
        # print(self.Errval, end0, 0, 0, 0, 0=' ')
        if self.SIGN == -1:
            self.Errval = -self.Errval

    def moduloReductionError(self):
        """
        docstring
        """
        if self.Errval < 0:
            self.Errval = self.Errval + self.RANGE
        if self.Errval >= ((self.RANGE+1)/2):
            self.Errval = self.Errval - self.RANGE

    def computeGolombParameter(self):
        """
        docstring
        """
        self.k = 0
        while (self.N[self.q] << self.k) < self.A[self.q]:
            # print("oself.k")
            self.k = self.k + 1

    def errorMapping(self):
        """
        docstring
        """
        if self.Errval >= 0:
            self.MErrval = 2 * self.Errval
        else:
            self.MErrval = -2 * self.Errval - 1

    def updateVariable(self):
        """
        docstring
        """
        self.B[self.q] += self.Errval
        self.A[self.q] += abs(self.Errval)
        if self.N[self.q] == self.RESET:
            self.A[self.q] = self.A[self.q] >> 1
            self.B[self.q] = self.B[self.q] >> 1
            self.N[self.q] = self.N[self.q] >> 1
        self.N[self.q] += 1

    def computeContextBias(self):
        """
        docstring
        """
        if self.B[self.q] <= -self.N[self.q]:
            self.B[self.q] += self.N[self.q]
            if self.C[self.q] > self.MIN_C:
                self.C[self.q] = self.C[self.q] - 1
            if self.B[self.q] <= -self.N[self.q]:
                self.B[self.q] = -self.N[self.q] + 1
        elif self.B[self.q] > 0:
            self.B[self.q] = self.B[self.q] - self.N[self.q]
            if self.C[self.q] < self.MAX_C:
                self.C[self.q] = self.C[self.q] + 1
            if self.B[self.q] > 0:
                self.B[self.q] = 0

    def golombCode(self):
        """
        docstring
        """
        m = 1 << self.k
        q = self.MErrval >> self.k
        r = self.MErrval - m * q
        ErrBitArr = BitArray()
        for i in range(0, q):
            ErrBitArr += [1]
        ErrBitArr += [0]
        rbin = "{0:b}".format(r)
        for i in range(0, self.k-len(rbin)):
            ErrBitArr += [0]
        for i in rbin:
            if i == '1':
                ErrBitArr += [1]
            else:
                ErrBitArr += [0]
        self.Buffer += ErrBitArr

    def writeToFile(self):
        """
        docstring
        """
        x = 0
        while (self.Buffer.length // 8) > 0:
            x += 1
            self.f.write(self.Buffer[0:8].tobytes())
            del self.Buffer[0:8]
        return x
    
    def writeLastByte(self):
        self.f.write(self.Buffer.tobytes())
        self.f.close()

    def showGraph(self, arr):
        if arr == "MErrVal":   
            range = (-255, 255)
            bins = 100
            # plt.hist(np.ravel(np.array(self.originalImage)), bins, color='blue', alpha=0.5)
            plt.hist(self.MErrvalArr, bins, color='blue', alpha=0.5)
            plt.xlabel('ErrVal')
            plt.ylabel('Frequency')
            plt.title('ErrVal')
            plt.show()
        elif arr == "Img":  
            range = (-255, 255)
            bins = 100
            plt.hist(np.ravel(np.array(self.originalImage)), bins, color='blue', alpha=0.5)
            plt.xlabel('ErrVal')
            plt.ylabel('Frequency')
            plt.title('ErrVal')
            plt.show() 

    def regularMode(self):
        """
        docstring
        """
        self.quantizeGradient()
        self.mergeQuantizedGradient()
        self.predictMED()
        self.correctPrediction()
        self.computeError()
        # self.moduloReductionError()
        self.computeGolombParameter()
        self.errorMapping()
        self.updateVariable()
        self.computeContextBias()
        
        self.golombCode()
        self.writeToFile()

    def process(self):
        """
        docstring
        """
        self.convertImageToArr()
        for i in range(0, self.ImgHeight):
            for j in range(0, self.ImgWidth):
                self.Rx = self.originalImage[i][j]

                if (i == 0 and j == 0):
                    self.Ra = 0
                    self.Rb = 0
                    self.Rc = 0
                elif (i == 0):
                    self.Ra = self.originalImage[i][j - 1]
                    self.Rb = 0
                    self.Rc = 0
                elif (j == 0):
                    self.Rb = self.originalImage[i - 1][j]
                    self.Ra = self.Rb
                    self.Rc = self.Rb
                else:
                    self.Ra = self.originalImage[i][j - 1]
                    self.Rb = self.originalImage[i - 1][j]
                    self.Rc = self.originalImage[i - 1][j - 1]
                if i == 0:
                    self.Rd = 0
                elif j == len(self.originalImage[0]) - 1:
                    self.Rd = self.Rb
                else:
                    self.Rd = self.originalImage[i - 1][j + 1]

                self.D[0] = self.Rd - self.Rb
                self.D[1] = self.Rb - self.Rc
                self.D[2] = self.Rc - self.Ra

                self.regularMode()
                # print(self.MErrval, end=' ')
                self.ErrvalArr.append(self.Errval)
                self.MErrvalArr.append(self.MErrval)
                self.kArr.append(self.k)
                self.ImgArr.append(self.Rx)
        self.writeLastByte()
        self.showGraph("Img")
        self.showGraph("MErrVal")

if __name__ == "__main__":
    # x = Encoder(sys.argv[1:])
    x = Encoder("")
    x.process()
