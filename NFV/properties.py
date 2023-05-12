# 地球质量 kg
EARTH_MASS = 5.965 * pow(10, 24)
# 万有引力常量 G = 6.67×10^(-11) m^3/(kg*s^2)
G = 6.67 * pow(10, -11)
# 地球半径 6371km.
RADIUS = 6371
# 光速 km/s
C = 3 * pow(10, 5)
# 卫星覆盖角 °
COVER_ANGLE = 120
# 地球自转速度 °/s
ROTATIONAL_ANGULAR_VELOCITY = 4.178 * pow(10, -3)

# 基站数量
STATION_NUM = 4
# 轨道数量
ORBIT_NUM = 4
# 每个轨道卫星数量
MIN_ORBIT_SATELLITE_NUM = 7
MAX_ORBIT_SATELLITE_NUM = 15
# 带宽 MB/s
BANDWIDTH = 100
# 传输成本 dollar/MB
TRANSMISSION_COST = 0.01 / 1000

# 时隙长度 s
TIME_SLOT_LENGTH = 0.03

# 请求数据大小 MB
DATA_SIZE = [10, 20, 30, 40, 50]
# vnf数量
SERVICE_CHAIN_LENGTH = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
# vnf需求单位计算资源 unit/100MB
REQUIRED_COMPUTE_RESOURCE = [1, 2, 3, 4, 5, 6]
# 每计算单元处理速度 MB/s
UNIT_PROCESS_RATE = [200, 250, 300, 400]
# 每单位资源使用成本 dollar/unit
UNIT_PROCESS_COST = [0.0253, 0.04493, 0.08987, 0.17973]
# 实例化成本 dollar
VNF_INSTANTIATION_COST = [[0.01, 0.02, 0.03, 0.04, 0.05, 0.06],
                          [0.015, 0.025, 0.035, 0.045, 0.055, 0.065],
                          [0.02, 0.03, 0.04, 0.05, 0.06, 0.07],
                          [0.025, 0.035, 0.045, 0.055, 0.065, 0.075]]
# 卫星计算资源 unit
COMPUTE_RESOURCE = [64, 48, 32, 16]

