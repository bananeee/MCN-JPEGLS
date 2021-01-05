import cv2
import numpy as np
from bitstring import BitArray, BitStream

import numpy as np
from PIL import Image as im
from matplotlib import pyplot as plt
# from matplotlib import pyplot as plt


class Decoder:
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
    MErrvalArr = []
    k = TEMP = 0

    Buffer = BitArray()

    f = open('test2', 'rb')

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
        for i in range(0, 365):
            self.A[i] = 4
            self.N[i] = 1
            self.B[i] = self.Nn[i] = self.C[i] = 0
        self.A[365] = self.A[366] = 4
        self.N[365] = self.N[366] = 1

    def readImgSize(self):
        self.ImgHeight = 100
        self.ImgWidth = 100

    def showOriginalImg(self):
        # result = np.array(self.originalImage)
        # img = im.fromarray(result)
        # img.save('createImg.png')
        # print(len(self.originalImage[0]), len(self.originalImage))
        self.showGraph()

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
        if(self.MErrval & 1) == 1:
            self.Errval = - ((self.MErrval+1) >> 1)
        else:
            self.Errval = self.MErrval >> 1

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

    def computeError(self):
        """
        docstring
        """
        if self.SIGN == -1:
            self.Errval = -self.Errval

        self.Rx = (self.Errval+self.Px) % self.RANGE

        # if self.Rx < 0:
        #     self.Rx = self.Rx + self.RANGE
        # elif self.Rx > self.MAXVAL:
        #     self.Rx = self.Rx - self.RANGE

        # if self.Rx < 0:
        #     self.Rx = 0
        # elif self.Rx > self.MAXVAL:
        #     self.Rx = self.MAXVAL

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

    def golombDecode(self):
        """
        docstring
        """
        while 1:
            q = 0
            for i in self.Buffer:
                if i == 1:
                    q += 1
                else:
                    break
            if q == self.Buffer.length or (q + self.k + 1) > self.Buffer.length:
                self.readFromFile()
                continue
            r = 0
            rcd = 0  # r count down
            for i in self.Buffer[q + 1: q + self.k + 1]:
                r += int(i) << (self.k-rcd-1)
                rcd += 1
            self.MErrval = (q << self.k) + r
            del self.Buffer[0:(q + self.k + 1)]
            break

    def readFromFile(self):
        """
        docstring
        """
        self.Buffer += self.f.read(1)

    def regularMode(self):
        """
        docstring
        """
        self.quantizeGradient()
        self.mergeQuantizedGradient()
        self.predictMED()
        self.correctPrediction()
        self.computeGolombParameter()
        self.golombDecode()
        self.errorMapping()
        self.updateVariable()
        self.computeError()
        self.computeContextBias()
        
    def showGraph(self):
        range = (-255, 255)
        bins = 100
        # plt.hist(np.ravel(np.array(self.originalImage)), bins, color='blue', alpha=0.5)
        plt.hist(self.MErrvalArr, bins, color='blue', alpha=0.5)
        plt.xlabel('ErrVal')
        plt.ylabel('Frequency')
        plt.title('ErrVal')
        plt.show()

    def process(self):
        self.readImgSize()
        for i in range(0, self.ImgHeight):
            tempCol = []
            # if i // 20 == 0:
            #     print(i)
            for j in range(0, self.ImgWidth):
                if (i == 0 and j == 0):
                    self.Ra = 0
                    self.Rb = 0
                    self.Rc = 0
                elif (i == 0):
                    self.Ra = tempCol[j - 1]
                    self.Rb = 0
                    self.Rc = 0
                elif (j == 0):
                    self.Rb = self.originalImage[i - 1][j]
                    self.Ra = self.Rb
                    self.Rc = self.Rb
                else:
                    self.Ra = tempCol[j - 1]
                    self.Rb = self.originalImage[i - 1][j]
                    self.Rc = self.originalImage[i - 1][j - 1]
                if i == 0:
                    self.Rd = 0
                elif j == self.ImgWidth - 1:
                    self.Rd = self.Rb
                else:
                    self.Rd = self.originalImage[i - 1][j + 1]

                self.D[0] = self.Rd - self.Rb
                self.D[1] = self.Rb - self.Rc
                self.D[2] = self.Rc - self.Ra

                self.regularMode()
                tempCol.append(self.Rx)
                # print(self.MErrval, end=' ')
                # self.ErrvalArr.append(self.Errval)
                self.MErrvalArr.append(self.MErrval)
                # self.kArr.append(self.k)
                # self.ImgArr.append(self.Rx)
            self.originalImage.append(tempCol)
            # print(tempCol)

        self.f.close()
        self.showGraph()
        print(self.originalImage)

        # self.showOriginalImg()
        
if __name__ == "__main__":
    # x = Encoder(sys.argv[1:])
    x = Decoder("")
    x.process()