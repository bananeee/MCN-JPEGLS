from bitstring import BitArray, BitStream
import cv2

bitarray = BitArray([1,0,1,0,0,0,1,1])

bitarray2 = BitArray([1,0,1,0,0,0,1,0])

bitarray3 = BitArray([0,0,1,0,0,0,0,1, 1, 0, 1, 1, 1])

# with open('test', 'wb') as f:
# f = open('test', 'wb')
# f.write(bitarray.tobytes())
# f.write(bitarray2.tobytes())
# f.write(bitarray3.tobytes())
# f.close()
    # print(f_contents )

# with open('test', 'rb') as file:
#     f_contents = file.read(1)
#     while f_contents != b'':
#         print(BitArray(f_contents).bin)
#         f_contents = file.read(1)

img = cv2.imread("anh.jpg",0)
cv2.imshow("img",img)
cv2.waitKey(0)