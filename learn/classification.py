# coding=utf-8

import jieba
import xlrd
from xlrd.book import Book
from xlrd.sheet import Sheet
from xlrd.sheet import Cell
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn import linear_model
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB


def regress():

    clf = linear_model.LinearRegression()
    X = [[0, 0, 1], [1, 1, 2], [2, 2, 3]]
    y = [0, 1, 2]
    clf.fit(X, y)
    print(clf.coef_)
    print(clf.intercept_)
    result = clf.predict([[2, 4, 6]])
    print(result)


def classify():
    stop_words = _readfile('/Users/mazhen01/Documents/work/benmu/stop_words').splitlines()
    workbook = xlrd.open_workbook('/Users/mazhen01/Documents/work/benmu/test_result.xlsx')
    # sheet_names = workbook.sheet_names()
    sheet = workbook.sheet_by_index(0)
    description = sheet.col_values(3, 1)
    label = sheet.col_values(1, 1)
    x_train, x_test, y_train, y_test = train_test_split(description, label, test_size=0.2, random_state=0)
    # print(description)

    vector_train = TfidfVectorizer(stop_words=stop_words, sublinear_tf=True, max_df=0.5)
    feature_train = vector_train.fit_transform(x_train)
    vector_test = TfidfVectorizer(sublinear_tf=True, max_df=0.5, vocabulary=vector_train.vocabulary_)
    feature_test = vector_test.fit_transform(x_test)

    # model = SVC(kernel='linear')
    model = MultinomialNB(alpha=0.001)
    model.fit(feature_train, y_train)

    y_true, y_pred = y_test, model.predict(feature_test)
    print(classification_report(y_true, y_pred))


def _readfile(path):
    with open(path, "rb") as fp:
        content = fp.read()
    return content


def main():
    """
    定义入口
    :return: None
    """
    # regress()
    classify()
    # pass


if __name__ == '__main__':
    main()