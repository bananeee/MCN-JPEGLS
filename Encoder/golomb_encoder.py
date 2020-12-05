def golomb_encoder(error_arr):
    string = ''
    for i in range (0,len(error_arr[0])):
        for j in range (0, len(error_arr)):
            s = error_arr[i][j]
            m = 7
            

