# coding=utf-8
# Author zhen.ma

"""
体检商品标签提取
"""
import sys
sys.path.append("../")
import logbook
import jieba
import jieba.posseg as pseg
from impala.dbapi import connect
import pymysql
from helper.config import get_config


logger = logbook.Logger("checkup_flag_extract")
jieba_path = get_config("jieba", "path")


def extract_checkup_flag():
    """
    提取体检商品标签
    :return: None
    """
    # checkup_list = _get_checkup_data_from_mysql()
    checkup_list = _get_checkup_data_from_impala()
    flag_list = _extract_flag(checkup_list)
    _save_flag(flag_list)
    print "extract_checkup_flag end."


def _get_checkup_data_from_impala():
    """
    获取全部体检商品
    :return: 体检商品
    """
    try:
        conn = connect(
            host=get_config("impala", "host"),
            port=get_config("impala", "port"),
            database=get_config("impala", "database"),
            auth_mechanism="PLAIN")
        cursor = conn.cursor()
        cursor.execute('''select ''')
        checkup_list = cursor.fetchall()
        cursor.close()
        conn.close()
        return checkup_list
    except Exception as ex:
        logger.exception(ex)


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


def _extract_flag(checkup_list):
    """
    抽取疾病和症状标签
    :param checkup_list:
    :return: 标签集合
    """
    flag_list = list()
    for row in checkup_list:
        flag_dict = dict()
        flag_dict["commodity_id"] = "2-{0}".format(row[0])
        flag_dict["commodity_name"] = row[1]
        flag_dict["commodity_type"] = 2
        flag_dict["hospital_flag"] = row[2]
        disease_list = set()
        symptom_list = set()
        if row[1] is not None:
            name_words = pseg.cut(row[1])
            for word in name_words:
                if word.flag == "njb":
                    disease_list.add(word.word.encode("utf-8"))
                if word.flag == "nbz":
                    symptom_list.add(word.word.encode("utf-8"))

        if row[3] is not None:
            item_words = pseg.cut(row[3])
            for word in item_words:
                if word.flag == "njb":
                    disease_list.add(word.word.encode("utf-8"))
                if word.flag == "nbz":
                    symptom_list.add(word.word.encode("utf-8"))

        if row[4] is not None:
            intro_words = pseg.cut(row[4])
            for word in intro_words:
                if word.flag == "njb":
                    disease_list.add(word.word.encode("utf-8"))
                if word.flag == "nbz":
                    symptom_list.add(word.word.encode("utf-8"))

        flag_dict["disease_flag"] = "&".join(disease_list)
        flag_dict["symptom_flag"] = "&".join(symptom_list)
        flag_list.append(flag_dict)
    return flag_list


def _save_flag(flag_list):
    """
    保存标签
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
            for flag_dict in flag_list:
                insert_sql = '''replace into r_commodity_flag() values("{0}", "{1}", {2}, "{3}", "{4}", "{5}")'''\
                    .format(flag_dict["0"], flag_dict["1"], flag_dict["2"],
                            flag_dict["3"], flag_dict["4"], flag_dict["5"])
                cursor.execute(insert_sql)
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


if __name__ == "__main__":
    _set_jieba()
    extract_checkup_flag()
