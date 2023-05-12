from NFV.properties import *


def process(sec, req, time_solt):
    # 每个时隙里只干一件事
    sec.updateSEC(time_solt)
    # print("当前请求的id是", req.request_no, "当前的请求处于", req.current_index, "当前vnf处于", req.current_vnf_index, "起点是", req.source, "终点是", req.destination, "vnf长度是", req.service_chain.number_of_vnf)
    # print(req.route_path, req.service_chain_path)
    # 处理当前时隙内的请求
    if req.current_index >= len(req.route_path) - 1 and \
            req.current_vnf_index >= len(req.service_chain_path):
        # 到达目的地
        delay = time_solt - req.process_timeslot + 1
        req.is_finish = True
        req.finish_timeslot = time_solt
        sec.finishReq(req)
        # print(req.request_no, "已到达")
        # print('-----------------------------')
        # print((delay - 1) * TIME_SLOT_LENGTH)
    elif req.current_vnf_index >= len(req.service_chain_path) or \
            (req.route_path[req.current_index] !=
             req.service_chain_path[req.current_vnf_index]
             and req.current_index < len(req.route_path) - 1):
        # 请求转发
        # 判断当前是否能进行传输
        current_node = req.route_path[req.current_index]
        next_node = req.route_path[req.current_index + 1]
        # print("当前节点", current_node, "下一个结点", next_node, "当前节点的临近结点",
        #       sec.sec_graph[current_node])
        if sec.sec_graph.has_edge(current_node, next_node):
            # 判断转发动作能否在一个时隙内完成
            distance = sec.sec_graph[current_node][next_node]["distance"]
            # tran_delay = req.data_size / BANDWIDTH + distance / C
            tran_delay = distance / C
            # if tran_delay >= TIME_SLOT_LENGTH:
            #     # print("时隙长度是", TIME_SLOT_LENGTH, "你的传输延迟是", tran_delay)
            if tran_delay <= TIME_SLOT_LENGTH:
                # print("从", current_node, "转发到", next_node, " 传输延迟是", tran_delay)
                # 如果可以
                req.tran_delay += tran_delay
                req.request_forward()
        # else:
        #     # print(current_node, next_node, "之间没边，此刻时隙是：", time_solt)
    else:
        # 处理vnf
        vnf = req.get_current_vnf()
        sate = req.service_chain_path[req.current_vnf_index]
        sate = sec.getNode(sate)
        # 如果不存在
        if not sate.hasVNF(vnf):
            # 加入vnf
            sate.addVNF(vnf, req.data_size, time_solt)
        # 如果存在，处理此请求的vnf
        else:
            if sate.isFinishVNF(vnf, time_solt):
                proc_delay = sate.getProcessDelay(vnf, req.data_size)
                # print("处理延迟是", proc_delay, "此时请求处于", req.route_path[req.current_index])
                # 如果够结束请求
                req.current_vnf_index += 1
                req.proc_delay += proc_delay
                # 释放资源
                # sate.finishVNF(vnf, req.data_size)
