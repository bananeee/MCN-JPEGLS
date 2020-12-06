from bitstring import BitArray, BitStream


def golomb_encoder(k, s):
    q_encode = BitArray()
    r_encode = BitArray()
    m = 1 << k
    r = s % m
    q = s // m

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

    temp = q_encode + r_encode
    print(temp.bin)
    print(temp.length)
    while (temp.length // 8) > 0:
        print(temp[0:8].bin)
        del temp[0:8]
    # temp = "{0:kb}".format(r)


golomb_encoder(2, 76)
# def writeToFile():
