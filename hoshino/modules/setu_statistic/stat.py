import re
import random
import asyncio
import os
import hoshino
import nonebot
import datetime
from hoshino.util import DailyNumberLimiter
from hoshino import R, Service, priv, sucmd
from hoshino.util import pic2b64
from hoshino.typing import *
cqbot = nonebot.get_bot()
sv_help = '''
[涩图统计]涩图统计
'''.strip()
sv = Service('setu_statistic', help_=sv_help, bundle='娱乐')

from .database import *
db = Database(sys.path[0])

from .paint import *

msg_count = 0
def update_msg_count():
    global msg_count
    time = datetime.datetime.now().hour * 6 + datetime.datetime.now().minute // 10
    db.update_total_msg(time, msg_count)
    msg_count = 0
@sv.scheduled_job('cron', minute = '*/10')
async def _call():
    await asyncio.sleep(20)
    update_msg_count()

@cqbot.on_message
async def count_msg(context):
    global msg_count
    msg_count += 1

@sv.on_fullmatch(('涩图统计'))
async def stat(bot, ev):
    data = {
        "time": [],
        "message": [],
        "setu_in": [],
        "setu_out": [],

        "sepi": [
            
        ],
        "contribution": [
            
        ]
    }
    if not ev['message_type'] == 'group':
        return
    time = datetime.datetime.now().hour * 6 + datetime.datetime.now().minute // 10
    msg_stat = db.get_day_msg_num()
    setu_stat = db.get_day_setu_num()
    contrib_stat = db.get_day_contrib_num()
    for i in range(time + 1):
        data["time"].append("%02d:%02d" % (i // 6, (i % 6) * 10))
        data["message"].append(0)
        data["setu_in"].append(0)
        data["setu_out"].append(0)
    for x in msg_stat:
        if x[0] <= time:
            data["message"][x[0]] = x[1]
    for x in setu_stat:
        if x[0] <= time:
            data["setu_out"][x[0]] = x[1]
    for x in contrib_stat:
        if x[0] <= time:
            data["setu_in"][x[0]] = x[1]
    for i in range(1, time + 1):
        if data["message"][i] < data["message"][i - 1]:
            data["message"][i] = data["message"][i - 1]
        if data["setu_in"][i] < data["setu_in"][i - 1]:
            data["setu_in"][i] = data["setu_in"][i - 1]
        if data["setu_out"][i] < data["setu_out"][i - 1]:
            data["setu_out"][i] = data["setu_out"][i - 1]
    sepi = db.get_max_setu_user()
    contribution = db.get_max_contrib_user()
    print(sepi)
    print(contribution)
    for i in range(5):
        if i >= len(sepi):
            data["sepi"].append(("", 0, 0))
        else:
            nickname = await bot.get_stranger_info(user_id = sepi[i][0])
            data["sepi"].append((f"https://q1.qlogo.cn/g?b=qq&nk={sepi[i][0]}&s=100",  nickname["nickname"], sepi[i][1]))
    for i in range(5):
        if i >= len(contribution):
            data["contribution"].append(("", 0, 0))
        else:
            nickname = await bot.get_stranger_info(user_id = contribution[i][0])
            data["contribution"].append((f"https://q1.qlogo.cn/g?b=qq&nk={contribution[i][0]}&s=100", nickname["nickname"] , contribution[i][1]))
    msg = paint(data)
    await bot.send(ev, msg)
        
        

    
    
    