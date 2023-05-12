from random import *
from NFV.tools import *


class SatelliteNode:
    # 卫星编号
    node_no = ""
    # 卫星计算总资源
    compute_resource = -1
    remain_resource = -1
    # 卫星所处轨道
    orbit = -1
    # 卫星轨道高度
    altitude = 0
    # 卫星角
    angle = 0
    # 初始角度
    initial_angle = 0
    # 单位资源处理速度 Mbit/s
    unit_process_rate = 0
    # 单位资源使用成本
    unit_process_cost = 0
    # networkx绘图
    node_pos = []

    def __init__(self, node_no, initial_angle, altitude=0, orbit=-1):
        self.node_no = node_no
        self.orbit = orbit
        self.angle = initial_angle
        self.initial_angle = initial_angle
        self.altitude = altitude
        self.sate_kind = randint(0, len(UNIT_PROCESS_RATE) - 1)
        self.unit_process_rate = UNIT_PROCESS_RATE[self.sate_kind]
        self.unit_process_cost = UNIT_PROCESS_COST[self.sate_kind]
        self.compute_resource = COMPUTE_RESOURCE[self.sate_kind]
        self.remain_resource = self.compute_resource
        # vnf处理列表
        self.process_dict = dict()
        # vnf到达时隙
        self.arrive_time_dict = dict()
        # vnf请求的资源
        self.resource_dict = dict()
        # vnf结束的时隙
        self.end_time_dict = dict()
        if orbit == -1:
            self.node_pos = [0.5 * math.sin(math.radians(self.angle)), 0.5 * math.cos(math.radians(self.angle))]
        else:
            self.node_pos = [(self.orbit + 2) * math.sin(math.radians(self.angle)),
                             (self.orbit + 2) * math.cos(math.radians(self.angle))]

    def setAngle(self, new_angle):
        """
        设置卫星角度

        :param new_angle: 新的角度
        :return:
        """
        self.angle = new_angle

    def getProcessDelay(self, vnf, b):
        """
        获取时隙在t卫星处理延迟（和分配的计算资源量以及卫星的拥塞程度有关）

        :param vnf: vnf
        :param b: 数据大小
        :return: 处理延迟
        """
        return b / (vnf.getReqResource(b) * self.unit_process_rate)

    def getVirtualizationCost(self, vnf, b):
        """
        获取vnf在卫星上的资源使用成本以及实例化成本

        :param vnf: vnf
        :param b: 数据大小
        :return: 资源使用成本
        """
        process_cost = vnf.getReqResource(b) * self.unit_process_cost * self.getProcessDelay(vnf, b)
        instance_cost = VNF_INSTANTIATION_COST[self.sate_kind][vnf.vnf_kind]
        return process_cost + instance_cost

    def updateSatelliteAngular(self, t):
        """
        更新卫星角度

        :param t: 时隙
        :return:
        """
        if self.orbit == -1:
            self.angle = (self.initial_angle + ROTATIONAL_ANGULAR_VELOCITY * t * TIME_SLOT_LENGTH) % 360
            self.node_pos = [0.5 * math.sin(math.radians(self.angle)), 0.5 * math.cos(math.radians(self.angle))]
        else:
            self.angle = (self.initial_angle + getAngularVelocity(self.altitude) * t * TIME_SLOT_LENGTH) % 360
            self.node_pos = [(self.orbit + 2) * math.sin(math.radians(self.angle)),
                             (self.orbit + 2) * math.cos(math.radians(self.angle))]

    def hasVNF(self, vnf):
        """
        判断vnf是否在处理队列中:

        :param vnf:
        :return:
        """

        return self.process_dict.__contains__(vnf.get_vnf_no())

    def occupyResource(self, vnf, data_size, t):
        """
        添加vnf，资源充足则成功加入

        :param vnf: vnf
        :param data_size: 数据大小
        :param t: 到达时隙
        :return:
        """
        if self.orbit == -1:
            return False
        req_resource = vnf.getReqResource(data_size)
        # print("剩余资源", self.getRemainResource(t), "需求资源", req_resource, "资源", self.compute_resource)
        if self.getRemainResource() >= req_resource:
            self.remain_resource -= req_resource
            return True
        else:
            return False

    def addVNF(self, vnf, data_size, t):
        """
        添加vnf，资源充足则成功加入

        :param vnf: vnf
        :param data_size: 数据大小
        :param t: 到达时隙
        :return:
        """
        if self.orbit == -1:
            return False
        req_resource = vnf.getReqResource(data_size)
        self.process_dict[vnf.get_vnf_no()] = vnf
        self.resource_dict[vnf.get_vnf_no()] = req_resource
        self.end_time_dict[vnf.get_vnf_no()] = math.ceil(self.getProcessDelay(vnf, data_size) / TIME_SLOT_LENGTH) + t

    def finishVNF(self, vnf):
        """
        vnf结束，释放资源

        :param vnf:
        :return:
        """
        vnf_no = vnf.get_vnf_no()
        self.process_dict.pop(vnf_no)
        self.remain_resource += self.resource_dict.pop(vnf_no)
        self.end_time_dict.pop(vnf_no)

    def isFinishVNF(self, vnf, t):
        """
        vnf是否结束

        :param vnf: vnf
        :param t: 时隙
        :return:
        """
        if t >= self.end_time_dict[vnf.get_vnf_no()]:
            return True
        return False

    def getRemainResource(self):
        return self.remain_resource

    # def getRemainResource(self, t):
    #     """
    #     获取t时隙的剩余资源
    #
    #     :param t:
    #     :return:
    #     """
    #     if self.orbit == -1:
    #         return 0
    #     remain_resource = self.compute_resource
    #     # print("当前卫星", self.node_no, "总资源:", self.compute_resource, "里面有vnf", len(self.process_dict.keys()))
    #     for vnf_no in self.process_dict.keys():
    #         if t < self.end_time_dict.get(vnf_no):
    #             vnf = self.process_dict.get(vnf_no)
    #             data_size = self.datasize_dict.get(vnf_no)
    #             remain_resource -= vnf.getReqResource(data_size)
    #     return remain_resource

    def getUnitProcessRate(self):
        if self.orbit == -1:
            return -1
        else:
            return self.unit_process_rate
