import numpy as np
import copy
import pygame,sys
from pygame.locals import *
# from meshpy.triangle import MeshInfo, build
import meshpy.triangle as triangle
import json

class Node:

    def __init__(self):
        self.id = -1
        self.type = -1
        self.coord = -1


class Material:

    def __init__(self):
        self.id = -1
        self.E = -1
        self.h = -1
        self.miu = -1
        self.mass = -1
        self.thickness = -1


class Element:

    def __init__(self):
        self.id = -1
        self.type = -1
        self.nodes = []
        self.material = -1
        self.C = -1
        self.S = -1
        self.k = -1
        self.runType = 0
        self.A = -1
        self.G = -1


    def get_k(self,nodes):
        material = self.material
        if material == -1:
            return
        if self.type == 0:
            E = material.E
            miu = material.miu
        else :
            E = material.E/(1-material.miu**2)
            miu = material.miu/(1-material.miu)
        D = np.mat([[1,miu,0],[miu,1,0],[0,0,(1-miu)/2]])*E/(1-miu**2)
        A = np.mat([[1,nodes[self.nodes[0]].coord[0],nodes[self.nodes[0]].coord[1]],
                    [1,nodes[self.nodes[1]].coord[0],nodes[self.nodes[1]].coord[1]],
                    [1,nodes[self.nodes[2]].coord[0],nodes[self.nodes[2]].coord[1]],])
        A = 0.5*np.abs(np.linalg.det(A))
        node_abc = [[],[],[]]
        B = np.zeros((3,6))
        for i in range(3):
            if i == 0:
                j = 1
                m = 2
            elif i == 1:
                j = 2
                m = 0
            else:
                j = 0
                m = 1
            a = nodes[self.nodes[j]].coord[0]*nodes[self.nodes[m]].coord[1] - nodes[self.nodes[m]].coord[0]*nodes[self.nodes[j]].coord[1]
            b = nodes[self.nodes[j]].coord[1] - nodes[self.nodes[m]].coord[1]
            c = -nodes[self.nodes[j]].coord[0] + nodes[self.nodes[m]].coord[0]
            node_abc[i] = [a,b,c]
            Bi = np.mat([[b,0],[0,c],[c,b]])/2/A
            B[:,i*2:i*2+2] = Bi
        self.k = B.T*D*B*material.h*A
        self.G = np.mat([0,1,0,1,0,1]).T*-1/3*material.mass*material.h*A
        return self.k




    def update(self):
        if self.id == -1 | self.node == -1 | self.material == -1:
            return
        if type == 3:
            nodesCount = len(self.nodes)
            if nodesCount !=3:
                return
            A = np.mat(np.zeros((3,3)))
            A[0,:] = [1,self.nodes[0].coord[0],self.nodes[0].coord[1]]
            A[1, :] = [1, self.nodes[1].coord[0], self.nodes[0].coord[1]]
            A[2, :] = [1, self.nodes[2].coord[0], self.nodes[0].coord[1]]
            A = 0.5*np.abs(np.linalg.det(A))
            ABC = np.mat(np.zeros(3,3))
            for i in range(3):
                if i == 0:
                    j = 1
                    m = 2
                elif i == 1:
                    j = 2
                    m = 0
                else:
                    j = 0
                    m = 1
                ABC[i,0] = self.nodes[j].coord[0]*self.nodes[m].coord[1]-self.nodes[j].coord[0]*self.nodes[m].coord[1]
                ABC[i,1] = self.nodes[j].coord[1]-self.nodes[m].coord[1]
                ABC[i,2] = -self.nodes[j].coord[0]+self.nodes[m].coord[0]

            if self.runType == 0:
                k = np.mat(np.zeros(6,6))
                miu = self.material.miu
                D = np.mat([[1,miu,0],[miu,1,0],[0,0,(1-miu)/2]])\
                    *self.material.E/(1-miu**2)
                B = np.mat(np.zeros(3,6))
                for i in range(3):
                    B[:,i:i+2] = np.mat([[ABC[i,1],0],[0,ABC[i,2]],[ABC[i,2],ABC[i,1]]])
                for i in range(nodesCount):
                    for j in range(nodesCount):
                        tmp_k = self.material.E*self.material.thickness/4/(1-miu**2)/A
                        tmp_k = tmp_k*np.mat([[ABC[i,1]*ABC[j,1]+(1-miu)/2*ABC[i,2]*ABC[j,2], miu*ABC[i,1]*ABC[j,2]+(1-miu)/2*ABC[i,2]*ABC[j,1]],
                                              [miu*ABC[i,2]*ABC[j,1]+(1-miu)/2*ABC[i,1]*ABC[j,2], ABC[i,2]*ABC[j,2]+(1-miu)/2*ABC[i,1]*ABC[j,1]]])




class Main:

    def __init__(self):

        self.nodes = []
        self.elements = []
        self.structureHeight = -1
        self.structureWidth = -1
        self.structureThickness = -1

        self.material = Material
        self.material.id = 1
        self.material.E = 1000000000
        self.material.mass = 100
        self.material.miu = 0.2
        self.material.h = 0.2

        self.meshSize = -1
        self.runType = 0
        self.g = 9.806
        self.X = -1

    def run(self):
        self.structureHeight = 50
        self.structureWidth = 500
        self.structureThickness = 1
        self.meshSize = [3,3]
        node_row = int(np.ceil(self.structureHeight/self.meshSize[1]))+1
        node_col = int(np.ceil(self.structureWidth / self.meshSize[0]))+1
        # self.nodes = np.array(Node)#[i for i in range(node_col*node_row)]
        # self.nodes = np.array(Node)
        node_count = 0
        np.set_printoptions(precision=2)
        # random_points = np.random.rand(100,2)
        # for i in range(len(random_points)):
        #     node = Node()
        #     node.id = node_count
        #     node.type = 1
        #     y = random_points[i,0]*self.structureHeight # i * self.structureHeight / (node_row - 1)
        #     x = random_points[i,1]*self.structureWidth  # j * self.structureWidth / (node_col - 1)
        #     if abs(x - self.structureWidth) < 1e-5:
        #         x = self.structureWidth
        #     if abs(x - 0) < 1e-5:
        #         x = 0
        #     if abs(y - self.structureHeight) < 1e-5:
        #         y = self.structureHeight
        #     if abs(y - 0) < 1e-5:
        #         y = 0
        #     node.coord = [x, y]
        #     self.nodes.append(node)
        #     node_count = node_count + 1
        #
        # facets = []
        #
        # for j in range(node_col):
        #     node = Node()
        #     node.id = node_count
        #     node.type = 1
        #     y = 0
        #     x = j * self.structureWidth / (node_col - 1)
        #     if abs(x - self.structureWidth) < 1e-5:
        #         x = self.structureWidth
        #     if abs(x - 0) < 1e-5:
        #         x = 0
        #     node.coord = [x, y]
        #     self.nodes.append(node)
        #     node_count = node_count + 1
        #
        #     node = Node()
        #     node.id = node_count
        #     node.type = 1
        #     y = self.structureHeight
        #     x = j * self.structureWidth / (node_col - 1)
        #     if abs(x - self.structureWidth) < 1e-5:
        #         x = self.structureWidth
        #     if abs(x - 0) < 1e-5:
        #         x = 0
        #     node.coord = [x, y]
        #     self.nodes.append(node)
        #     node_count = node_count + 1
        #
        #     # if j == node_col - 1:
        #     #     print('this is col - 1')
        #     #     print(node_count)
        #     # if j == 0:
        #     #     print('this is 0')
        #     #     print(node_count)
        #
        #     if j == 0 or j == node_col - 1:
        #         # print([node_count-2,node_count-1])
        #         facets.append([node_count-2,node_count-1])
        #
        #
        # for i in range(node_row):
        #     node = Node()
        #     node.id = node_count
        #     node.type = 1
        #     y = i*self.structureHeight/(node_row-1)
        #     x = 0
        #     if abs(y - self.structureHeight) < 1e-5:
        #         y = self.structureHeight
        #     if abs(y - 0) < 1e-5:
        #         y = 0
        #     node.coord = [x,y]
        #     self.nodes.append(node)
        #     node_count = node_count + 1
        #
        #     node = Node()
        #     node.id = node_count
        #     node.type = 1
        #     y = i * self.structureHeight / (node_row - 1)
        #     x = self.structureWidth
        #     if abs(y - self.structureHeight) < 1e-5:
        #         y = self.structureHeight
        #     if abs(y - 0) < 1e-5:
        #         y = 0
        #     node.coord = [x, y]
        #     self.nodes.append(node)
        #     node_count = node_count + 1
        #     # if i == node_row - 1:
        #     #     print('this is row - 1')
        #     # if i == 0:
        #     #     print('this is 0')
        #     if i == 0 or i == node_row - 1:
        #         # print([node_count-2,node_count-1])
        #         facets.append([node_count-2,node_count-1])


        # from scipy.spatial import Delaunay
        # points = []
        # for item in self.nodes:
        #     points.append(tuple(item.coord))
        # tri = Delaunay(np.array(points))
        # element_count = 0
        # for element_item in tri.simplices:
        #     element = Element()
        #     element.id = element_count
        #     for node_id in  element_item:
        #         for nodeitem in self.nodes:
        #             if (points[node_id][0] - nodeitem.coord[0])**2+(points[node_id][1] - nodeitem.coord[1])**2 <1e-5:
        #                 element.nodes.append(node_id)
        #                 break
        #
        #     if len(element.nodes) >= 3:
        #         self.elements.append(element)
        #         element_count = element_count+1

        mesh_info = triangle.MeshInfo()
        # with open('data.json') as json_file:
        #     points = json.load(json_file)
        # points = [(0,0),(0,100),(150,100),(150,0)]
        points = [[0, 0], [0, self.structureHeight], [self.structureWidth, self.structureHeight], [self.structureWidth, 0]]
        random_points = np.random.rand(300, 2)
        # random_points = np.random.rand(0,1,(100,2))
        random_points = np.mat(random_points)
        random_points[:, 0] = random_points[:, 0] * self.structureWidth
        random_points[:, 1] = random_points[:, 1] * self.structureHeight
        points.extend(random_points.tolist())
        with open('data_random12171.json', 'w') as json_file:
            json_file.write(json.dumps(points))
        mesh_info.set_points(points)
        facets = [[0,1],[1,2],[2,3],[3,0]]
        # print('\n')
        # print(points)
        # print('\n')
        # print(facets)
        # holes = []
        # mesh_info.set_holes(holes)
        mesh_info.set_facets(facets)
        mesh = triangle.build(mesh_info)
        # print("Mesh Points:")
        node_count = 0
        for i, p in enumerate(mesh.points):
            # print(p)
            node = Node()
            node.id = node_count
            node.type = 1
            node.coord = p
            self.nodes.append(node)
            node_count = node_count + 1

        # print("Point numbers in tetrahedra:")
        # for i, t in enumerate(mesh.elements):
        #     print(i)
        #     print(t)
        element_count = 0
        K = np.zeros((node_count*2,node_count*2))
        F = np.zeros((2 * node_count, 1))
        # Constrain = np.zeros((2 * node_count, 1))

        for i,element_item in enumerate(mesh.elements):
            element = Element()
            element.id = element_count
            element.nodes = element_item
            element.material = self.material
            k = element.get_k(self.nodes)
            for j in range(3):
                F[2*element_item[j]:2*element_item[j]+2,:] = F[2*element_item[j]:2*element_item[j]+2,:]+element.G[2*j:2*j+2,:]
                for m in range(3):
                    K[2*element_item[j]:2*element_item[j]+2,2*element_item[m]:2*element_item[m]+2] = \
                        K[2 * element_item[j]:2 * element_item[j] + 2, 2 * element_item[m]:2 * element_item[m] + 2] + k[2*j:2*j+2,2*m:2*m+2]
            self.elements.append(element)
            element_count = element_count + 1
        for i in range(node_count):
            if np.abs(self.nodes[i].coord[0] - 0) < 1e-5:
                K[:,2*i:2*i+2] = 0
                K[2 * i:2 * i + 2,:] = 0
                K[2 * i:2 * i + 2,2 * i:2 * i + 2] = np.eye(2)
                F[2*i:2*i+2,:] = 0
        self.X = np.mat(K).I*np.mat(F)
        a = 0






if __name__ == '__main__':
    main = Main()
    main.run()

    pygame.init()

    geo_scale = [3,-3]
    geo_offset = [55,300]

    screen = pygame.display.set_mode((1600, 800), 0, 32)

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
            pointpos = (np.multiply(np.mat(main.nodes[i].coord),np.mat(geo_scale))+np.mat(geo_offset)).tolist()[0]
            pygame.draw.circle(screen, [255, 0, 0], [int(pointpos[0]), int(pointpos[1])], 3, 2)
            # pointpos = (np.multiply(np.mat(main.nodes[i].coord),np.mat(geo_scale))+np.mat(geo_offset)+np.mat([10,10])).tolist()[0]
            # screen.blit(my_font.render("%d" % (main.nodes[i].id + 1), True, (255, 0, 0)), pointpos)

        for i in range(len(main.elements)):
            if flag == 1:
                break
            node1 = (np.multiply(np.mat(main.nodes[main.elements[i].nodes[0]].coord),np.mat(geo_scale))+np.mat(geo_offset)).tolist()[0]
            node2 = (np.multiply(np.mat(main.nodes[main.elements[i].nodes[1]].coord),np.mat(geo_scale))+np.mat(geo_offset)).tolist()[0]
            node3 = (np.multiply(np.mat(main.nodes[main.elements[i].nodes[2]].coord),np.mat(geo_scale))+np.mat(geo_offset)).tolist()[0]
            pygame.draw.lines(screen, color, False, [node1,node2], 1)
            pygame.draw.lines(screen, color, False, [node1, node3], 1)
            pygame.draw.lines(screen, color, False, [node2, node3], 1)

            node1 = (np.multiply(np.mat(main.nodes[main.elements[i].nodes[0]].coord)+main.X[2*main.elements[i].nodes[0]:2*main.elements[i].nodes[0]+2,:].T, np.mat(geo_scale)) + np.mat(
                geo_offset)).tolist()[0]
            node2 = (np.multiply(np.mat(main.nodes[main.elements[i].nodes[1]].coord)+main.X[2*main.elements[i].nodes[1]:2*main.elements[i].nodes[1]+2,:].T, np.mat(geo_scale)) + np.mat(
                geo_offset)).tolist()[0]
            node3 = (np.multiply(np.mat(main.nodes[main.elements[i].nodes[2]].coord)+main.X[2*main.elements[i].nodes[2]:2*main.elements[i].nodes[2]+2,:].T, np.mat(geo_scale)) + np.mat(
                geo_offset)).tolist()[0]
            pygame.draw.lines(screen, color, False, [node1, node2], 1)
            pygame.draw.lines(screen, color, False, [node1, node3], 1)
            pygame.draw.lines(screen, color, False, [node2, node3], 1)
        flag = 1

        pygame.display.update()