from os import path
import asyncio
import datetime
import pytz
import re
from apscheduler.triggers.date import DateTrigger # 一次性触发器
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot import permission as perm
from nonebot import on_command, CommandSession, scheduler
from nonebot import message
from nonebot import get_bot
from nonebot import log
from hoshino import Service
sv = Service("涩图")

from .get_setu import *
is_setu_open = True
setu_send_groupid = 1042285895
setu_scheduled_open = None
setu_scheduled_close = None
setu_scheduled_open_time = None
setu_scheduled_close_time = None

from .database import *
db = Database(sys.path[0])

@on_command('开启色图', aliases=('开启涩图'), only_to_me = False, permission = perm.SUPERUSER)
async def open_setu(session):
    if session.current_arg == '':
        global is_setu_open
        is_setu_open = True
        await session.send(message.MessageSegment.text('涩图已开启'))

async def open_setu_scheduled():
    bot = get_bot()
    global is_setu_open
    is_setu_open = True
    msg = message.MessageSegment.text('涩图已开启')
    try:
        await bot.send_group_msg(group_id=setu_send_groupid, message=msg)
    except CQHttpError:
        pass

async def close_setu_scheduled():
    bot = get_bot()
    global is_setu_open
    is_setu_open = False
    msg = message.MessageSegment.text('涩图已关闭')
    try:
        await bot.send_group_msg(group_id=setu_send_groupid, message=msg)
    except CQHttpError:
        pass

@on_command('关闭色图', aliases=('关闭涩图'), only_to_me = False, permission = perm.SUPERUSER)
async def close_setu(session):
    if session.current_arg == '':
        global is_setu_open
        is_setu_open = False
        await session.send(message.MessageSegment.text('涩图已关闭'))

@on_command('色图开启时间', aliases=('涩图开启时间'), only_to_me = False, permission = perm.SUPERUSER)
async def set_open_setu_time(session):
    match = re.match(r'^(\d+):(\d+)', session.current_arg)
    if not match:
        return
    hour = int(match.group(1))
    minute = int(match.group(2))
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        await session.send(message.MessageSegment.text('输入错误'))
        return
    global setu_scheduled_open
    global setu_scheduled_open_time
    setu_scheduled_open_time = (hour, minute)
    if setu_scheduled_open != None:
        scheduler.remove_job(setu_scheduled_open)
        setu_scheduled_open = None

    scheduler.add_job(open_setu_scheduled, 'cron', hour = hour, minute = minute, id = 'setu_open')
    setu_scheduled_open = 'setu_open'
    await session.send(message.MessageSegment.text('设置成功，当前涩图每日开启时间为：{}:{}'.format(str(hour).zfill(2), str(minute).zfill(2))))
    
@on_command('色图关闭时间', aliases=('涩图关闭时间'), only_to_me = False, permission = perm.SUPERUSER)
async def set_close_setu_time(session):
    match = re.match(r'^(\d+):(\d+)', session.current_arg)
    if not match:
        return
    hour = int(match.group(1))
    minute = int(match.group(2))
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        await session.send(message.MessageSegment.text('输入错误'))
        return
    global setu_scheduled_close
    global setu_scheduled_close_time
    setu_scheduled_close_time = (hour, minute)
    if setu_scheduled_close != None:
        scheduler.remove_job(setu_scheduled_close)
        setu_scheduled_close = None

    scheduler.add_job(close_setu_scheduled, 'cron', hour = hour, minute = minute, id = 'setu_close')
    setu_scheduled_close = 'setu_close'
    await session.send(message.MessageSegment.text('设置成功，当前涩图每日关闭时间为：{}:{}'.format(str(hour).zfill(2), str(minute).zfill(2))))

@on_command('清除色图定时', aliases=('清除涩图定时'), only_to_me = False, permission = perm.SUPERUSER)
async def clear_setu_schedule(session):
    if session.current_arg == '':
        global setu_scheduled_open
        global setu_scheduled_open_time
        global setu_scheduled_close
        global setu_scheduled_close_time
        if setu_scheduled_open != None:
            scheduler.remove_job(setu_scheduled_open)
            setu_scheduled_open = None
        if setu_scheduled_close != None:
            scheduler.remove_job(setu_scheduled_close)
            setu_scheduled_close = None
        setu_scheduled_open_time = None
        setu_scheduled_close_time = None
        await session.send(message.MessageSegment.text('清除成功'))

@on_command('查看色图定时', aliases=('查看涩图定时'), only_to_me = False)
async def get_setu_schedule(session):
    if session.current_arg == '':
        global setu_scheduled_open_time
        global setu_scheduled_close_time
        msg = message.MessageSegment.text('涩图开启时间为：')
        if setu_scheduled_open_time == None:
            msg = msg + message.MessageSegment.text('未设置\n')
        else:
            msg = msg + message.MessageSegment.text('{}:{}\n'.format(str(setu_scheduled_open_time[0]).zfill(2), str(setu_scheduled_open_time[1]).zfill(2)))
        msg = msg + message.MessageSegment.text('涩图关闭时间为：')
        if setu_scheduled_close_time == None:
            msg = msg + message.MessageSegment.text('未设置')
        else:
            msg = msg + message.MessageSegment.text('{}:{}'.format(str(setu_scheduled_close_time[0]).zfill(2), str(setu_scheduled_close_time[1]).zfill(2)))
        await session.send(msg)

setu_count = 0
def update_setu_count():
    global setu_count
    time = datetime.datetime.now().hour * 6 + datetime.datetime.now().minute // 10
    db.update_total_setu(time, setu_count)
    setu_count = 0
@sv.scheduled_job('cron', minute = '*/10')
async def _call():
    update_setu_count()

@on_command('色图', aliases=('涩图'), only_to_me = False)
async def setu(session: CommandSession):
    bot = get_bot()
    if session.current_arg == '':
        has_perm = await perm.check_permission(session.bot, session.event, perm.GROUP)
        if has_perm and is_setu_open:
            # msg1 = message.MessageSegment.image('https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1592212494831&di=ee6127d25949ab52d82402d2309a8537&imgtype=0&src=http%3A%2F%2Fb.hiphotos.baidu.com%2Fzhidao%2Fwh%253D450%252C600%2Fsign%3D14f304ca50da81cb4eb38bc96756fc20%2Fae51f3deb48f8c542d7329113b292df5e0fe7f68.jpg')
            Flag = await can_get_a_setu(session.event.user_id)
            if not Flag:
                await session.send(message.MessageSegment.text('你看太多涩图了'))
                return
            db.update_setu(session.event.user_id)
            global setu_count
            setu_count += 1
            msg1 = await get_a_setu()
            log.logger.debug(str(msg1))
            msg_data = await session.send(msg1)
            log.logger.debug(str(msg_data['message_id']))
            # 制作一个“10秒钟后”触发器
            delta = datetime.timedelta(seconds=20)
            trigger = DateTrigger(
                run_date=datetime.datetime.now() + delta
            )
            scheduler.add_job(
                func=bot.delete_msg,  # 要添加任务的函数，不要带参数
                trigger=trigger,  # 触发器
                kwargs={'message_id':msg_data['message_id'], 'self_id':session.event.self_id},  # 函数的参数列表，注意：只有一个值时，不能省略末尾的逗号
                # kwargs=None,
                misfire_grace_time=1,  # 允许的误差时间，建议不要省略
                # jobstore='default',  # 任务储存库
            )
         #   await asyncio.sleep(10)
         #   await bot.delete_msg(message_id = msg_data['message_id'], self_id = session.event.self_id)
        else:
            msg1 = message.MessageSegment.text('我们可以通过“色图”来表示所有自然界之色，国际照明学会规定分别用x、y、z来表示红、绿、蓝三原色之间的百分比。由于是百分比，三者相加必须等于1，故色调在色图中只需用x、y两值即可。将光谱色中各段波长所引起的色调感觉在x、y平面上做成图标时，即得色图。')
            await session.send(msg1)      
    pass

    