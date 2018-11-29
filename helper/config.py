# coding=utf-8

import ConfigParser
import os

conf = ConfigParser.ConfigParser()
# conf_path = "/Users/mazhen01/Documents/work/py_git/bigdata-casebase/env/dev/sys_dev.conf"
conf_path = "/home/mazhen/casebase/env/dev/sys_dev.conf"
env_path = os.environ.get('ml_conf')
if env_path is not None:
    conf_path = env_path
conf.read(conf_path)


def get_config(section, option):
    """
    获取指定配置信息
    :param section:
    :param option:
    :return: 配置信息
    """
    return conf.get(section=section, option=option)