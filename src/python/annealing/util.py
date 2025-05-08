import math
from random import random
from typing import Callable

from src.python.schedule.config import temperature_hyper_enable, temperature_linear_enable

# !!!!!!!!!!
N = 4000
k = N / 10

# deprecated
def temperature_hyper(t, i):
    return t / (0.005 * i)


def temperature_linear(t, i):
    return max((N - i) / k, 0)


def get_temp_fun() -> Callable:
    if temperature_linear_enable:
        return temperature_linear
    elif temperature_hyper_enable:
        return temperature_hyper
    raise Exception("No temperature enable")


def get_transition_fun() -> Callable:
    if temperature_linear_enable:
        return transition_linear
    elif temperature_hyper_enable:
        return transition_hyper
    raise Exception("No transition enable")



def transition_hyper(energy, temp):
    probability = math.exp(-energy / temp)
    bound = random()
    return probability >= bound


def transition_linear(energy, temp):
    probability = math.exp(-energy / (k * temp))
    bound = random()
    return probability >= bound


def puff():
    return
