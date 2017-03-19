from math import modf

"""Misc helper functions"""


def number_to_string_with_stepsize(value, decimals, stepsize):

    steps = round(value / stepsize)
    stepped_value = steps * stepsize
    after_the_point, before_the_point = modf(stepped_value)

    after_the_point = abs(after_the_point * (10 ** decimals))

    return "{}.{}".format(int(before_the_point), int(after_the_point))
