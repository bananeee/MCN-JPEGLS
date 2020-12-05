def golomb_encoder(k,s):
    str = ''
    m = 2**k
    r = s % m
    q = s // m
    str = ''
    for i in range(0,q):
        str +='1'
    str += '0'
    temp = "{0:b}".format(r)
    for i in range(0,k-len(temp)):
        str += '0'
    str += temp
    return str



            

