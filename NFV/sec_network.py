import copy

import networkx as nx
from NFV.satellite import *
from NFV.tools import *


def generateSECRandomly(max_sate_num):
    # 生成基站
    station_num = STATION_NUM
    stations = []
    for index in range(station_num):
        station = SatelliteNode(node_no=str(index), initial_angle=(360 / station_num * index))
        stations.append(station)
    # 生成卫星
    satellites = []
    orbit_num = ORBIT_NUM  # 轨道数量
    # 生成每个轨道的高度
    orbit_altitude = [780, 991, 1202, 1414]
    # 生成每个轨道的卫星数
    each_orbit_sate_num = []
    for orbit in range(orbit_num):
        each_orbit_sate_num.append(randint(MIN_ORBIT_SATELLITE_NUM, max_sate_num))
    # 节点总和
    nodes_num = station_num
    for orbit in range(orbit_num):
        for index in range(each_orbit_sate_num[orbit]):
            sate = SatelliteNode(node_no=str(nodes_num + index),
                                 initial_angle=360 / each_orbit_sate_num[orbit] * index,
                                 altitude=orbit_altitude[orbit],
                                 orbit=orbit)
            satellites.append(sate)

        nodes_num += each_orbit_sate_num[orbit]

    sec = SEC(stations, satellites, orbit_altitude)
    sec.generateSEC()
    return sec


class SEC:
    # 结点字典
    node_dict = {}
    # 轨道数量
    orbit_num = 0
    # 基站数量
    station_num = 0
    # 卫星数量
    satellite_num = 0
    # 各轨道高度
    orbit_altitude = []
    # 卫星-地面网络拓扑图
    sec_graph = nx.Graph()
    # pos
    pos = {}

    def __init__(self, station_nodes, sate_nodes, orbit_altitude):
        """

        :param station_nodes: 基站
        :param sate_nodes: 卫星
        :param orbit_altitude: 各轨道高度
        """
        for station_node in station_nodes:
            self.node_dict[station_node.node_no] = station_node
        self.station_num = len(station_nodes)
        for sate_node in sate_nodes:
            self.node_dict[sate_node.node_no] = sate_node
        self.satellite_num = len(sate_nodes)
        self.orbit_altitude = orbit_altitude
        self.orbit_num = len(self.orbit_altitude)
        self.orbit_satellite_num = []
        for i in range(self.orbit_num):
            self.orbit_satellite_num.append(0)

    def generateSEC(self):
        """
        生成sec网络

        :return:
        """
        # 添加节点到网络中
        for node in self.node_dict.keys():
            self.sec_graph.add_node(node)
            self.pos[node] = self.node_dict.get(node).node_pos
            # 统计每个轨道上的卫星数量
            if self.node_dict.get(node).orbit != -1:
                self.orbit_satellite_num[self.node_dict.get(node).orbit] += 1

        # 星地链路
        self.generateUSL()
        # 相同轨道的星间链路
        self.generateISL()
        # 不同轨道的星间链路
        self.generateIOL()

    def updateSEC(self, t):
        """
        更新网络拓扑

        :param t:
        :return:
        """
        self.sec_graph.clear()
        # 更新角度
        for node in self.node_dict.keys():
            self.node_dict.get(node).updateSatelliteAngular(t)
            self.pos[node] = self.node_dict.get(node).node_pos

        # 更新星地链路
        self.generateUSL()
        # 更新不同轨道间的星间链路
        self.generateIOL()
        # 更新相同轨道的星间链路
        self.generateISL()

    def generateUSL(self):
        """
        生成地面基站与卫星网络的连接

        :return:
        """
        # 星地链路
        height = RADIUS + self.orbit_altitude[0]
        critical_angle = 90 - math.degrees(math.asin(RADIUS / height))
        for i in range(self.station_num):
            for j in range(self.station_num, self.station_num + self.orbit_satellite_num[0]):
                difference = abs(self.node_dict.get(str(j)).angle - self.node_dict.get(str(i)).angle)
                if difference > 180:
                    difference = 360 - difference
                if difference <= critical_angle:
                    distance = lawOfCosines(height, RADIUS, difference)
                    self.sec_graph.add_edge(str(i), str(j), distance=distance)

    def generateIOL(self):
        """
        生成不同轨道间的链路

        :return:
        """
        # 不同轨道间的星间链路
        start_index = self.station_num  # 卫星节点开始编号
        for i in range(self.orbit_num - 1):
            end_index = start_index + self.orbit_satellite_num[i]
            end_index1 = len(self.node_dict.keys())
            height1 = self.orbit_altitude[i] + RADIUS
            for j in range(start_index, end_index):
                for k in range(end_index, end_index1):
                    height2 = self.orbit_altitude[self.node_dict.get(str(k)).orbit] + RADIUS
                    # 两个卫星可以建立连接的最大角度
                    critical_angle = 180 - math.degrees(math.asin(RADIUS / height2)) - math.degrees(
                        math.asin(RADIUS / height1))
                    difference = abs(self.node_dict.get(str(j)).angle - self.node_dict.get(str(k)).angle)
                    if difference > 180:
                        difference = 360 - difference
                    if difference < critical_angle:
                        distance = lawOfCosines(height1, height2, difference)
                        self.sec_graph.add_edge(str(j), str(k), distance=distance)
            start_index = end_index

    def generateISL(self):
        """
        生成同一轨道上的星间链路

        :return:
        """
        # 同一轨道上的星间链路
        start_index = self.station_num  # 卫星节点开始编号
        for i in range(self.orbit_num):
            height1 = self.orbit_altitude[i] + RADIUS
            height2 = height1
            end_index = start_index + self.orbit_satellite_num[i]  # 轨道上卫星的结束节点
            for j in range(start_index, end_index):
                distance = lawOfCosines(height1, height2, 360 / self.orbit_satellite_num[i])
                self.sec_graph.add_edge(str(j), str(start_index + (j + 1 - start_index) % self.orbit_satellite_num[i]),
                                        distance=distance)

            start_index = end_index

    def getNode(self, node_no):
        return self.node_dict[node_no]

    def deepCopy(self):
        """
        deep copy

        :return:
        """
        new_sec = copy.deepcopy(self)
        new_sec.node_dict = copy.deepcopy(self.node_dict)
        new_sec.pos = copy.deepcopy(self.pos)
        new_sec.sec_graph = copy.deepcopy(self.sec_graph)
        return new_sec

    def finishReq(self, request):
        # print(request.service_chain.number_of_vnf, request.route_path, request.service_chain_path)
        if len(request.route_path) == 0:
            return
        for index in range(len(request.service_chain.vnf_lists)):
            self.getNode(request.service_chain_path[index]).finishVNF(request.service_chain.vnf_lists[index])
