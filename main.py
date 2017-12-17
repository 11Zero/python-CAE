import numpy as np
import copy
import pygame,sys
from pygame.locals import *

class Node:

    def __init__(self):
        self.id = -1
        self.coordinate = [0, 0]
        self.type = -1

    def copy(self):
        return self


class RodElement:

    def __init__(self):
        self.id = -1
        self.node_id = [0]*2
        self.node_coord = np.zeros((2,2))
        self.type = -1
        self.material = -1
        self.length = 0
        self.C = 0
        self.S = 0
        self.uElement = np.zeros((4,1))
        self.k = np.zeros((4,4))
        self.nodef = np.zeros((4,1))
        self.stress = 0
        self.nodef_global = np.zeros((4, 1))

    def copy(self):
        return self

    def get_k(self):
        self.length = np.sqrt((self.node_coord[0, 0] - self.node_coord[1, 0]) ** 2 +
                         (self.node_coord[0, 1] - self.node_coord[1, 1]) ** 2)
        self.C = (self.node_coord[0, 0] - self.node_coord[1, 0]) / self.length
        self.S = (self.node_coord[0, 1] - self.node_coord[1, 1]) / self.length
        EA = 1000
        T = np.mat([[self.C,-self.S,0,0],
             [self.S,self.C,0,0],
             [0,0,self.C,-self.S],
             [0,0,self.S,self.C]])
        k = np.mat([[1,0,-1,0],
             [0,0,0,0],
             [-1,0,1,0],
             [0,0,0,0]])*EA/self.length

        # print(T*k*T.T)
        # print(T)
        # print(k)
        # print('-----------------------')
        k = T*k*T.T
        self.k = k
        return k

    def get_f(self):
        self.nodef_global = self.k*self.uElement
        T = np.mat([[self.C, -self.S, 0, 0],
                    [self.S, self.C, 0, 0],
                    [0, 0, self.C, -self.S],
                    [0, 0, self.S, self.C]])
        self.nodef = T.T*self.nodef_global
        return self.nodef_global

    def get_stress(self):
        self.stress = self.nodef


class Main:

    def __init__(self):
        self.node_num = 10
        self.element_num = 21
        self.nodes = [Node]*node_num
        self.elements = [RodElement]*element_num
        self.height = 1
        self.width = 1
        self.u = []
        self.node_f = np.zeros((2*node_num,1))

    def run(self):
        node = Node()

        for i in range(5):
            node.id = i*2
            node.coordinate = copy.deepcopy([i*self.width,0])
            self.nodes[i*2] = copy.deepcopy(node)
            node.id = i*2+1
            node.coordinate = copy.deepcopy([i*self.width,self.height])
            self.nodes[i * 2+1] = copy.deepcopy(node)


        element = RodElement()
        ele_num = 0

        for i in range(4):
            element.id = ele_num
            element.node_id = [i * 2,1 + i * 2]
            self.elements[ele_num] = copy.deepcopy(element)
            ele_num = ele_num + 1

            element.id = ele_num
            element.node_id = [i * 2,2 + i * 2]
            self.elements[ele_num] = copy.deepcopy(element)
            ele_num = ele_num + 1

            element.id = ele_num
            element.node_id = [i * 2, 3 + i * 2]
            self.elements[ele_num] = copy.deepcopy(element)
            ele_num = ele_num + 1

            element.id = ele_num
            element.node_id = [1 + i * 2, 2 + i * 2]
            self.elements[ele_num] = copy.deepcopy(element)
            ele_num = ele_num + 1

            element.id = ele_num
            element.node_id = [1 + i * 2, 3 + i * 2]
            self.elements[ele_num] = copy.deepcopy(element)
            ele_num = ele_num + 1

        element.id = ele_num
        element.node_id = [4 * 2, 4 * 2 + 1]
        self.elements[ele_num] = copy.deepcopy(element)
        ele_num = ele_num + 1

        P = -10
        F = [0,0,0,P,0,0,0,P,0,0,0,P,0,0,0,P,0,0,0,P]
        K = np.zeros((2*len(self.nodes),2*len(self.nodes)))
        EA = 1000
        for i in range(len(self.elements)):
            element = self.elements[i]
            try:
                self.elements[i].node_coord = \
                    copy.deepcopy(np.mat([self.nodes[element.node_id[0]].coordinate,self.nodes[element.node_id[1]].coordinate]))
            except IndexError as e:
                print(i)
            element = self.elements[i]
            k = self.elements[i].get_k()
            nodei = element.node_id[0]
            nodej = element.node_id[1]
            K[2 * nodei: 2 * nodei+2, 2 * nodei: 2 * nodei+2] = \
                K[2 * nodei: 2 * nodei+2, 2 * nodei: 2 * nodei+2]+k[0: 2, 0: 2]

            K[2 * nodei: 2 * nodei+2, 2 * nodej: 2 * nodej+2] = \
                K[2 * nodei: 2 * nodei+2, 2 * nodej: 2 * nodej+2]+k[0: 2, 2: 4]

            K[2 * nodej: 2 * nodej+2, 2 * nodei: 2 * nodei+2] = \
                K[2 * nodej: 2 * nodej+2, 2 * nodei: 2 * nodei+2]+k[2: 4, 0: 2]

            K[2 * nodej: 2 * nodej+2, 2 * nodej: 2 * nodej+2] = \
                K[2 * nodej: 2 * nodej+2, 2 * nodej: 2 * nodej+2]+k[2: 4, 2: 4]

        constrain_node = [0,8]
        constrain_degree = [[1,1],[0,1]]
        for i in range(len(constrain_node)):
            for j in range(2):
                if constrain_degree[i][j] == 1:
                    K[2 * constrain_node[i] + j,:]=0
                    K[:, 2 * constrain_node[i] + j]=0
                    K[2 * constrain_node[i] + j, 2 * constrain_node[i] + j] = 1
        K = K*1e15
        F = np.mat(F)*1e15
        self.u=np.mat(K).I*F.T
        F = F / 1e15
        for i in range(len(self.elements)):
            nodei = self.elements[i].node_id[0]
            nodej = self.elements[i].node_id[1]
            self.elements[i].uElement[0] = self.u[2*nodei]
            self.elements[i].uElement[1] = self.u[2*nodei+1]
            self.elements[i].uElement[2] = self.u[2*nodej]
            self.elements[i].uElement[3] = self.u[2*nodej + 1]
            print(self.elements[i].get_f())
            self.node_f[[2*nodei,2*nodei+1],:] -= self.elements[i].get_f()[[0,1],:]
            self.node_f[[2*nodej,2*nodej+1], :] -= self.elements[i].get_f()[[2,3], :]

        print('-----------------------------------')
        print(self.u)
        print('-----------------------------------')
        print(self.node_f)
        print('-----------------------------------')
        self.node_f = self.node_f + np.mat(F).T
        for i in range(self.node_f.shape[0]):
            for j in range(self.node_f.shape[1]):
                if np.abs(self.node_f[i,j])<1e-10:
                    self.node_f[i, j] = 0

        print(self.node_f)


if __name__ == '__main__':
    main = Main()
    main.run()
    pygame.init()

    screen = pygame.display.set_mode((640, 360), 0, 32)

    color = (200, 156, 64)
    # points = []
    flag = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        my_font = pygame.font.SysFont('arial', 16)

        for i in range(len(main.nodes)):
            if flag == 1:
                break
            txtpos = main.nodes[i].coordinate
            screen.blit(my_font.render("%d" % (main.nodes[i].id + 1), True, (255, 0, 0)), [txtpos[0]*100+150,-txtpos[1]*100+150])
            pygame.display.update()
        for i in range(len(main.elements)):
            if flag == 1:
                break
            nodei = main.elements[i].node_id[0]
            nodej = main.elements[i].node_id[1]
            main.elements[i].uElement[0] = main.u[2*nodei]
            main.elements[i].uElement[1] = main.u[2*nodei+1]
            main.elements[i].uElement[2] = main.u[2*nodej]
            main.elements[i].uElement[3] = main.u[2*nodej + 1]
            nodepos = main.elements[i].node_coord
            nodepos[:,1] = copy.deepcopy(-nodepos[:,1])
            nodepos = (nodepos*100+150*np.ones((2,2))).tolist()
            pygame.draw.lines(screen, color, False, nodepos, 1)
            txtpos = [(nodepos[0][0]+nodepos[1][0])/2+(nodepos[0][0]-nodepos[1][0])/4-10,(nodepos[0][1]+nodepos[1][1])/2+(nodepos[0][1]-nodepos[1][1])/4-10]
            screen.blit(my_font.render("%d"%(main.elements[i].id+1), True, (255, 255, 255)), txtpos)
            # 显示字体
            pygame.display.update()

        flag = 1

        # if len(points) > 1:
        #     pygame.draw.lines(screen, color, False, points, 5)

        pygame.display.update()