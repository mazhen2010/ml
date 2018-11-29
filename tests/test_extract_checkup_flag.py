# coding=utf-8

"""
体检标签提取测试
"""
from recommend import extract_checkup_flag


def test_save_mysql():
    flag_dict = dict()
    flag_dict["commodity_id"] = "2-{0}".format(1)
    flag_dict["commodity_name"] = "test"
    flag_dict["commodity_type"] = 2
    flag_dict["hospital_flag"] = "hospital"
    flag_dict["disease_flag"] = "disease"
    flag_dict["symptom_flag"] = "symptom"

    flag_list = list()
    flag_list.append(flag_dict)
    extract_checkup_flag._save_flag(flag_list)


if __name__ == "__main__":
    test_save_mysql()