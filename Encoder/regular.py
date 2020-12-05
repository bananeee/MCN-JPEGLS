def encoder(array):
    error_arr = []
    for i in range (0, len(array)):
        tempCol = []
        for j in range (0, len(array[0])):
            if ( i == 0 & j  == 0):
                tempA = 0
                tempB = 0
                tempC = 0
            elif( i == 0 ):
                tempA = array[i][j-1]
                tempB = 0
                tempC = 0
            elif (j == 0):
                tempA = 0
                tempB = array[i-1][j]
                tempC = 0
            else:
                tempA = array[i][j-1]
                tempB = array[i-1][j]
                tempC = array[i-1][j-1]
            if (tempC > max(tempA, tempB)):
                tempCol.append(min(tempA, tempB))
            elif (tempC < min(tempA, tempB)):
                tempCol.append(max(tempA, tempB))
            else:
                tempCol.append(tempA + tempB - tempC)
        error_arr.append(tempCol)
    for i in range (0,len(array)):
        for j in range(0,len(array[0])):
            error_arr[i][j] = array[i][j] - error_arr[i][j]
    return error_arr


                

    