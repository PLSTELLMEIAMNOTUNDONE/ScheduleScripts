from random import choice
from random import randrange
from random import random
import math


def temperature(t, i):
    return t / (0.005 * i)


def transition(energy, temp):
    probability = math.exp(-energy / temp)
    bound = random()
    return probability >= bound


def puff():
    return
