import json
from hoshino import config, Service, priv
from hoshino.typing import CQEvent
from .. import chara
from .data import *

sv = Service('wiki', help_='''
[@bot简介ue] 角色简介
[@bot技能ue] 角色技能
[@bot专武ue] 角色专武
[@bot羁绊ue] 角色羁绊
'''.strip(), bundle='pcr查询')

def get_chara(name, types):
    id_ = chara.name2id(name)
    confi = 100
    if id_ == chara.UNKNOWN:
        id_, guess_name, confi = chara.guess_id(name)
    c = chara.fromid(id_)
    msg = ''
    is_npc = chara.is_npc(id_)
    if confi < 100:
        msg = f'兰德索尔似乎没有叫"{name}"的人...\n角色别称补全计划: github.com/Ice-Cirno/HoshinoBot/issues/5\n您有{confi}%的可能在找{guess_name}{c.icon.cqcode}'
    elif is_npc:
        msg = f'没有查询到{name}的wiki数据'
    else:
        msg = f'{c.icon.cqcode}'
        try:
            if types == 'introduce':
                msg += get_info(id_)
            elif types == 'skill':
                msg += get_skill(id_)
            elif types == 'uniquei':
                msg += get_uniquei(id_)
            elif types == 'kizuna':
                msg += get_kizuna(id_)
        except:
            msg += f'\n暂时没有更新{name}的数据'
    return msg

@sv.on_prefix(('简介','介绍'), only_to_me=True)
async def introduce(bot, ev: CQEvent):
    name = ev.message.extract_plain_text().strip()
    if not name:
        await bot.send(ev, '请发送"简介"+别称，如"简介ue"')
        return
    result = get_chara(name,'introduce')
    await bot.send(ev, result)

@sv.on_prefix(('技能'), only_to_me=True)
async def skill(bot, ev: CQEvent):
    name = ev.message.extract_plain_text().strip()
    if not name:
        await bot.send(ev, '请发送"技能"+别称，如"技能ue"')
        return
    result = get_chara(name,'skill')
    await bot.send(ev, result)

@sv.on_prefix(('专武'), only_to_me=True)
async def uniquei(bot, ev: CQEvent):
    name = ev.message.extract_plain_text().strip()
    if not name:
        await bot.send(ev, '请发送"专武"+别称，如"专武ue"')
        return
    result = get_chara(name,'uniquei')
    await bot.send(ev, result)

@sv.on_prefix(('羁绊'), only_to_me=True)
async def kizuna(bot, ev: CQEvent):
    name = ev.message.extract_plain_text().strip()
    if not name:
        await bot.send(ev, '请发送"羁绊"+别称，如"羁绊ue"')
        return
    result = get_chara(name,'kizuna')
    await bot.send(ev, result)

@sv.on_fullmatch(('更新wiki'))
async def update_wiki(bot, ev: CQEvent):
    if priv.get_user_priv(ev) < priv.SUPERUSER:
        return
    local_version = get_file_md5()
    download_addres = 'https://wiki.calloy.com.cn/version.json'
    f = requests.get(download_addres)
    with open(os.path.join(os.path.dirname(__file__), 'version.json'), "wb") as code:
        code.write(f.content)
    with open(os.path.join(os.path.dirname(__file__), 'version.json'), "rb") as file:
        version = json.load(file) 
    if version['hash'] == local_version:
        await bot.send(ev, f'已是最新版本，无需更新')
    else:
        db_request = requests.get(version['url'])
        with open(os.path.join(os.path.dirname(__file__), 'data.db'), "wb") as db:
            db.write(db_request.content)
        result = version['content']
        await bot.send(ev, f'{result}')