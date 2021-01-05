from bitstring import BitArray, BitStream
import numpy as np


class encode:
    Buffer = BitArray()
    f = open('test', 'ab')
    k = 7
    MErrVal = 0

    def __init__(self):
        pass

    def writeToFile(self):
        x = 0
        # with open('test', 'ab') as f:
        while (self.Buffer.length // 8) > 0:
            x += 1
            self.f.write(self.Buffer[0:8].tobytes())
            del self.Buffer[0:8]
        return x

    def writeLastByte(self):
        # with open('test', 'ab') as f:
        self.f.write(self.Buffer.tobytes())
        self.f.close()

    def golomb(self):
        # m = 2 ** self.k
        m = 1 << self.k
        q = self.MErrVal >> self.k
        r = self.MErrVal - m * q
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

    def encode(self):
        temp = (136, 84, 137, 0, 63, 1092, 86, 85, 99, 888, 129, 82)

        for i in temp:
            self.Buffer += self.golomb(i)
            self.writeToFile()
            # del Buffer[0:8 * writeToFile(Buffer)]
        self.writeLastByte()


if __name__ == "__main__":
    myTest = encode()
    myTest.encode()
