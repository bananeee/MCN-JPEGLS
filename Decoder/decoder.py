import cv2
import numpy as np
from bitstring import BitArray, BitStream

import numpy as np
from PIL import Image as im 
from matplotlib import pyplot as plt
# from matplotlib import pyplot as plt

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

ImgHeight = 280
ImgWidth = 295

OriginalImgMatrix = []
BufferBitArray = BitArray([])
f = open('test', 'rb')

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

    # Determine Golomb parameter
    k = 0
    while (N[q] << k) < A[q]:
        # print("ok")
        k = k + 1

    # Mapped-error Decoding
    MErrval = GolombDecoding(k)

    # Error mapping
    if(MErrval & 1) == 1:
        Errval = - ((MErrval+1) >> 1)
    else:
        Errval = MErrval >> 1

    # Update variable
    B[q] = B[q] + Errval
    A[q] = A[q] + abs(Errval)
    if N[q] == RESET:
        A[q] = A[q] >> 1
        B[q] = B[q] >> 1
        N[q] = N[q] >> 1
    N[q] = N[q] + 1

    if SIGN == -1:
        Errval = -Errval
        
    Rx = (Errval+Px)%RANGE
    
    if Rx < 0:
        Rx = Rx + RANGE;
    elif Rx > MAXVAL:
        Rx = Rx - RANGE;

    if Rx<0:
        Rx = 0;
    elif Rx > MAXVAL:
        Rx = MAXVAL;
        
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
    
def GolombDecoding(k):
    
    # q_encode = BitArray()
    q = 0
    r = 0
    r_encode = BitArray()
    counter = -1
    while True:
        if (BufferBitArray.length == 0):
            f_contents = f.read(1)
            BufferBitArray += f_contents
        if BufferBitArray[0] == 1 and counter == -1:
            # q_encode += [1]
            q += 1
            del BufferBitArray[0]
        elif BufferBitArray[0] == 0 and counter == -1:
            del BufferBitArray[0]
            counter = k
        elif counter > 0:
            counter -= 1
            r_encode += BufferBitArray[0]
            del BufferBitArray[0]
        elif counter == 0:
            break
        
    for bit in r_encode:
        r = (r << 1) | bit
        
    return q * k + r


if __name__ == "__main__":

    OriginalImgMatrix = [[0] * ImgWidth] * ImgHeight

    # Initiate
    for i in range(0, 365):
        A[i] = 4
        N[i] = 1
        B[i] = Nn[i] = C[i] = 0
    A[365] = A[366] = 4
    N[365] = N[366] = 1

    # Start decoding
    for i in range(0, ImgHeight):
        for j in range(0, ImgWidth):
            if (i == 0 & j == 0):
                Ra = 0
                Rb = 0
                Rc = 0
            elif (i == 0):
                Ra = OriginalImgMatrix[i][j - 1]
                Rb = 0
                Rc = 0
            elif (j == 0):
                Rb = OriginalImgMatrix[i - 1][j]
                Ra = Rb
                Rc = Rb
            else:
                Ra = OriginalImgMatrix[i][j - 1]
                Rb = OriginalImgMatrix[i - 1][j]
                Rc = OriginalImgMatrix[i - 1][j - 1]
            if j == len(OriginalImgMatrix[0]) - 1:
                Rd = Rb
            else:
                Rd = OriginalImgMatrix[i - 1][j + 1]

            D[0] = Rd - Rb
            D[1] = Rb - Rc
            D[2] = Rc - Ra

            regularModeProcessing()
            OriginalImgMatrix[i][j] = Rx
    f.close()
    result = np.array(OriginalImgMatrix)
    img = im.fromarray(result)
    img.save('createImg.png')
            
    
