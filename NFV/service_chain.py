import math
from random import *

from faker import Faker
from NFV.properties import *

fk = Faker()
Faker.seed(25)


class VNF:
    required_compute_resource = 0
    vnf_no = ""
    vnf_kind = 0

    def __init__(self):
        """
        随机生成VNF

        """
        self.vnf_no = str(fk.unique.pystr())
        self.vnf_kind = randint(0, len(REQUIRED_COMPUTE_RESOURCE) - 1)
        self.required_compute_resource = REQUIRED_COMPUTE_RESOURCE[self.vnf_kind]

    def getReqUnitResource(self):
        """
        获取vnf处理单位数据所需的计算资源

        :return: 单位计算资源
        """
        return self.required_compute_resource

    def getReqResource(self, b):
        """
        获取所需资源

        :param b: 数据大小
        :return:
        """
        return math.ceil(self.getReqUnitResource() * (b / 100))

    def get_vnf_no(self):
        """
        返回vnf编号

        :return: 返回vnf编号
        """
        return self.vnf_no

    def __str__(self):
        return "vnf_no:" + self.vnf_no + " required_compute_resource" + str(self.required_compute_resource)


class ServiceChain:

    def __init__(self, number_of_vnf=0):
        """

        :param number_of_vnf: vnf数量
        """
        self.vnf_lists = []
        self.number_of_vnf = number_of_vnf
        for i in range(number_of_vnf):
            self.vnf_lists.append(VNF())

    def getSumReqUnitResource(self):
        """
        返回服务链总体处理单位数据所需计算资源

        :return: 服务链所需单位计算资源
        """
        sum_resource = 0
        for vnf in self.vnf_lists:
            sum_resource += vnf.getReqUnitResource()

        return sum_resource

    def get_vnf(self, index):
        """
        获取vnf

        :param index:
        :return:
        """
        if index >= len(self.vnf_lists) or index < 0:
            return
        else:
            return self.vnf_lists[index]

    def get_min_req_resource(self):
        """
        找需求资源最少的VNF

        :return:
        """
        min_resource = 10000
        vnf_min = None
        for vnf in self.vnf_lists:
            if min_resource > vnf.getReqUnitResource():
                min_resource = vnf.getReqUnitResource()
                vnf_min = vnf
        return vnf_min

    def get_max_req_resource(self):
        """
        找需求资源最多的VNF

        :return:
        """
        max_resource = -1
        vnf_max = None
        for vnf in self.vnf_lists:
            if max_resource < vnf.getReqUnitResource():
                max_resource = vnf.getReqUnitResource()
                vnf_max = vnf
        return vnf_max
