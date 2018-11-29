# coding=utf-8

"""
全局锁
"""

import redis
import time
import logbook
from contextlib import contextmanager
from config import get_config

LOCK_EXPIRES = 600
CACHE_EXPIRES = 2 * 3600
DEFAULT_RETRIES = 3
logger = logbook.Logger("redis")
con_pool = redis.BlockingConnectionPool(
                max_connections=int(get_config("redis", "max_cons")),
                host=get_config("redis", "host"),
                port=int(get_config("redis", "port")),
                db=int(get_config("redis", "db")),
                password=get_config("redis", "passwd"))


def redis_client():
    """
    获得redis链接
    :return: redis链接
    """
    return redis.Redis(connection_pool=con_pool)


@contextmanager
def dist_lock(key):
    """
    全局加锁
    :param key:
    :return: with执行加锁
    """
    lock_key, cache_key = _generate_key(key)
    has_lock = False
    has_error = False
    try:
        has_lock = bool(_acquire_lock(lock_key))
        yield has_lock
    except BaseException as ex:
        has_error = True
        # logger.exception(ex.message)
        raise ex
    finally:
        if not has_error:
            _set_cache(cache_key)
        if has_lock:
            _release_lock(lock_key)


def is_expired(key):
    """
    key是否已失效
    :param key:
    :return: 失效：true，未失效：False
    """
    lock_key, cache_key = _generate_key(key)
    update_time = redis_client().get(cache_key)
    if update_time is not None:
        return False

    return True


def _set_cache(key):
    """
    设置缓存key
    :param key:
    :return:
    """
    redis_client().set(key, time.time(), ex=CACHE_EXPIRES)


def _generate_key(key):
    """
    生成redis的key
    :param key: 原始key
    :return: 关键字key
    """
    return 'lock_quant_%s' % key, 'cache_quant_%s' % key


def _acquire_lock(key):
    """
    获取全局锁
    :param key:
    :return:
    """
    run_times = 0
    while run_times < DEFAULT_RETRIES:
        if redis_client().set(key, time.time(), ex=LOCK_EXPIRES, nx=True):
            return True
        else:
            time.sleep(0.03)
        run_times = run_times + 1

    return False


def _release_lock(key):
    """
    释放全局锁
    :param key: 锁key
    :return: None
    """
    redis_client().delete(key)

