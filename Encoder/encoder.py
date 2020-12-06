import cv2
import numpy as np
from bitstring import BitArray, BitStream

MAXVAL = 255
MAX_C = 127
MIN_C = -128
RESET = 64
RANGE = 256
SIGN = 0
T1 = 3
T2 = 7
T3 = 21
Ra = Rb = Rc = Rd = 0, 0, 0, 0, 0
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
# updated variables
LIMIT = qbpp = bpp = 0
BufferBitArray = BitArray()

def regularModeProcessing():
    # Quantization of the gradients
    for i in range(0, 3):
        if D[i] <= -T3:
            Q[i] = -4
        elif D[i] <= -T2:
            Q[i] = -3
        elif D[i] <= -T1:
            Q[i] = -2
        elif D[i] < 0:
            Q[i] = -1
        elif D[i] <= 0:
            Q[i] = 0
        elif D[i] < T1:
            Q[i] = 1
        elif D[i] < T2:
            Q[i] = 2
        elif D[i] < T3:
            Q[i] = 3
        else:
            Q[i] = 4

    # Quantized gradient merging
    if Q[0] < 0:
        Q[0] = -Q[0]
        Q[1] = -Q[1]
        Q[2] = -Q[2]
        SIGN = -1
    elif Q[0] == 0:
        if Q[1] < 0:
            Q[1] = -Q[1]
            Q[2] = -Q[2]
            SIGN = -1
        elif Q[1] == 0 and Q[2] < 0:
            Q[2] = -Q[2]
            SIGN = -1
        else:
            SIGN = 1
    else:
        SIGN = 1

    # Mapping context to q index
    q = 81 * Q[0] + 9 * Q[1] + Q[2]

    # Edge-detection predictor
    if Rc > max(Ra, Rb):
        Px = min(Ra, Rb)
    elif Rc < min(Ra, Rb):
        Px = max(Ra, Rb)
    else:
        Px = Ra + Rb - Rc

    # Prediction correction
    if SIGN == 1:
        Px = Px + C[q]
    else:
        Px = Px - C[q]

    if Px > MAXVAL:
        Px = MAXVAL
    elif Px < 0:
        Px = 0

    # Computation of prediction error
    Errval = Rx - Px
    if SIGN == -1:
        Errval = -Errval

    # Modulo reduction of the prediction error
    if Errval < 0:
        Errval = Errval + RANGE
    if Errval >= ((RANGE+1)/2):
        Errval = Errval - RANGE

    # Determine Golomb parameter
    k = 0
    while (N[q] << k) < A[q]:
        # print("ok")
        k = k + 1

    # Error mapping
    if Errval >= 0:
        MErrval = 2 * Errval
    else:
        MErrval = -2 * Errval - 1 
        
    # Golomb code
    GolombCoding(MErrval, k)
    
    # Update variable
    B[q] = B[q] + Errval
    A[q] = A[q] + abs(Errval)
    if N[q] == RESET:
        A[q] = A[q] >> 1
        B[q] = B[q] >> 1
        N[q] = N[q] >> 1
    N[q] = N[q] + 1
        
    # Contex-dependent bias computation
    if B[q] <= -N[q]:
        B[q] = B[q] + N[q]
        if C[q] > MIN_C:
            C[q] = C[q] - 1
        if B[q] <= -N[q]:
            B[q] = -N[q] + 1
    elif B[q] > 0:
        B[q] = B[q] - N[q]
        if C[q] < MAX_C:
            C[q] = C[q] + 1
        if B[q] > 0:
            B[q] = 0

def GolombCoding(MErrval, k):
    f = open('test', 'ab')
    q_encode = BitArray()
    r_encode = BitArray()
    m = 1 << k
    r = MErrval % m
    q = MErrval // m
    
    # Encode quotient
    for i in range(0, q):
        q_encode += [1]
    q_encode += [0]
    
    # Encode remainder
    for i in range(0, k):
        if (r & 1 == 0):
            r_encode = [0] + r_encode
        else:
            r_encode = [1] + r_encode
        r = r >> 1
        
    BufferBitArray = q_encode + r_encode
    # print(BufferBitArray.bin)
    # print(BufferBitArray.length)
    while (BufferBitArray.length // 8) > 0:
        f.write(BufferBitArray[0:8].tobytes())
        del BufferBitArray[0:8]
    f.close()

if __name__ == "__main__":
    img = cv2.imread("anh.jpg", 0)
    # cv2.imshow("img", img)
    # cv2.waitKey(0)
    img2dMatrix = []

    for i in range(0, img.shape[0]):
        tempCol = []
        for j in range(0, img.shape[1]):
            tempCol.append(int(img[i][j]))
        img2dMatrix.append(tempCol)
    # print(type(img[0][0]))
    # error_encoder = encoder(img2dMatrix)
    # print(error_encoder)

    # Initiate
    for i in range(0, 365):
        A[i] = 4
        N[i] = 1
        B[i] = Nn[i] = C[i] = 0
    A[365] = A[366] = 4
    N[365] = N[366] = 1

    # Start encoding
    for i in range(0, len(img2dMatrix)):
        for j in range(0, len(img2dMatrix[0])):
            Rx = img2dMatrix[i][j]

            if (i == 0 & j == 0):
                Ra = 0
                Rb = 0
                Rc = 0
            elif (i == 0):
                Ra = img2dMatrix[i][j - 1]
                Rb = 0
                Rc = 0
            elif (j == 0):
                Rb = img2dMatrix[i - 1][j]
                Ra = Rb
                Rc = Rb
            else:
                Ra = img2dMatrix[i][j - 1]
                Rb = img2dMatrix[i - 1][j]
                Rc = img2dMatrix[i - 1][j - 1]
            if j == len(img2dMatrix[0]) - 1:
                Rd = Rb
            else:
                Rd = img2dMatrix[i - 1][j + 1]

            D[0] = Rd - Rb
            D[1] = Rb - Rc
            D[2] = Rc - Ra

            regularModeProcessing()
    
