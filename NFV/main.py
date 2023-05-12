import time

import networkx as nx
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from NFV.processor import process
from NFV.properties import TIME_SLOT_LENGTH
from NFV.request import generateRequests
from NFV.sec_network import generateSECRandomly
from algorithm.auxiliary_algorithm import auxiliaryGraph

if __name__ == '__main__':
    satellite_num = int(input("Please input maximum number of satellites per orbit (n > 6):"))
    while satellite_num <= 6:
        satellite_num = int(input("Please enter a number greater than 6:"))

    chain_length = int(input("Please input maximum number of VNFs (n > 4):"))
    while chain_length <= 4:
        chain_length = int(input("Please enter a number greater than 4:"))

    request_num = int(input("Please input number of requests (n > 0):"))
    while request_num <= 0:
        request_num = int(input("Please enter a number greater than 0:"))

    sec = generateSECRandomly(satellite_num)
    reqs = generateRequests(sec, request_num, 0, chain_length)
    sec_temp = sec.deepCopy()

    nx.draw_networkx(sec.sec_graph, pos=sec.pos)
    plt.savefig(str(time.time()) + ".png")

    for req_index in range(len(reqs)):
        time_solt = 0
        s_time = time.time()
        auxiliaryGraph(sec, reqs[req_index], time_solt, 0.5, 0.5)
        e_time = time.time()

        while not reqs[req_index].is_finish:
            process(sec, reqs[req_index], time_solt)
            time_solt += 1

        sec = sec_temp.deepCopy()
        print("request", req_index, "VNF num:", reqs[req_index].service_chain.number_of_vnf,
              "source:", reqs[req_index].source, "destination", reqs[req_index].destination,
              " route path:", reqs[req_index].route_path, " SFC:", reqs[req_index].service_chain_path,
              " delay:", time_solt * TIME_SLOT_LENGTH, " cost:", reqs[req_index].sum_cost,
              " running time:", e_time - s_time
              )

    input("Press Enter to exit...")
