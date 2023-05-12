import math
from NFV.properties import *


def lawOfCosines(side1, side2, angle):
    """
    余弦定理

    :param side1: a
    :param side2: b
    :param angle: angle C, degree
    :return:c
    """
    return math.sqrt(side1 * side1 + side2 * side2 -
                     2 * side1 * side2 * math.cos(math.radians(angle)))


def lawOfSine(side1, side2, angle2):
    """
    正弦定理

    :param side1: a
    :param side2: b
    :param angle2: angle B
    :return: angle A, degree
    """
    return math.degrees(math.asin(side1 * math.sin(math.radians(angle2)) / side2))


def getAngularVelocity(altitude):
    """
    计算角速度

    :param altitude: the altitude of LEO satellite.
    :return: the angular velocity.
    """
    # pow(10,6) km->m and radius^3
    return math.degrees(math.sqrt(G * EARTH_MASS /
                                  pow((RADIUS + altitude) * pow(10, 3), 3)))



