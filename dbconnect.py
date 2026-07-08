import pymysql
import numpy as np

def dbconnect_iced():
    #dbc = pymysql.connect(host='localhost',user='reader',password='beryllium-10',database='iced')
   
    dbc = pymysql.connect(host='34.73.248.9', user='reader', password='beryllium-10',database='iced')

    return dbc

def dbconnect_radci():
    #dbc = pymysql.connect(host='localhost',user='reader',password='beryllium-10',database='iced')
   
    dbc = pymysql.connect(host='34.28.9.226', user='reader', password='carbon-14',database='mines')

    return dbc

def querier_iced(input):
    dbc = dbconnect_iced()
    dbcursor = dbc.cursor()

    query = input

    dbcursor.execute(query)
   
    header = [column[0] for column in dbcursor.description]
    result = dbcursor.fetchall()
    headed_result = [header] + list(result)
   
    dbcursor.close
    dbc.close
   
    result_list = np.array(headed_result)

    return result_list

def querier_radci(input):
    dbc = dbconnect_radci()
    dbcursor = dbc.cursor()

    query = input

    dbcursor.execute(query)
   
    header = [column[0] for column in dbcursor.description]
    result = dbcursor.fetchall()
    headed_result = [header] + list(result)
   
    dbcursor.close
    dbc.close
   
    result_list = np.array(headed_result)

    return result_list