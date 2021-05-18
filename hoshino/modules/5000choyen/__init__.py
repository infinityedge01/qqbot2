from PIL import Image

from hoshino import Service, priv, logger, aiorequests
from hoshino.typing import CQEvent, MessageSegment
from hoshino.util import FreqLimiter, DailyNumberLimiter, pic2b64

from .generator import genImage, change_font

lmt = FreqLimiter(10)
max_len = 40
sv = Service('dickytwister', help_='[男同] (上半句)|(下半句)')

@sv.on_prefix(('男同'))
async def dickytwistergen(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    mid= ev.message_id
    if not lmt.check(uid):
        await bot.send(ev, f'您生成太多男同了', at_sender=True)
        return
    try:
        keyword = ev.message.extract_plain_text().strip()
        if not keyword:
            await bot.send(ev, '请提供要生成的内容')
            return
        if len(keyword) > max_len:
            await bot.send(ev, '输入内容太长了')
            return
        upper=keyword.split("|")[0]
        downer=keyword.split("|")[1]
        img=genImage(word_a=upper, word_b=downer)
        img = str(MessageSegment.image(pic2b64(img)))
        await bot.send(ev, img)
        lmt.start_cd(uid)
    except:
        await bot.send(ev, '生成失败……请检查命令格式是否正确\n男同 上半句|下半句')

@sv.on_prefix(('男同帮助'))
async def dickytwisterhelp(bot, ev: CQEvent):
    await bot.send(ev, '[男同] 上半句|下半句\n[切换男同字体] [CN|JP]')

fonts = {"JP": ["Source Han Sans Bold.otf", "Source Han Serif Heavy.otf"], "CN": ["思源黑体CN.otf", "思源宋体CN.otf"]}

@sv.on_prefix(('切换男同字体'))
async def dickytwisterfont(bot, ev: CQEvent):
    keyword = ev.message.extract_plain_text().strip()
    if keyword in fonts:
        change_font(fonts[keyword][0], fonts[keyword][1])
        await bot.send(ev, '切换字体成功')
    else:
        await bot.send(ev, '没有这种字体')
