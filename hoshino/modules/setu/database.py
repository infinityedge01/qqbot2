import sqlite3
import os
import time
import pickle
import sys
class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        db_exists = os.path.exists(os.path.join(
            db_path, "setu.db"))
        db_conn = sqlite3.connect(os.path.join(
            db_path, "setu.db"))
        self.db = db_conn.cursor()
        if not db_exists:
            self.db.execute(
                '''CREATE TABLE Data(
                qqid INT PRIMARY KEY,
                day_setu INT,
                day_contrib INT,
                total_setu INT,
                total_contrib INT,
                last_day CHARACTER(4))''')
            self.db.execute(
                '''CREATE TABLE Total_Data(
                time INT PRIMARY KEY,
                day_setu INT,
                day_contrib INT,
                day_msg INT,
                total_setu INT,
                total_contrib INT,
                total_msg INT,
                last_day CHARACTER(4))''')
        db_conn.commit()
        db_conn.close()
    def update_setu(self, qqid: int):
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "setu.db"))
        self.db = db_conn.cursor()
        today = time.strftime("%m%d")
        sql_info = list(self.db.execute(
            "SELECT qqid, day_setu, day_contrib, total_setu, total_contrib, last_day FROM Data WHERE qqid=?", (qqid,)))
        mem_exists = (len(sql_info) == 1)
        if mem_exists:
            day_setu, day_contrib, total_setu, total_contrib, last_day = sql_info[0][1:]
        else:
            day_setu, day_contrib, total_setu, total_contrib, last_day = 0, 0, 0, 0, ""
        if today != last_day:
            day_setu = 0
            day_contrib = 0
        day_setu += 1
        total_setu += 1
        last_day = today
        if mem_exists:
            self.db.execute("UPDATE Data SET day_setu=?, day_contrib=?, total_setu=?, total_contrib=?, last_day=? WHERE qqid=?",
                       (day_setu, day_contrib, total_setu, total_contrib, last_day, qqid))
        else:
            self.db.execute("INSERT INTO Data (qqid,day_setu,day_contrib,total_setu,total_contrib,last_day) VALUES(?,?,?,?,?,?)",
                       (qqid, day_setu, day_contrib, total_setu, total_contrib, last_day))
        db_conn.commit()
        db_conn.close()
    
    def update_total_setu(self, ttime: int, num: int):
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "setu.db"))
        self.db = db_conn.cursor()
        today = time.strftime("%m%d")
        sql_info = list(self.db.execute(
            "SELECT time, day_setu, total_setu, last_day FROM Total_Data ORDER BY total_setu DESC,last_day DESC,time DESC limit 0,5"))
        #sql_info = list(self.db.execute(
        #    "SELECT time, day_setu, total_setu, last_day FROM Total_Data WHERE time=?", ((ttime + 143) % 144 ,)))
        mem_exists = (len(sql_info) != 0)
        if mem_exists:
            day_setu, total_setu, last_day = sql_info[0][1:]
        else:
            day_setu, total_setu, last_day = 0, 0, ""
        print(day_setu, total_setu, last_day, sql_info)
        if today != last_day:
            day_setu = 0
        day_setu += num
        total_setu += num
        last_day = today
        sql_info = list(self.db.execute(
            "SELECT time, day_setu, total_setu, last_day FROM Total_Data WHERE time=?", (ttime ,)))
        mem_exists = (len(sql_info) == 1)
        print(ttime, mem_exists)
        if mem_exists:
            self.db.execute("UPDATE Total_Data SET day_setu=?, total_setu=?, last_day=? WHERE time=?",
                       (day_setu, total_setu, last_day, ttime))
        else:
            self.db.execute("INSERT INTO Total_Data (time,day_setu,day_contrib,day_msg,total_setu,total_contrib,total_msg,last_day) VALUES(?,?,?,?,?,?,?,?)",
                       (ttime, day_setu, 0, 0, total_setu, 0, 0, last_day))
        db_conn.commit()
        db_conn.close()
    