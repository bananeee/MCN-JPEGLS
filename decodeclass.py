from bitstring import BitArray, BitStream
import numpy as np
class decode:
    Buffer = BitArray()
    arr = []
    originalImage = []
    MErrVal = 0
    f = open('test','rb')
    def __init__(self):
        pass
    
    def readFile(self):
        self.Buffer += self.f.read(1)
        
    def golomb(self):
        while 1:
            q = 0
            for i in self.Buffer:
                if i == 1:
                    q += 1
                else:
                    break
            if q == self.Buffer.length or (q + self.k + 1) > self.Buffer.length:
                self.readFile()
                continue
            r = 0
            rcd = 0         #r count down
            # print(type(q),q)
            for i in self.Buffer[ q + 1: q + self.k + 1 ]:
                r += int(i) << (self.k-rcd-1)
                rcd += 1
            # temp = []
            self.MErrVal = (q << self.k) + r
            del self.Buffer[0:(q + self.k + 1)]
            # return temp
    def golomb1(self,k):
        s = 0
        for i in self.Buffer:
            if i == 1:
                s += 1
            else:
                break
        if s == self.Buffer.length or (s + k + 1) > self.Buffer.length:
            self.readFile()
            s = self.golomb1(k)
        else: 
            return s
    def decode(self,k):
        self.readFile()
        for i in range(0,13):
            temp = self.golomb(k)
            self.arr.append(temp[0])
            del self.Buffer[0:temp[1]]
            print(self.arr)
if __name__ == "__main__":
    myTest = decode()
    myTest.decode(7)
    print(myTest.arr)
