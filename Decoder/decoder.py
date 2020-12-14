import cv2
import numpy as np
from bitstring import BitArray, BitStream

import numpy as np
from PIL import Image as im
from matplotlib import pyplot as plt
# from matplotlib import pyplot as plt

class Encoder:
    MAXVAL = 255
    self.MAX_C = 127
    MIN_C = -128
    RESET = 64
    RANGE = 256
    SIGN = 0
    T1 = 3
    T2 = 7
    T3 = 21
    Ra = self.Rb = Rc = Rd = 0, 0, 0, 0, 0
    EOLine = 0
    A, N, Nn = [0] * 367, [0] * 367, [0] * 367
    B, C = [0] * 365, [0] * 365
    RUNindex = RUNval = RUNcnt = 0
    D, Q = [0] * 3, [0] * 3
    q = 0
    Px = Rx = 0
    Errval = MErrval = EMErrval = 0
    k = TEMP = 0
    RItype = map = 0
    
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
        if SIGN == 1:
            self.Px = self.Px + self.C[q]
        else:
            self.Px = self.Px - self.C[q]

        if self.Px > MAXVAL:
            self.Px = MAXVAL
        elif self.Px < 0:
            self.Px = 0

    def computeGolombParameter(self):
        """
        docstring
        """
        self.k = 0
        while (self.N[q] << self.k) < self.A[q]:
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
        self.B[q] = self.B[q] + Errval
        self.A[q] = self.A[q] + abs(Errval)
        if self.N[q] == RESET:
            self.A[q] = self.A[q] >> 1
            self.B[q] = self.B[q] >> 1
            self.N[q] = self.N[q] >> 1
        self.N[q] += 1
        
    def computeError(self):
        """
        docstring
        """
        if SIGN == -1:
            Errval = -Errval

        Rx = (Errval+Px) % RANGE

        if Rx < 0:
            Rx = Rx + RANGE
        elif Rx > MAXVAL:
            Rx = Rx - RANGE

        if Rx < 0:
            Rx = 0
        elif Rx > MAXVAL:
            Rx = MAXVAL

    def computeContextBias(self):
        """
        docstring
        """
        if self.B[q] <= -self.N[q]:
            self.B[q] = self.B[q] + self.N[q]
        if self.C[q] > self.MIN_C:
            self.C[q] = self.C[q] - 1
        if self.B[q] <= -self.N[q]:
            self.B[q] = -self.N[q] + 1
        elif self.B[q] > 0:
            self.B[q] = self.B[q] - self.N[q]
            if self.C[q] < self.MAX_C:
                self.C[q] = self.C[q] + 1
            if self.B[q] > 0:
                self.B[q] = 0

    def writeToFile(self):
        """
        docstring
        """
        pass

    def regularMode(self):
        """
        docstring
        """
        pass
