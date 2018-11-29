#coding: utf-8
import multiprocessing
import time

import gc
import pandas as pd
import sys
import jieba
import jieba.posseg as pseg
from collections import defaultdict

from sqlalchemy import create_engine

jieba_path = "/Users/mazhen01/Documents/work/py_git/bigdata-casebase/etc/product.txt"
def _set_jieba():
    """
    加载结巴词库
    :return: None
    """
    jieba.set_dictionary(jieba_path)

    with open(jieba_path, "r") as file_to_read:
        lines = file_to_read.readlines()
        for line in lines:
            word, _, flag = line.strip('\r\n').split(' ')
            jieba.add_word(word, tag=flag)

def func(msg):
    print "msg:", msg
    # try:
    #     pd.read_pickle("/Users/mazhen01/Documents/work/py_git/bigdata-casebase/etc/product.txt")
    # except Exception as ex:
    #     print ex
    #     print "error"
    time.sleep(10)
    print "end"
    return msg


def test_m():
    products = pd.read_pickle('products')
    products.reset_index(drop=True, inplace=True)
    products.fillna('', inplace=True)
    print(sys.getsizeof(products))
    # combinations = get_combinations(len(products))
    n = len(products)
    # combinations = [(i, j) for i in xrange(n - 1) for j in xrange(i + 1, n)]

    pool = multiprocessing.Pool(processes=10)
    combinations = list()
    result_list = list()
    size = 1000000
    for i in range(n-1):
        for j in range(i + 1, n):
            combinations.append((i, j))
            if len(combinations) > size:
                msg = "hello %d" %(i)
                result_list.append(pool.apply_async(func, (msg, )))   #维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去
                combinations = list()

    pool.close()
    pool.join()


    print(len(combinations))
    print(sys.getsizeof(combinations))
    gc.collect()
    for k, _ in locals().items():
        print(k, sys.getsizeof(eval(k)))

    exit(0)


def test_type():
    _set_jieba()
    article_df = pd.read_pickle('article_df')
    article_vector = list()
    for i, row in article_df.iterrows():
        temp = {'commodity_id': '3-' + str(row['id']), 'commodity_name': row['heading']}
        #words = pseg.cut(row['heading'], HMM=False)
        #words = pseg.cut(row['content'], HMM=False)
        head = row['heading']
        words = pseg.cut(head.decode('utf8') + row['content'], HMM=False)
        label_class = defaultdict(set)
        for w in words:
            if w.flag in ['nyy', 'nks', 'nys', 'njb', 'nbz']:
                label_class[w.flag].add(w.word)
        for k, v in label_class.items():
            temp[k] = '&'.join(v)
        article_vector.append(temp)
    article_vector = pd.DataFrame(article_vector)
    article_vector.rename(
        columns = {
            'nyy': 'hospital_flag',
            'nks': 'department_flag',
            'nys': 'doctor_flag',
            'njb': 'disease_flag',
            'nbz': 'symptom_flag'},
        inplace=True)
    article_vector.loc[:, 'commodity_type'] = 3
    print "11"


def test_semaphore():
    # pool = multiprocessing.Pool(processes=3)
    # for i in xrange(30):
    #     msg = "hello %d" %(i)
    #     pool.apply_async(func_s, (msg, ))   #维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去
    #     # sem.acquire()
    #     print(">>>>>>>")

    sem = multiprocessing.Semaphore(5)
    for i in xrange(30):
        msg = "hello %d" % (i)
        p = multiprocessing.Process(target=func_s, args=(msg, sem))
        p.start()
        print ">>>>>"
        sem.acquire()


    print "Mark~ Mark~ Mark~~~~~~~~~~~~~~~~~~~~~~"
    # pool.close()
    # pool.join()   #调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    print "Sub-process(es) done."


def func_s(msg, sem):
    print "msg:", msg
    # try:
    #     pd.read_pickle("/Users/mazhen01/Documents/work/py_git/bigdata-casebase/etc/product.txt")
    # except Exception as ex:
    #     print ex
    #     print "error"
    time.sleep(10)
    print "end"
    sem.release()
    return msg


if __name__ == "__main__":
    # test_type()
    # test_m()
    test_semaphore()

    # pool = multiprocessing.Pool(processes=3)
    # for i in xrange(30):
    #     msg = "hello %d" %(i)
    #     pool.apply_async(func, (msg, ))   #维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去
    #     print("++++++")
    #
    # print "Mark~ Mark~ Mark~~~~~~~~~~~~~~~~~~~~~~"
    # pool.close()
    # pool.join()   #调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    # print "Sub-process(es) done."