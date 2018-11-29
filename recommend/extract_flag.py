#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author zhen.ma
import sys
sys.path.append("/home/mazhen/casebase/")
import jieba
import jieba.posseg as pseg
from impala.dbapi import connect
from impala.util import as_pandas
import pandas as pd
from collections import defaultdict
import re
from extract_checkup_flag import extract_checkup_flag
from sqlalchemy import create_engine
import pymysql
import time
import logbook
from helper.config import get_config

logbook.StderrHandler(bubble=True).push_application()
logbook.TimedRotatingFileHandler(get_config("log", "extract_flag"),
                                 backup_count=7, bubble=True).push_application()
logger = logbook.Logger("flag_extract")

jieba_path = get_config("jieba", "path")


def save_to_mysql(df, table='r_commodity_flag'):
    engine = create_engine(get_config("recommend", "full_path"))
    pd.io.sql.to_sql(df, table, con=engine, index=False, if_exists='append')


def impala_db(hive_sql):
    conn = connect(
        host=get_config("impala", "host"),
        port=get_config("impala", "port"),
        database=get_config("impala", "database"),
        auth_mechanism='PLAIN')
    curl = conn.cursor()
    curl.execute(hive_sql)
    return as_pandas(curl)


def set_jieba():
    jieba.set_dictionary(jieba_path)
    
    with open(jieba_path, 'r') as file_to_read:
        lines = file_to_read.readlines()
        for line in lines:
            word, _, flag = line.strip('\r\n').split(' ')
            jieba.add_word(word, tag=flag)


def content_wash(content):
    get_re = re.compile(u'([\u4e00-\u9fa5]+)') 
    get_corpus = re.findall(get_re, str(content).decode('utf8'))
    return ','.join(get_corpus)


def get_article_vector():

    # 获取文章数据
    sql = 'select'
    article_df = impala_db(sql)
    article_df.loc[:, 'content'] = article_df['content'].apply(content_wash)
    #article_df.to_pickle('article_df')
    #article_df = pd.read_pickle('article_df')
    logger.info(article_df.head())

    article_vector = list()
    article_vector.loc[:, 'commodity_type'] = 3
    save_to_mysql(article_vector)
    article_vector.to_pickle('article_vector')
    article_vector.to_csv('article_vector.csv', encoding='utf8')


def _delete_all_data():
    """
    清除数据
    :return: None
    """
    try:
        conn = pymysql.connect(
            host=get_config("recommend", "host"),
            port=int(get_config("recommend", "port")),
            db=get_config("recommend", "db"),
            user=get_config("recommend", "user"),
            passwd=get_config("recommend", "passwd"),
            charset='utf8')
        cursor = conn.cursor()

        try:
            cursor.execute("delete")
            conn.commit()
        except Exception as ex:
            logger.exception(ex)
            print ex
            conn.rollback()

        cursor.close()
        conn.close()
    except Exception as ex:
        logger.exception(ex)
        print ex


if __name__ == '__main__':
    start_time = time.time()
    # extract labels
    set_jieba()
    _delete_all_data()
    logger.info("_delete_all_data end. cost:{0}", time.time() - start_time)
    get_article_vector()
    logger.info("get_article_vector end. cost:{0}", time.time() - start_time)
    extract_checkup_flag()
    logger.info("label extract end. cost:{0}", time.time() - start_time)
