import hoshino, os, requests, aiohttp, base64, gc
import matplotlib.pyplot as plt
import pandas as pd, numpy as np

from hoshino import Service, priv
from hoshino.typing import CQEvent
from hoshino.util import FreqLimiter
from PIL import Image,ImageFont,ImageDraw
from datetime import datetime
from io import BytesIO
from os import path
from .data_source import add_text, get_apikey, get_GmServer, get_db_path, get_web_address

sv_help = '''
[生成会战报告] 生成自己的会战报告书
[生成离职报告] 生成自己的离职报告书
[看看报告+@他人] 查看他人的会战报告书（限管理）
'''.strip()

sv = Service('公会战报告书', help_=sv_help, bundle='会战')

try:
    config = hoshino.config.clanbattlereport.report_config
except:
    hoshino.logger.error('not found config of clanbattlereport')

_lmt = FreqLimiter(config.time_limit)
logo = Image.open(path.join(path.dirname(__file__), 'logo.png'))
year = datetime.now().strftime('%Y')
month = str(int(datetime.now().strftime('%m')))

try:
    yobot_url = get_web_address()
except OSError:
    yobot_url = config.yobot_url

@sv.on_rex(r'生成(离职|会战)报告')
async def create_resignation_report(bot, ev: CQEvent):
    if ev['match'].group(1) == '离职':
        background = config.Resignation
    elif ev['match'].group(1) == '会战':
        background = config.FindingsLetter
    uid = ev['user_id']
    gid = ev['group_id']
    if len(yobot_url) == 0:
        await bot.finish(ev, '获取api地址失败，请检查配置')
    if not get_db_path():
        await bot.finish(ev, '获取数据库路径失败，请检查配置')
    try:
        apikey = get_apikey(gid)
    except:
        await bot.finish(ev, '本群未创建公会，或已禁止API获取数据，请检查设置后再试')
    global game_server
    game_server = get_GmServer(gid)
    if game_server == 'cn':
        constellation = config.constellation_cn
    elif game_server == 'tw':
        constellation = config.constellation_tw
    else :
        constellation = config.constellation_jp
    api_url = f'{yobot_url}clan/{gid}/statistics/api/?apikey={apikey}'
    if not _lmt.check(uid):
        await bot.finish(ev, f'{config.time_limit/3600}小时仅能生成一次报告', at_sender=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            data = await resp.json()
    clanname = data['groupinfo'][0]['group_name']
    clanname = clanname[:9]
    challenges: list = data['challenges']
    names: list = data['members']
    nickname = ''
    for name in names[::-1]:
        if uid == name['qqid']:
            nickname = name.get('nickname')
    if not nickname:
        await bot.finish(ev, '你没有加入公会或已从公会离职，无法生成报告', at_sender=True)
    for chl in challenges[::-1]:
        if chl['qqid'] != uid:
            challenges.remove(chl)
    total_chl = len(challenges)
    if total_chl == 0:
        await bot.finish(ev, '没有查询到出刀数据，请出刀后再试', at_sender=True)
    _lmt.start_cd(uid)
    await bot.send(ev, '正在生成公会战报告书，请稍等……')
    damage_to_boss: list = [0 for i in range(5)]
    times_to_boss: list = [0 for i in range(5)]
    truetimes_to_boss: list = [0 for i in range(5)]
    total_chl = 0
    total_damage = 0
    for chl in challenges[::-1]:
        total_damage += chl['damage']
        times_to_boss[chl['boss_num']-1] += 1
        if chl['health_ramain'] != 0 and chl['is_continue'] == 0:
            damage_to_boss[chl['boss_num']-1] += chl['damage']
            truetimes_to_boss[chl['boss_num']-1] += 1
    for chl in challenges[::-1]:
        if chl['health_ramain'] != 0:
            total_chl += 1
    avg_day_damage = int(total_damage/6)
    df=pd.DataFrame({'a':damage_to_boss,'b':truetimes_to_boss})
    result=(df.a/df.b).replace(np.inf,0).fillna(0)
    avg_boss_damage = list(result)
    for chl in challenges[::-1]:
        if chl['damage'] != 0:
            challenges.remove(chl)
    Miss_chl = len(challenges)     
    if total_chl >= 18:
        disable_chl = 0
        attendance_rate = 100
    else:
        disable_chl = 18 - total_chl
        attendance_rate = round(total_chl/18*100,2)

    #设置中文字体
    plt.rcParams['font.family'] = ['Microsoft YaHei']
    x = [f'{x}王' for x in range(1,6)]
    y = times_to_boss
    plt.figure(figsize=(4.5,4.5))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制刀数柱状图
    recs = ax.bar(x,y,width=0.618,color=['#fd7fb0','#ffeb6b','#7cc6f9','#9999ff','orange'],alpha=1)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_tick_params(color='white',colors='white')
    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        a = np.amax(times_to_boss)
        plt.text(rec.get_x(), h+0.01*a, f'{int(truetimes_to_boss[i])}刀',fontdict={"size":15,'color': 'white'})
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img1 = Image.open(buf)
    #清空图
    plt.clf()

    x = [f'{x}王' for x in range(1,6)]
    y = avg_boss_damage
    plt.figure(figsize=(4.5,4.5))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制均伤柱状图
    recs = ax.bar(x,y,width=0.618,color=['#fd7fb0','#ffeb6b','#7cc6f9','#9999ff','orange'],alpha=1)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_tick_params(color='white',colors='white')
    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        b = np.amax(avg_boss_damage)
        plt.text(rec.get_x(), h+b*0.01, f'{int(avg_boss_damage[i]/10000)}万',fontdict={"size":15,'color': 'white'})

    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img2 = Image.open(buf)

    #将饼图和柱状图粘贴到模板图,mask参数控制alpha通道，括号的数值对是偏移的坐标
    current_folder = os.path.dirname(__file__)
    img = Image.open(os.path.join(current_folder,background))
    img.paste(bar_img1, (100,1095), mask=bar_img1.split()[3])
    img.paste(bar_img2, (100,1815), mask=bar_img2.split()[3])

    #添加文字到img

    _fontsize = ImageFont.truetype('QYW3.ttf', 28)
    fontsize = ImageFont.truetype('RZYZY.ttf',24)
    x_nickname ,y_nickname = _fontsize.getsize(nickname)
    x_clanname ,y_clanname = fontsize.getsize(clanname)
    add_text(img,nickname,position=(172,623-y_nickname/2),textsize=28)
    img.paste(logo,(174+x_nickname,625-8),logo)
    add_text(img,clanname,position=(259-x_clanname/2,709-24/2),textsize=24,font='RZYZY.ttf',textfill='#8277b3')
    add_text(img,year,position=(260-50/2,667-21/2),textsize=24,font='RZYZY.ttf',textfill='#8277b3')
    add_text(img,month,position=(344-22/2,667-21/2),textsize=24,font='RZYZY.ttf',textfill='#8277b3')
    add_text(img,constellation,position=(428-48/2,667-24/2),textsize=24,font='RZYZY.ttf',textfill='#8277b3')
    #第一列
    add_text(img,f'{total_chl}',position=(245,801-30/2),textsize=24,textfill='#8277b3')
    add_text(img,f'{disable_chl}',position=(245,849-30/2),textsize=24,textfill='#8277b3')
    add_text(img,f'{total_damage}',position=(245,897-30/2),textsize=24,textfill='#8277b3')
    #第二列
    add_text(img,f'{attendance_rate}%',position=(505,801-30/2),textsize=24,textfill='#8277b3')
    add_text(img,f'{Miss_chl}',position=(505,849-30/2),textsize=24,textfill='#8277b3')
    add_text(img,f'{avg_day_damage}',position=(505,897-30/2),textsize=24,textfill='#8277b3')
    
    #输出
    buf = BytesIO()
    img = img.convert('RGB')
    img.save(buf,format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(ev, f'[CQ:image,file={base64_str}]')
    plt.close('all')
    plt.clf()
    del rec, h, b
    gc.collect()

@sv.on_prefix('看看报告')
async def create_resignation_report(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才可以查看其他成员的报告书')
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
    gid = ev.group_id
    if len(yobot_url) == 0:
        await bot.finish(ev, '获取api地址失败，请检查配置')
    if not get_db_path():
        await bot.finish(ev, '获取数据库路径失败，请检查配置')
    try:
        apikey = get_apikey(gid)
    except:
        await bot.finish(ev, '本群未创建公会，或已禁止API获取数据，请检查设置后再试')
    global game_server
    game_server = get_GmServer(gid)
    if game_server == 'cn':
        constellation = config.constellation_cn
    elif game_server == 'tw':
        constellation = config.constellation_tw
    else :
        constellation = config.constellation_jp
    api_url = f'{yobot_url}clan/{gid}/statistics/api/?apikey={apikey}'
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            data = await resp.json()
    clanname = data['groupinfo'][0]['group_name']
    clanname = clanname[:9]
    challenges: list = data['challenges']
    names: list = data['members']
    nickname = ''
    for name in names[::-1]:
        if uid == name['qqid']:
            nickname = name.get('nickname')
    if not nickname:
        await bot.finish(ev, '该成员未加入公会或已从公会离职，无法生成报告', at_sender=True)
    for chl in challenges[::-1]:
        if chl['qqid'] != uid:
            challenges.remove(chl)
    total_chl = len(challenges)
    if total_chl == 0:
        await bot.finish(ev, '没有查询到该成员的出刀数据，请出刀后再试', at_sender=True)
    await bot.send(ev, '正在生成该成员的公会战报告书，请稍等……')
    damage_to_boss: list = [0 for i in range(5)]
    times_to_boss: list = [0 for i in range(5)]
    truetimes_to_boss: list = [0 for i in range(5)]
    total_chl = 0
    total_damage = 0
    for chl in challenges[::-1]:
        total_damage += chl['damage']
        times_to_boss[chl['boss_num']-1] += 1
        if chl['health_ramain'] != 0 and chl['is_continue'] == 0:
            damage_to_boss[chl['boss_num']-1] += chl['damage']
            truetimes_to_boss[chl['boss_num']-1] += 1
    for chl in challenges[::-1]:
        if chl['health_ramain'] != 0:
            total_chl += 1
    avg_day_damage = int(total_damage/6)
    df=pd.DataFrame({'a':damage_to_boss,'b':truetimes_to_boss})
    result=(df.a/df.b).replace(np.inf,0).fillna(0)
    avg_boss_damage = list(result)
    for chl in challenges[::-1]:
        if chl['damage'] != 0:
            challenges.remove(chl)
    Miss_chl = len(challenges)     
    if total_chl >= 18:
        disable_chl = 0
        attendance_rate = 100
    else:
        disable_chl = 18 - total_chl
        attendance_rate = round(total_chl/18*100,2)
    
    #设置中文字体
    plt.rcParams['font.family'] = ['msyh']
    x = [f'{x}王' for x in range(1,6)]
    y = times_to_boss
    plt.figure(figsize=(4.5,4.5))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制刀数柱状图
    recs = ax.bar(x,y,width=0.618,color=['#fd7fb0','#ffeb6b','#7cc6f9','#9999ff','orange'],alpha=1)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_tick_params(color='white',colors='white')
    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        a = np.amax(times_to_boss)
        plt.text(rec.get_x(), h+0.01*a, f'{int(truetimes_to_boss[i])}刀',fontdict={"size":15,'color': 'white'})
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img1 = Image.open(buf)
    #清空图
    plt.clf()

    x = [f'{x}王' for x in range(1,6)]
    y = avg_boss_damage
    plt.figure(figsize=(4.5,4.5))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制均伤柱状图
    recs = ax.bar(x,y,width=0.618,color=['#fd7fb0','#ffeb6b','#7cc6f9','#9999ff','orange'],alpha=1)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_tick_params(color='white',colors='white')
    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        b = np.amax(avg_boss_damage)
        plt.text(rec.get_x(), h+b*0.01, f'{int(avg_boss_damage[i]/10000)}万',fontdict={"size":15,'color': 'white'})

    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img2 = Image.open(buf)

    #将饼图和柱状图粘贴到模板图,mask参数控制alpha通道，括号的数值对是偏移的坐标
    current_folder = os.path.dirname(__file__)
    img = Image.open(os.path.join(current_folder,config.FindingsLetter))
    img.paste(bar_img1, (100,1095), mask=bar_img1.split()[3])
    img.paste(bar_img2, (100,1815), mask=bar_img2.split()[3])

    #添加文字到img
    _fontsize = ImageFont.truetype('QYW3.ttf', 28)
    fontsize = ImageFont.truetype('RZYZY.ttf',24)
    x_nickname ,y_nickname = _fontsize.getsize(nickname)
    x_clanname ,y_clanname = fontsize.getsize(clanname)
    add_text(img,nickname,position=(172,623-y_nickname/2),textsize=28)
    img.paste(logo,(174+x_nickname,625-8),logo)
    add_text(img,clanname,position=(259-x_clanname/2,709-24/2),textsize=24,font='RZYZY.ttf',textfill='#8277b3')
    add_text(img,year,position=(260-50/2,667-21/2),textsize=24,font='RZYZY.ttf',textfill='#8277b3')
    add_text(img,month,position=(344-22/2,667-21/2),textsize=24,font='RZYZY.ttf',textfill='#8277b3')
    add_text(img,constellation,position=(428-48/2,667-24/2),textsize=24,font='RZYZY.ttf',textfill='#8277b3')
    #第一列
    add_text(img,f'{total_chl}',position=(245,801-30/2),textsize=24,textfill='#8277b3')
    add_text(img,f'{disable_chl}',position=(245,849-30/2),textsize=24,textfill='#8277b3')
    add_text(img,f'{total_damage}',position=(245,897-30/2),textsize=24,textfill='#8277b3')
    #第二列
    add_text(img,f'{attendance_rate}%',position=(505,801-30/2),textsize=24,textfill='#8277b3')
    add_text(img,f'{Miss_chl}',position=(505,849-30/2),textsize=24,textfill='#8277b3')
    add_text(img,f'{avg_day_damage}',position=(505,897-30/2),textsize=24,textfill='#8277b3')

    #输出
    buf = BytesIO()
    img = img.convert('RGB')
    img.save(buf,format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(ev, f'[CQ:image,file={base64_str}]')
    plt.close('all')
    plt.clf()
    del rec, h, b
    gc.collect()