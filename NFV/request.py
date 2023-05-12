import math

from NFV.service_chain import *


def generateRequests(sec, num=1, t=0, max_service_chain_length=10):
    """
    随机生成请求

    :param max_service_chain_length: 服务链最大长度
    :param sec: sec
    :param num: 请求数量
    :param t: 时隙
    :return:
    """
    requests = []
    for i in range(num):
        req_no = t * 10000 + i
        source = str(randint(0, sec.station_num - 1))
        destination = str(randint(0, sec.station_num + sec.satellite_num - 1))
        while destination == source:
            destination = str(randint(0, sec.station_num + sec.satellite_num - 1))
        data_size = DATA_SIZE[randint(0, len(DATA_SIZE) - 1)]
        service_chain_length = randint(5, max_service_chain_length)
        arrive_time = t
        requests.append(Request(req_no, source, destination, data_size, service_chain_length, arrive_time))
    return requests


class Request:
    request_no = -1
    source = ""
    destination = ""
    data_size = -1
    # 请求到达时隙
    arrive_timeslot = -1
    # 开始处理的时隙
    process_timeslot = -1
    # 结束时隙
    finish_timeslot = -1
    # 当前请求所处节点
    current_index = 0
    # 当前vnf所处节点
    current_vnf_index = 0
    route_path = []
    service_chain_path = []
    # 等待时隙
    wait_timeslot = 0
    # 容忍延迟
    tolerance_delay = 1
    # 成本预算
    budget = 50
    # 到达目的地
    is_finish = False
    # 传输延迟
    tran_delay = 0
    # 处理延迟
    proc_delay = 0
    # 成本
    sum_cost = 0

    def __init__(self, request_no, source, destination, data_size, service_chain_length, arrive_timeslot):
        self.request_no = request_no
        self.source = source
        self.destination = destination
        self.data_size = data_size
        self.service_chain = ServiceChain(service_chain_length)
        self.arrive_timeslot = arrive_timeslot

    def getSumReqResource(self):
        """
        获取请求所需的计算资源量

        :return: 计算资源量
        """
        return math.ceil(self.service_chain.getSumReqUnitResource() * (self.data_size / 100))

    def set_route_path(self, path):
        """
        设置请求转发路径

        :param path: 节点路径
        :return:
        """
        self.route_path = path

    def set_service_chain_path(self, path):
        """
        设置服务链放置路径

        :param path: 放置路径
        :return:
        """
        self.service_chain_path = path

    def get_route_path(self):
        """
        获取请求转发路径

        :return: 请求转发路径
        """
        return self.route_path

    def get_service_chain_path(self):
        """
        获取服务链放置路径

        :return: 服务链放置路径
        """

        return self.service_chain_path

    def request_forward(self):
        """
        请求前进，如果到达目的地了，则返回False

        :return: 布尔值
        """

        self.current_index += 1
        if self.current_index >= len(self.route_path):
            return False

    def request_wait(self):
        """
        请求在当前节点等待转发

        :return:
        """
        return

    def get_current_vnf(self):
        """
        获取当前vnf

        :return:
        """
        return self.service_chain.get_vnf(self.current_vnf_index)

    def __str__(self):
        return f"请求编号是：{self.request_no}，源是：{self.source}，目的地是：{self.destination}，" \
               f"请求到达时隙是：{self.arrive_timeslot}，数据大小是：{self.data_size}，服务链长度是：{self.service_chain.number_of_vnf}，" \
               f"路由路径是：{self.route_path}，vnf放置路径是：{self.service_chain_path}"
