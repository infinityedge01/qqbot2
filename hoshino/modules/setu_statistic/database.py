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
    
    def update_total_msg(self, ttime: int, num: int):
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "setu.db"))
        self.db = db_conn.cursor()
        today = time.strftime("%m%d")
        sql_info = list(self.db.execute(
            "SELECT time, day_msg, total_msg, last_day FROM Total_Data ORDER BY total_msg DESC,last_day DESC,time DESC limit 0,5"))
        #sql_info = list(self.db.execute(
        #    "SELECT time, day_msg, total_msg, last_day FROM Total_Data WHERE time=?", ((ttime + 143) % 144 ,)))
        mem_exists = (len(sql_info) != 0)
        if mem_exists:
            day_msg, total_msg, last_day = sql_info[0][1:]
        else:
            day_msg, total_msg, last_day = 0, 0, ""
        if today != last_day:
            day_msg = 0
        sql_info = list(self.db.execute(
            "SELECT time, day_msg, total_msg, last_day FROM Total_Data WHERE time=?", (ttime ,)))
        mem_exists = (len(sql_info) == 1)
        day_msg += num
        total_msg += num
        last_day = today
        
        print(ttime, mem_exists)
        if mem_exists:
            self.db.execute("UPDATE Total_Data SET day_msg=?, total_msg=?, last_day=? WHERE time=?",
                       (day_msg, total_msg, last_day, ttime))
        else:
            self.db.execute("INSERT INTO Total_Data (time,day_setu,day_contrib,day_msg,total_setu,total_contrib,total_msg,last_day) VALUES(?,?,?,?,?,?,?,?)",
                       (ttime, 0, 0, day_msg, 0, 0, total_msg, last_day))
        db_conn.commit()
        db_conn.close()

    def get_day_msg_num(self):
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "setu.db"))
        self.db = db_conn.cursor()
        today = time.strftime("%m%d")
        sql_info = list(self.db.execute(
            "SELECT time, day_msg, total_msg, last_day FROM Total_Data WHERE last_day=?", (today ,)))
        return sql_info
    def get_day_setu_num(self):
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "setu.db"))
        self.db = db_conn.cursor()
        today = time.strftime("%m%d")
        sql_info = list(self.db.execute(
            "SELECT time, day_setu, total_setu, last_day FROM Total_Data WHERE last_day=?", (today ,)))
        return sql_info
    def get_day_contrib_num(self):
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "setu.db"))
        self.db = db_conn.cursor()
        today = time.strftime("%m%d")
        sql_info = list(self.db.execute(
            "SELECT time, day_contrib, total_contrib, last_day FROM Total_Data WHERE last_day=?", (today ,)))
        return sql_info
    def get_max_setu_user(self):
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "setu.db"))
        self.db = db_conn.cursor()
        today = time.strftime("%m%d")
        sql_info = list(self.db.execute(
            "SELECT qqid, day_setu FROM Data WHERE last_day=? ORDER BY day_setu DESC limit 0,5", (today ,)))
        return sql_info
    
    def get_max_contrib_user(self):
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "setu.db"))
        self.db = db_conn.cursor()
        today = time.strftime("%m%d")
        sql_info = list(self.db.execute(
            "SELECT qqid, day_contrib FROM Data WHERE last_day=? ORDER BY day_contrib DESC limit 0,5", (today ,)))
        return sql_info