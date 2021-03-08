from os import path
import asyncio
import datetime
import pytz
import requests
import ast
import re
import hashlib
import base64
import csv
from apscheduler.triggers.date import DateTrigger # 一次性触发器
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot import permission as perm
from nonebot import on_command, CommandSession, scheduler
from nonebot import message
from nonebot import get_bot
from nonebot import log
from .PCRClanBattle import ClanBattle
Clan = ClanBattle(1314202001949, "2020081016480401600000", "204ea6141f2eed91eb4a3df3d2c1b6e7")
Push_Score_Lines = None
Crawl_Score_Lines = None
@on_command('查排名', only_to_me = False)
async def query_by_rank(session):
    match = re.match(r'^(\d+)', session.current_arg)
    if not match:
        return
    global Clan
    rank = int(match.group(1))
    if rank <= 0 or rank >= 15000:
        await session.send(message.MessageSegment.text('输入错误'))
        return
    log.logger.debug(str(rank))
    msg_str = Clan.rank_to_string(Clan.get_rank_status(rank), long_info = True)
    await session.send(message.MessageSegment.text(msg_str))

def get_score_line(lst):
    global Clan
    msg_str = ''
    for x in lst:  
        msg_str += Clan.rank_to_string(Clan.get_rank_status(x), long_info = False)
        msg_str += '\n'
    return msg_str

@on_command('查档线', only_to_me = False)
async def query_score_line(session):
    if session.current_arg == '':
        msg_str = get_score_line([1, 2, 3, 20])
        await session.send(message.MessageSegment.text(msg_str))
        msg_str = get_score_line([50, 100, 150])
        await session.send(message.MessageSegment.text(msg_str))

@on_command('查页', only_to_me = False)
async def query_page_score(session):
    match = re.match(r'^(\d+)', session.current_arg)
    if not match:
        return
    global Clan
    page = int(match.group(1))
    msg_str = ''
    data = Clan.get_page_data(page + 1)
    for i in range(len(data)):
        msg_str += Clan.rank_to_string(data[i], long_info = False)
        msg_str += '\n'
        if i == 4:
            await session.send(message.MessageSegment.text(msg_str))
            msg_str = ''

async def push_score_line_scheduled():
    msg_str = get_score_line([1, 2, 3, 20, 50, 100, 150])
    bot = get_bot()
    try:
        await bot.send_group_msg(group_id=653134962, message=message.MessageSegment.text("截至当前的档线：\n") + message.MessageSegment.text(msg_str))
    except CQHttpError:
        pass

async def write_down_score_line_scheduled():
    global Clan
    bot = get_bot()
    cnt = 0
    try:
        await bot.send_private_msg(user_id = 309173017, message = message.MessageSegment.text('开始爬取数据'))
    except CQHttpError:
        pass
    with open('score_line.csv', 'w', newline='') as f:
        head = ['rank', 'clan_name', 'member_num', 'leader_name', 'damage', 'lap', 'boss_id', 'remain', 'grade_rank']
        writer = csv.writer(f) 
        writer.writerow(head)
        for i in range(0, 1000):
            temp1 = Clan.get_page_data(i)
            if len(temp1) == 0:
                break
            rows = []
            for item in temp1:
                rows.append([item['rank'], item['clan_name'], item['member_num'], item['leader_name'], item['damage'], item['lap'], item['boss_id'], item['remain'], item['grade_rank']])
            writer.writerows(rows)
            cnt += len(rows)
            log.logger.debug(str(i))
    
    try:
        await bot.send_private_msg(user_id = 309173017, message = message.MessageSegment.text('记录成功，共记录数据{}条'.format(cnt)))
    except CQHttpError:
        pass


@on_command('开启推送档线', only_to_me = False, permission = perm.SUPERUSER)
async def set_open_score_line(session):
    match = re.match(r'^(\d+):(\d+)', session.current_arg)
    if not match:
        return
    hour = int(match.group(1))
    minute = int(match.group(2))
    global Push_Score_Lines
    if Push_Score_Lines != None:
        scheduler.remove_job(Push_Score_Lines)
        Push_Score_Lines = None
    scheduler.add_job(push_score_line_scheduled, 'cron', hour = hour, minute = minute, id = 'score_lines_open')
    Push_Score_Lines = 'score_lines_open'
    await session.send(message.MessageSegment.text('每日{}:{}会自动推送当前档线'.format(str(hour).zfill(2), str(minute).zfill(2))))

@on_command('开启爬取数据', only_to_me = False, permission = perm.SUPERUSER)
async def set_open_crawl_score_line(session):
    match = re.match(r'^(\d+):(\d+)', session.current_arg)
    if not match:
        return
    hour = int(match.group(1))
    minute = int(match.group(2))
    global Crawl_Score_Lines
    if Crawl_Score_Lines != None:
        scheduler.remove_job(Crawl_Score_Lines)
        Crawl_Score_Lines = None
    scheduler.add_job(write_down_score_line_scheduled, 'cron', hour = hour, minute = minute, id = 'crawl_score_lines_open')
    Crawl_Score_Lines = 'crawl_score_lines_open'
    await session.send(message.MessageSegment.text('每日{}:{}会自动爬取数据'.format(str(hour).zfill(2), str(minute).zfill(2))))

@on_command('关闭推送档线', only_to_me = False, permission = perm.SUPERUSER)
async def set_close_score_line(session):
    if session.current_arg == '':
        global Push_Score_Lines
        if Push_Score_Lines != None:
            scheduler.remove_job(Push_Score_Lines)
            Push_Score_Lines = None
        await session.send(message.MessageSegment.text('自动推送当前档线已关闭'))

@on_command('关闭爬取数据', only_to_me = False, permission = perm.SUPERUSER)
async def set_close_crawl_score_line(session):
    if session.current_arg == '':
        global Crawl_Score_Lines
        if Crawl_Score_Lines != None:
            scheduler.remove_job(Crawl_Score_Lines)
            Crawl_Score_Lines = None
        await session.send(message.MessageSegment.text('自动爬取数据已关闭'))

