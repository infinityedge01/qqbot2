from os import path, listdir, system
import asyncio
import datetime
import random
from PIL import Image,ImageFont,ImageDraw
import textwrap
import os
import sys
from nonebot import permission as perm
from nonebot import on_command, CommandSession, scheduler
from nonebot import message
from nonebot import get_bot
from nonebot import log
is_qiuqian_open = True
from .database import *
bot = get_bot()
db = Database(sys.path[0])
@on_command('开启求签', only_to_me = False, permission = perm.SUPERUSER)
async def open_qiuqian(session):
    if session.current_arg == '':
        global is_qiuqian_open
        is_qiuqian_open = True
        await session.send(message.MessageSegment.text('求签功能已开启'))

@on_command('关闭求签', only_to_me = False, permission = perm.SUPERUSER)
async def close_qiuqian(session):
    if session.current_arg == '':
        global is_qiuqian_open
        is_qiuqian_open = False
        await session.send(message.MessageSegment.text('求签功能已关闭'))

@on_command('清空求签', only_to_me = False, permission = perm.SUPERUSER)
async def open_qiuqian(session):
    if session.current_arg == '':
        os.system('rm qiuqian.db')
        db = Database(sys.path[0])
        await session.send(message.MessageSegment.text('求签已清空'))

def get_qian_img(qian:int):
    qianwen = open(path.join(sys.path[0], 'hoshino/modules/qiuqian/word/%d.txt' % (qian)))
    text = qianwen.read()
    text_lst = text.split("\n")
    text = ""
    line_count = 0
    for s in text_lst:
        l1 = textwrap.wrap(s, width= 20)
        for s1 in l1:
            text = text + s1 + "\n"
            line_count += 1
    qian_img = Image.open("hoshino/modules/qiuqian/image/%d.jpg" % (qian))
    qian_img = qian_img.resize((800, 1125))
    base_img = Image.new("RGB", (850, 1125 + line_count * 45), (255, 255, 255))
    dr = ImageDraw.Draw(base_img)
    font = ImageFont.truetype("hoshino/modules/qiuqian/SourceHanSansCN-Normal.ttf", 40)
    dr.text((10, 10), text, font=font, fill="#000000", spacing=8)
    base_img.paste(qian_img, [25, line_count * 45])
    base_img.show()
    base_img.save('hoshino/modules/qiuqian/output.jpg') # 保存

@on_command('求签', aliases=('求籤'), only_to_me = False)
async def setu(session: CommandSession):
    if session.current_arg == '':
        has_perm = await perm.check_permission(session.bot, session.event, perm.GROUP)
        qqid = int(session.event['user_id'])
        if has_perm and is_qiuqian_open:
            Flag = db.can_qiuqian(qqid)
            if Flag: 
                qian = random.randint(1, 100)
                db.change_qian(qqid, qian)
            else: qian = db.get_qian(qqid)
            msg0 = message.MessageSegment.at(qqid)
            if Flag:
                msg0 = msg0 + message.MessageSegment.text('\n')
            else:
                msg0 = msg0 + message.MessageSegment.text('今天你已经求过签了 \n')
            get_qian_img(qian)
            msg1 = message.MessageSegment.image(os.path.join(sys.path[0], "hoshino/modules/qiuqian/output.jpg"))
            await session.send(msg0 + msg1)
            
