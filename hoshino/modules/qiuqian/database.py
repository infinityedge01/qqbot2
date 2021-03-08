import sqlite3
import os
import time
import pickle
import sys
class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        db_exists = os.path.exists(os.path.join(
            db_path, "qiuqian.db"))
        db_conn = sqlite3.connect(os.path.join(
            db_path, "qiuqian.db"))
        self.db = db_conn.cursor()
        if not db_exists:
            self.db.execute(
                '''CREATE TABLE Data(
                qqid INT PRIMARY KEY,
                points INT,
                last_day CHARACTER(4))''')
        db_conn.commit()
        db_conn.close()
    def can_qiuqian(self, qqid: int) -> bool:
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "qiuqian.db"))
        self.db = db_conn.cursor()
        today = time.strftime("%m%d")
        sql_info = list(self.db.execute(
            "SELECT qqid, points, last_day FROM Data WHERE qqid=?", (qqid,)))
        mem_exists = (len(sql_info) == 1)
        if mem_exists:
            points, last_day = sql_info[0][1:]
        else:
            points, last_day = 0, ""
        flag = False
        if today != last_day or points == 0:
            last_day = today
            flag = True
        else:
            flag = False
        if mem_exists:
            self.db.execute("UPDATE Data SET points=?, last_day=? WHERE qqid=?",
                       (points, last_day, qqid))
        else:
            self.db.execute("INSERT INTO Data (qqid,points,last_day) VALUES(?,?,?)",
                       (qqid, points, last_day))
        db_conn.commit()
        db_conn.close()
        return flag

    def change_qian(self, qqid: int, x: int) -> bool:
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "qiuqian.db"))
        self.db = db_conn.cursor()
        sql_info = list(self.db.execute(
            "SELECT qqid, points, last_day FROM Data WHERE qqid=?", (qqid,)))
        mem_exists = (len(sql_info) == 1)
        if mem_exists:
            points, last_day = sql_info[0][1:]
        else:
            points, last_day = 0, ""
        flag = True
        if x < 0:
            flag = False
        else:
            points = x
        if mem_exists:
            self.db.execute("UPDATE Data SET points=?, last_day=? WHERE qqid=?",
                       (points, last_day, qqid))
        else:
            self.db.execute("INSERT INTO Data (qqid,points,last_day) VALUES(?,?,?)",
                       (qqid, points, last_day))
        db_conn.commit()
        db_conn.close()
        return flag
    def get_qian(self, qqid: int) -> int:
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "qiuqian.db"))
        self.db = db_conn.cursor()
        sql_info = list(self.db.execute(
            "SELECT qqid, points, last_day FROM Data WHERE qqid=?", (qqid,)))
        mem_exists = (len(sql_info) == 1)
        if mem_exists:
            points, last_day = sql_info[0][1:]
        else:
            points, last_day = 0, ""
            self.db.execute("INSERT INTO Data (qqid,points,last_day) VALUES(?,?,?)",
                       (qqid, points, last_day))
        db_conn.commit()
        db_conn.close()
        return points