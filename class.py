from bitstring import BitArray, BitStream
import numpy as np
import random

def randomData(start, end, length):
    tempArr = []
    for i in range(0, length):
        tempArr.append(random.randint(start, end))
    return tempArr

class encode:
    Buffer = BitArray()
    f = open('test','ab')
    def __init__(self):
        pass
    def writeToFile(self):
        x = 0
        #with open('test', 'ab') as f:
        while (self.Buffer.length // 8) > 0:
            x += 1
            self.f.write(self.Buffer[0:8].tobytes())
            del self.Buffer[0:8]
        return x 
    def writeLastByte(self):
        #with open('test', 'ab') as f:
        self.f.write(self.Buffer.tobytes())
        self.f.close()
    def golomb(self,s,k):
        m = 2 ** k
        q = s // m
        r = s % m
        str = BitArray()
        for i in range(0,q):
            str += [1]
        str += [0]
        temp = "{0:b}".format(r)
        for i in range(0,k-len(temp)):
            str += [0]
        for i in temp:
            if i == '1':
                str += [1]
            else:
                str += [0]
        return str    
    def encode(self):
        
        temp = randomData(0, 100, 1000)
        print(temp)
        
        for i in temp:
            self.Buffer += self.golomb(i,7)
            self.writeToFile()
            # del Buffer[0:8 * writeToFile(Buffer)]
        self.writeLastByte()

if __name__ == "__main__":
    myTest = encode()
    myTest.encode()