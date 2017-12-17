import numpy as np
import types

mat = np.mat(np.zeros((4,4)))
k = np.mat([[1,0,-1,0],
             [0,0,0,0],
             [-1,0,1,0],
             [0,0,0,0]])
C = 0.375
S = 0.289
T = np.mat([[C, -S, 0, 0],
            [S, C, 0, 0],
            [0, 0, C, -S],
            [0, 0, S, C]])
# arr = [0]*6
# print(arr)
#
#
#
# for i in range(5):
#     print(i)
# print(mat)
# print(k)
# print(T)
# T[2,1:3] = 0
# print(T)
# print(k)
# print(T+k)
# print(T[2,1:3])
# print(mat)
# print(T)
# print(type(T) is type(mat))
# a=[]
# a.append(1)
# print(a)
# a = []
# for i in range(6):
#     a.append(tuple([i]))
#
# print(a)
T = np.mat([0,1,0,1,0,1])
print(T)
print(T.T)