from bitstring import BitArray, BitStream

a = BitArray([1, 0, 1])

for i in a:
    print(i  == 1)
    # print(i  == 1)
    # print(i  == [0])