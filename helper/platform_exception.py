# coding=utf-8

"""
平台的各种自定义异常
"""


class TaskRunningError(Exception):
    """
    任务已经执行异常.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class NoFactorException(Exception):
    """
    数据库没有因子数据异常.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class NoStockException(Exception):
    """
    数据库没有股票数据异常.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class DateRange12Exception(Exception):
    """
    所选日期范围过小不足以计算12期数据异常.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class DateRangeShortException(Exception):
    """
    所选日期范围过小不足以计算IC相关数据异常.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
