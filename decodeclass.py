from bitstring import BitArray, BitStream
import numpy as np
class decode:
    Buffer = BitArray()
    arr = []
    f = open('test','rb')
    def __init__(self):
        pass
    def golomb(self,str,k):
        s = 0
        for i in str:
            if i == '1':
                s += 1
            else:
                break
        # if s == 0:
        #     return -1
        if s == len(str) or (s + k + 1) > len(str):
            return 0
        r = 0
        x = 0
        for i in str[s+1:s+k+1]:
            r += int(i) * 2 ** (k-x-1)
            x += 1
        temp = []
        temp.append(s * 2 ** k + r)
        temp.append(s + k + 1)
        return temp
    def readFile(self,k):
        str = ''
        f_contents = self.f.read(1)
        temp = 1
        while f_contents:
            if temp == 1:
                for i in BitArray(f_contents).bin:
                    if i == '1':
                        str += '1'
                    else:
                        str += '0'
            a = self.golomb(str,k)
            temp = 1
            if a == -1:
                break
            elif a == 0:
                f_contents = self.f.read(1)
                continue
            else:
                self.arr.append(a[0])
                str = str[a[1]:]
                temp = 0
        print (self.arr)
        self.f.close()
    #def decode(self):

if __name__ == "__main__":
    myTest = decode()
    myTest.readFile(7)
