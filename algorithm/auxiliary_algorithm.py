import copy
import networkx as nx
from NFV.properties import *


def auxiliaryGraph(sec, request, t, xi, fai):
    auxiliary_graph = nx.DiGraph()
    source_node = request.source
    layer2_nodes = []
    for slot in range(request.tolerance_delay):
        sec.updateSEC(t + slot)
        for sate in range(sec.orbit_satellite_num[0]):
            if sec.sec_graph.has_edge(source_node, str(sate + sec.station_num)):
                new_node = str(sate + sec.station_num) + '_' + str(t + slot)
                auxiliary_graph.add_node(new_node)

                distance = sec.sec_graph[source_node][str(sate + sec.station_num)]["distance"]
                tran_delay = distance / C

                tran_cost = request.data_size / 1024 * TRANSMISSION_COST
                auxiliary_graph.add_edge(source_node, new_node, delay=slot * TIME_SLOT_LENGTH + tran_delay,
                                         cost=tran_cost)
                layer2_nodes.append(new_node)

    sec.updateSEC(t)
    layer3_nodes = []
    layer3_orbits = []
    for orbit in range(sec.orbit_num):
        orbit_sum_resource = 0
        start_num = sec.station_num
        for o in range(orbit):
            start_num += sec.orbit_satellite_num[o]

        for sate in range(sec.orbit_satellite_num[orbit]):
            sate_resource = sec.node_dict.get(str(sate + start_num)).getRemainResource()
            orbit_sum_resource += sate_resource

        if orbit_sum_resource >= request.getSumReqResource():
            for sate in range(sec.orbit_satellite_num[orbit]):
                auxiliary_graph.add_node(str(sate + start_num))
                layer3_nodes.append(str(sate + start_num))
                layer3_orbits.append(orbit)

    if len(layer3_nodes) == 0:
        return

    for node2 in layer2_nodes:
        source = node2.split("_")[0]
        for node3 in layer3_nodes:
            shortest_path = nx.dijkstra_path(sec.sec_graph, source, node3, weight="distance")
            sum_tran_delay = nx.path_weight(sec.sec_graph, shortest_path, weight="distance") / C
            sum_tran_cost = request.data_size / 1024 * TRANSMISSION_COST * (len(shortest_path) - 1)
            auxiliary_graph.add_edge(node2, node3, delay=sum_tran_delay, cost=sum_tran_cost, path=shortest_path)

    dest_node = request.destination
    auxiliary_graph.add_node(dest_node)
    index = 0
    min_vnf = request.service_chain.get_min_req_resource()
    max_vnf = request.service_chain.get_max_req_resource()
    for orbit in layer3_orbits:
        max_proc_delay = -1
        max_proc_cost = -1
        distance = sec.sec_graph[layer3_nodes[0]][layer3_nodes[1]]["distance"]
        for sate in layer3_nodes[index: index + sec.orbit_satellite_num[orbit]]:
            if sec.node_dict.get(sate).getProcessDelay(min_vnf, request.data_size) > max_proc_delay:
                max_proc_delay = sec.node_dict.get(sate).getProcessDelay(min_vnf, request.data_size)
            if sec.node_dict.get(sate).getVirtualizationCost(max_vnf, request.data_size) > max_proc_cost:
                max_proc_cost = sec.node_dict.get(sate).getVirtualizationCost(max_vnf, request.data_size)

        delay_min = max_proc_delay * request.service_chain.number_of_vnf
        delay_max = delay_min + sec.orbit_satellite_num[orbit] * (request.data_size / BANDWIDTH + distance / C)
        cost_min = max_proc_cost * request.service_chain.number_of_vnf
        cost_max = cost_min + sec.orbit_satellite_num[orbit] * (request.data_size / 1024 * TRANSMISSION_COST)

        estimated_delay = (1 - xi) * delay_min + xi * delay_max
        estimated_cost = (1 - fai) * cost_min + fai * cost_max

        for sate in layer3_nodes[index: index + sec.orbit_satellite_num[orbit]]:
            shortest_path = nx.dijkstra_path(sec.sec_graph, sate, dest_node, weight="distance")
            sum_tran_delay = nx.path_weight(sec.sec_graph, shortest_path, weight="distance") / C + estimated_delay
            sum_tran_cost = request.data_size * TRANSMISSION_COST * (len(shortest_path) - 1) + estimated_cost
            auxiliary_graph.add_edge(sate, dest_node + "_d", delay=sum_tran_delay, cost=sum_tran_cost,
                                     path=shortest_path)

        index = index + sec.orbit_satellite_num[orbit]

    all_shortest_paths = nx.shortest_simple_paths(auxiliary_graph, source_node, dest_node + "_d", weight="delay")
    deploy_path = []
    orbit_route_path = []

    temp_node_dict = copy.deepcopy(sec.node_dict)
    for path in all_shortest_paths:
        sum_cost = nx.path_weight(auxiliary_graph, path, "cost")
        if sum_cost > request.budget:
            continue
        connecting_sate = path[2]
        orbit = sec.node_dict.get(connecting_sate).orbit
        orbit_node_num = sec.orbit_satellite_num[orbit]
        node_num = sec.station_num
        for o in range(orbit):
            node_num += sec.orbit_satellite_num[o]
        start_node = int(connecting_sate)
        real_sum_cost = 0
        for vnf in request.service_chain.vnf_lists:
            flag = False
            while 1:
                if str(start_node) not in orbit_route_path:
                    orbit_route_path.append(str(start_node))
                if sec.getNode(str(start_node)).occupyResource(vnf, request.data_size, t):
                    real_sum_cost += sec.getNode(str(start_node)).getVirtualizationCost(vnf, request.data_size)
                    deploy_path.append(str(start_node))
                    break
                else:
                    start_node = (start_node + 1 - node_num) % orbit_node_num + node_num
                    if start_node == int(connecting_sate):
                        sec.node_dict = copy.deepcopy(temp_node_dict)
                        deploy_path = []
                        orbit_route_path = []
                        flag = True
                        break
            if flag:
                break

        if len(deploy_path) != 0:
            request.set_service_chain_path(deploy_path)
            if len(orbit_route_path) <= orbit_node_num / 2:
                orbit_route_path += list(reversed(orbit_route_path))[1:]
            else:
                while len(orbit_route_path) != orbit_node_num + 1:
                    orbit_route_path.append(str((int(orbit_route_path[-1]) + 1 - node_num) % orbit_node_num + node_num))

            route_path = [path[0], path[1].split("_")[0]] + auxiliary_graph[path[1]][path[2]]["path"][
                                                            1:] + orbit_route_path[1:] + \
                         auxiliary_graph[path[2]][path[3]]["path"][1:]
            request.set_route_path(route_path)
            real_sum_cost += request.data_size * TRANSMISSION_COST * (len(route_path) - 1)
            request.sum_cost = real_sum_cost
            return


