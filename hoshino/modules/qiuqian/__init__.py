import re
import random
import os
import hoshino
from hoshino.util import DailyNumberLimiter
from hoshino import R, Service, priv, sucmd
from hoshino.util import pic2b64
from hoshino.typing import *
from PIL import Image, ImageSequence, ImageDraw, ImageFont
from .qianwen import *
sv_help = '''
[求签]求签
[解签]解签
'''.strip()
#帮助文本
sv = Service('qiuqian', help_=sv_help, bundle='娱乐')
is_qiuqian_open = True
remove_xiong = False
from .database import *
db = Database(sys.path[0])
@sucmd('开启求签', force_private=False)
async def open_qiuqian(session: CommandSession):
    global is_qiuqian_open
    is_qiuqian_open = True
    await session.send(MessageSegment.text('求签功能已开启'))

@sucmd('关闭求签', force_private=False)
async def close_qiuqian(session: CommandSession):
    global is_qiuqian_open
    is_qiuqian_open = False
    await session.send(MessageSegment.text('求签功能已关闭'))

@sucmd('去除凶签', force_private=False)
async def close_qiuqian(session: CommandSession):
    global remove_xiong
    remove_xiong = True
    await session.send(MessageSegment.text('去除凶签已开启'))

@sucmd('关闭去除凶签', force_private=False)
async def close_qiuqian(session: CommandSession):
    global remove_xiong
    remove_xiong = False
    await session.send(MessageSegment.text('去除凶签已关闭'))


@sucmd('清空求签', force_private=False)
async def open_qiuqian(session: CommandSession):
    os.system('rm qiuqian.db')
    db = Database(sys.path[0])
    await session.send(MessageSegment.text('求签已清空'))

def random_Basemap() -> R.ResImg:
    Img_Path = 'portunedata/imgbase'
    base_dir = R.img(Img_Path).path
    random_img = random.choice(os.listdir(base_dir))
    return R.img(os.path.join(Img_Path, random_img))

def vertical(str):
    list = []
    for s in str:
        list.append(s)
    return '\n'.join(list)

def get_qian_img(id : int):
    fontPath = {
        'title': R.img('portunedata/font/Mamelon.otf').path,
        'text': R.img('portunedata/font/sakura.ttf').path
    }
    img = random_Basemap()
    img = img.open()
    # Draw title
    draw = ImageDraw.Draw(img)
    title = text_dict[id]["title"]
    font_size = 45
    if len(title) == 8:
        title = title.replace("\u3000", "")
    if len(title) <= 6:
        font_size *= 7/6
        font_size = int(font_size)
    
    color = '#F5F5F5'
    image_font_center = (280, 198)
    ttfront = ImageFont.truetype(fontPath['title'], font_size)
    font_length = ttfront.getsize(title)
    draw.text((image_font_center[0]-font_length[0]/2, image_font_center[1]-font_length[1]/2),
                title, fill=color,font=ttfront)
    # Text rendering
    font_size = 50
    color = '#323232'
    image_font_center = [280, 560]
    ttfront = ImageFont.truetype(fontPath['text'], font_size)
    result = text_dict[id]["text"]
    print(result)
    textVertical = []
    hspace = 15
    for i in range(0, result[0]):
        font_height = len(result[i + 1]) * (font_size + hspace)
        textVertical = vertical(result[i + 1])
        x = int(image_font_center[0] + (result[0] - 2) * font_size / 2 + 
                (result[0] - 1) * hspace - i * (font_size + hspace) - hspace)
        y = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), textVertical, fill = color, font = ttfront, spacing = hspace)
    img = pic2b64(img)
    img = MessageSegment.image(img)
    return img


@sv.on_fullmatch(('求签', '求籤'))
async def qiuqian(bot, ev):
    if not ev['message_type'] == 'group':
        return
    qqid = int(ev.user_id)
    if is_qiuqian_open:
        Flag = db.can_qiuqian(qqid)
        if Flag: 
            qian = random.randint(1, 100)
            while remove_xiong and '凶' in text_dict[qian]["title"]:
                qian = random.randint(1, 100)
            db.change_qian(qqid, qian)
        else: qian = db.get_qian(qqid)
        msg0 = MessageSegment.at(qqid)
        if Flag:
            msg0 = msg0 + MessageSegment.text('\n')
        else:
            msg0 = msg0 + MessageSegment.text('今天你已经求过签了 \n')
        msg1 = get_qian_img(qian)
        msg2 = MessageSegment.text('发送「解签」即可解签哦 \n')
        await bot.send(ev, msg0 + msg1 + msg2)
            
@sv.on_fullmatch(('解签', '解籤'))
async def jieqian(bot, ev):
    if not ev['message_type'] == 'group':
        return
    qqid = int(ev.user_id)
    if is_qiuqian_open:
        Flag = db.can_qiuqian(qqid)
        msg0 = MessageSegment.at(qqid)
        if Flag: 
            msg0 = msg0 + MessageSegment.text('今天你还没有求签哦，发送「求签」即可求签 \n')
        else: 
            qian = db.get_qian(qqid)
            msg0 = msg0 + MessageSegment.image("file://" + os.path.abspath(R.img(f"qiuqian/{qian}.jpg").path))
        await bot.send(ev, msg0)    