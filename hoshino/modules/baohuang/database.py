import sqlite3
import os
import time
import pickle
import sys
class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        db_exists = os.path.exists(os.path.join(
            db_path, "baohuang.db"))
        db_conn = sqlite3.connect(os.path.join(
            db_path, "baohuang.db"))
        self.db = db_conn.cursor()
        if not db_exists:
            self.db.execute(
                '''CREATE TABLE Data(
                qqid INT PRIMARY KEY,
                points INT,
                last_day CHARACTER(4))''')
        db_conn.commit()
        db_conn.close()
    def get_free_points(self, qqid: int, daily_free: int) -> bool:
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "baohuang.db"))
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
        if today != last_day:
            last_day = today
            flag = True
            points = points + daily_free
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

    def add_point(self, qqid: int, x: int) -> bool:
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "baohuang.db"))
        self.db = db_conn.cursor()
        sql_info = list(self.db.execute(
            "SELECT qqid, points, last_day FROM Data WHERE qqid=?", (qqid,)))
        mem_exists = (len(sql_info) == 1)
        if mem_exists:
            points, last_day = sql_info[0][1:]
        else:
            points, last_day = 0, ""
        flag = True
        points = points + x
        if points < 0:
            points = 0
        if mem_exists:
            self.db.execute("UPDATE Data SET points=?, last_day=? WHERE qqid=?",
                       (points, last_day, qqid))
        else:
            self.db.execute("INSERT INTO Data (qqid,points,last_day) VALUES(?,?,?)",
                       (qqid, points, last_day))
        db_conn.commit()
        db_conn.close()
        return flag
    def change_point(self, qqid: int, x: int) -> bool:
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "baohuang.db"))
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
    def get_point(self, qqid: int) -> int:
        db_conn = sqlite3.connect(os.path.join(
            self.db_path, "baohuang.db"))
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

#test = Database(sys.path[0])
#print(test.change_point(309173017, 19260817))
#print(test.add_point(309173017, 1))
#print(test.get_free_points(309173017, 10000))
#print(test.get_free_points(309173017, 10000))
#print(test.get_point(309173017))
#print(test.get_point(114514))
#print(test.get_free_points(114514, 10000))
#print(test.get_point(114514))



        
            

        