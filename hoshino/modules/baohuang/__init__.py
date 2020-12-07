from os import path
import asyncio
import datetime
import re
from apscheduler.triggers.date import DateTrigger # 一次性触发器
from nonebot import permission as perm
from nonebot import on_command, on_request, RequestSession, CommandSession, scheduler
from nonebot import message
from nonebot import get_bot
from nonebot import log
from .database import *
from .game import *
bot = get_bot()
is_baohuang_open = set()
db = Database(os.path.join(sys.path[0], "hoshino/modules/baohuang"))
on_table = []
table = None
buqiang = []
basepoint = 500
@on_command('开启保皇', only_to_me = False, permission = perm.SUPERUSER)
async def open_baohuang(session):
    if session.current_arg == '' and session.event.detail_type == 'group':
        global is_baohuang_open
        is_baohuang_open.add(session.event.group_id)
        log.logger.debug(str(is_baohuang_open))
        await session.send(message.MessageSegment.text('保皇功能已开启'))

@on_command('关闭保皇', only_to_me = False, permission = perm.SUPERUSER)
async def close_baohuang(session):
    if session.current_arg == '' and session.event.detail_type == 'group':
        global is_baohuang_open
        is_baohuang_open.remove(session.event.group_id)
        await session.send(message.MessageSegment.text('保皇功能已关闭'))

@on_command('重置保皇', only_to_me = False, permission = perm.SUPERUSER)
async def restart_baohuang(session):
    if session.current_arg == '' and session.event.detail_type == 'group':
        global is_baohuang_open, on_table, buqiang, table
        on_table = []
        buqiang = []
        table = None
        await session.send(message.MessageSegment.text('保皇功能已重置'))

@on_request('friend')
async def auto_add_friend(session: RequestSession):
    await session.approve()

@on_command('获取积分', only_to_me = False, permission = perm.GROUP)
async def get_free_points(session):
    if session.current_arg == '' and session.event.group_id in is_baohuang_open:
        global db
        is_success = db.get_free_points(session.event['user_id'], 10000)
        if is_success:
            await session.send(message.MessageSegment.at(session.event['user_id']) + message.MessageSegment.text('已为你成功添加积分。当前积分：%d' % (db.get_point(session.event['user_id']))))
        else:
            await session.send(message.MessageSegment.at(session.event['user_id']) + message.MessageSegment.text('又输光想要分？明天再来吧。当前积分：%d' % (db.get_point(session.event['user_id']))))

@on_command('我的积分', only_to_me = False, permission = perm.GROUP)
async def get_points(session):
    if session.current_arg == '' and session.event.group_id in is_baohuang_open:
        global db
        await session.send(message.MessageSegment.at(session.event['user_id']) + message.MessageSegment.text('当前积分：%d' % (db.get_point(session.event['user_id']))))

@on_command('添加积分', only_to_me = False, permission = perm.SUPERUSER)
async def add_points(session):
    global db
    match = re.match(r'^\[CQ:at,qq=(\d+)\] *(\d+)', session.current_arg)
    if not match:
        return
    qqid = int(match.group(1))
    add = int(match.group(2))
    db.add_point(qqid, add)
    await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('添加成功，当前积分：%d' % (db.get_point(qqid))))

@on_command('设置底分', only_to_me = False, permission = perm.SUPERUSER)
async def set_basepoint(session):
    global basepoint
    match = re.match(r'^ *(\d+)', session.current_arg)
    if not match:
        return
    basepoint = int(match.group(1))
    await session.send(message.MessageSegment.text('设置成功，当前底分：%d' % (basepoint)))

@on_command('加入游戏', aliases=('上桌'), only_to_me = False, permission = perm.GROUP)
async def join_game(session):
    global on_table, table, db
    qqid = int(session.event['user_id'])
    if session.current_arg == '' and session.event.group_id in is_baohuang_open:
        pass
    else:
        has_perm = await perm.check_permission(session.bot, session.event, perm.SUPERUSER)
        if not has_perm:
            return
        match = re.match(r'^\[CQ:at,qq=(\d+)\]', session.current_arg)
        if not match:
            return
        qqid = int(match.group(1))
    if db.get_point(qqid) <= 0:
        await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('没积分了你'))
        return
    if table != None:
        await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('游戏已开始不能加入'))
        return
    if qqid in on_table:
        await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('已经加入游戏'))
        return
    if len(on_table) == 5:
        await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('人数已满'))
        return
    on_table.append(qqid)
    await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('加入成功，当前玩家 %d 个' % (len(on_table))))

@on_command('退出游戏', aliases=('下桌'), only_to_me = False, permission = perm.GROUP)
async def exit_game(session):
    global on_table, table
    qqid = int(session.event['user_id'])
    if session.current_arg == '' and session.event.group_id in is_baohuang_open:
        pass
    else:
        has_perm = await perm.check_permission(session.bot, session.event, perm.SUPERUSER)
        if not has_perm:
            return
        match = re.match(r'^\[CQ:at,qq=(\d+)\]', session.current_arg)
        if not match:
            return
        qqid = int(match.group(1))
    if not qqid in on_table:
        await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('未加入游戏，不能退出'))
        return
    if table != None:
        await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('游戏已开始不能退出'))
        return
    on_table.remove(qqid)
    await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('退出成功，当前玩家 %d 个' % (len(on_table))))

def get_string_identity(identity: int) -> str:
    if identity == HUANGDI : return '皇帝'
    if identity == BAOZI : return '保子'
    if identity == DUBAO : return '独保'
    if identity == GEMINGDANG : return '革命党'
    if identity == UNKNOWN : return '未知'
    return ''

def tile_dict_to_string(tiles: dict) -> str:
    ret = ""
    log.logger.debug(str(tiles))
    for tile in reversed_tile_list:
        ret = ret + ("[%s]" % (tile)) * tiles[tile]
    log.logger.debug(ret)
    return ret

def tile_list_to_string(tiles: list) -> str:
    ret = ""
    for tile in tiles:
        ret = ret + ("[%s]" % (tile))
    return ret


@on_command('开始游戏', aliases=('开局'), only_to_me = False, permission = perm.GROUP)
async def start_game(session):
    global on_table, table, buqiang
    if session.current_arg == '' and session.event.group_id in is_baohuang_open:
        qqid = int(session.event['user_id'])
        if table != None:
            await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('游戏已经开始'))
            return
        if not qqid in on_table:
            await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('你未加入游戏，不能开始'))
            return
        if len(on_table) != 5:
            await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('人数未满，不能开局'))
            return
        table = Table(session.event.group_id, on_table)
        msg1 = message.MessageSegment.text('游戏开始')
        for i in range(5): 
            msg1 = msg1 + message.MessageSegment.text('\n[%s]' % (get_string_identity(table.players[table.player_id[i]].get_open_identity()))) + message.MessageSegment.at(table.player_id[i])
        log.logger.debug(str(table.player_id))
        for i in range(5):
            log.logger.debug(str(table.players[table.player_id[i]].get_tiles()))
            
        await session.send(msg1)
        table.qiangdu_begin()
        buqiang = []
        await session.send(message.MessageSegment.text('现在是抢独阶段，如需独保请在群聊中发送「抢独」，否则发送「不抢」'))
        for i in range(5):
            str1 = tile_dict_to_string(table.players[table.player_id[i]].get_tiles())
            log.logger.debug(str1)
            await bot.send_private_msg(user_id = table.player_id[i], message = message.MessageSegment.text(str1), self_id = session.event.self_id)

@on_command('抢独', only_to_me = False, permission = perm.GROUP)
async def qiangdu(session):
    global on_table, table, buqiang
    if session.current_arg == '' and session.event.group_id in is_baohuang_open and table != None:
        qqid = int(session.event['user_id'])
        if table.game_period != 1: return
        if not qqid in table.player_id: return
        if qqid in buqiang: 
            await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('你已经不抢了，不能抢独'))
            return
        table.qiangdu(qqid)
        table.game_begin()
        msg1 = message.MessageSegment.at(qqid) + message.MessageSegment.text('抢独，游戏开始！')
        for i in range(5): 
            msg1 = msg1 + message.MessageSegment.text('\n%d号位：[%s]' % (i + 1, get_string_identity(table.players[table.player_id[i]].get_open_identity()))) + message.MessageSegment.at(table.player_id[i])
        msg1 = msg1 + message.MessageSegment.text('\n[独保]') + message.MessageSegment.at(qqid) + message.MessageSegment.text('请出牌')
        await session.send(msg1)
        for i in range(5):
            str1 = tile_dict_to_string(table.players[table.player_id[i]].get_tiles())
            log.logger.debug(str1)
            await bot.send_private_msg(user_id = table.player_id[i], message = message.MessageSegment.text(str1), self_id = session.event.self_id)

@on_command('不抢', only_to_me = False, permission = perm.GROUP)
async def not_qiangdu(session):
    global on_table, table, buqiang
    if session.current_arg == '' and session.event.group_id in is_baohuang_open and table != None:
        qqid = int(session.event['user_id'])
        if table.game_period != 1: return
        if not qqid in table.player_id: return
        if qqid in buqiang: 
            await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('你已经不抢了'))
            return
        buqiang.append(qqid)
        await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('不抢'))
        if len(buqiang) == 5:
            table.dengji_begin()
            await session.send(message.MessageSegment.text('现在是登基阶段，当前皇帝是：') + message.MessageSegment.at(table.huangdi_id) + message.MessageSegment.text('\n如需登基请在群聊中发送「登基」，否则发送「让位」'))

@on_command('登基', only_to_me = False, permission = perm.GROUP)
async def dengji(session):
    global table
    if session.current_arg == '' and session.event.group_id in is_baohuang_open and table != None:
        qqid = int(session.event['user_id'])
        if table.game_period != 2: return
        if not qqid in table.player_id: return
        if qqid != table.huangdi_id: 
            await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('你又不是皇帝，登你') + message.MessageSegment.emoji(128052) +message.MessageSegment.text('呢？'))
            return
        table.dengji()
        table.mingbao_begin()
        await session.send(message.MessageSegment.text('[皇帝]') + message.MessageSegment.at(qqid) + message.MessageSegment.text('登基\n现在是明暗保阶段') + message.MessageSegment.text('，保子如需明保请在私聊中发送「明保」，否则在私聊种发送「暗保」'))

@on_command('让位', only_to_me = False, permission = perm.GROUP)
async def rangwei(session):
    global table
    if session.current_arg == '' and session.event.group_id in is_baohuang_open and table != None:
        qqid = int(session.event['user_id'])
        if table.game_period != 2: return
        if not qqid in table.player_id: return
        if qqid != table.huangdi_id: 
            await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('你又不是皇帝，让你') + message.MessageSegment.emoji(128052) +message.MessageSegment.text('呢？'))
            return
        is_success = table.rangwei()
        if is_success == -2:
            await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('你没有足够的2，不能让位'))
            return
        await session.send(message.MessageSegment.text('[皇帝]') + message.MessageSegment.at(qqid) + message.MessageSegment.text('让位给了') +  message.MessageSegment.at(table.huangdi_id) + message.MessageSegment.text('，新皇帝如需如需登基请在群聊中发送「登基」，否则发送「让位」\n当前让位所需2：%d' % (table.rangwei2)))
        str1 = tile_dict_to_string(table.players[qqid].get_tiles())
        log.logger.debug(str1)
        str2 = tile_dict_to_string(table.players[table.huangdi_id].get_tiles())
        log.logger.debug(str2)
        await bot.send_private_msg(user_id = qqid, message = message.MessageSegment.text(str1), self_id = session.event.self_id)
        await bot.send_private_msg(user_id = table.huangdi_id, message = message.MessageSegment.text(str2), self_id = session.event.self_id)

@on_command('明保', only_to_me = False, permission = perm.PRIVATE)
async def mingbao(session):
    global table
    if session.current_arg == '' and table != None:
        qqid = int(session.event['user_id'])
        if table.game_period != 3: return
        if not qqid in table.player_id: return
        if qqid != table.baozi_id: 
            await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('你又不是保子，明你') + message.MessageSegment.emoji(128052) +message.MessageSegment.text('呢？'))
            return
        table.mingbao()
        table.game_begin()
        msg1 = message.MessageSegment.at(qqid) + message.MessageSegment.text('明保，游戏开始！')
        for i in range(5): 
            msg1 = msg1 + message.MessageSegment.text('\n%d号位：[%s]' % (i + 1, get_string_identity(table.players[table.player_id[i]].get_open_identity()))) + message.MessageSegment.at(table.player_id[i])
        msg1 = msg1 + message.MessageSegment.text('\n[%s]' % (get_string_identity(table.players[table.huangdi_id].get_open_identity()))) + message.MessageSegment.at(table.huangdi_id) + message.MessageSegment.text('请出牌')
        await bot.send_group_msg(group_id = table.group_id, message = msg1, self_id = session.event.self_id)

@on_command('暗保', only_to_me = False, permission = perm.PRIVATE)
async def anbao(session):
    global table
    if session.current_arg == '' and table != None:
        qqid = int(session.event['user_id'])
        if table.game_period != 3: return
        if not qqid in table.player_id: return
        if qqid != table.baozi_id: 
            await session.send(message.MessageSegment.at(qqid) + message.MessageSegment.text('你又不是保子，暗你') + message.MessageSegment.emoji(128052) +message.MessageSegment.text('呢？'))
            return
        table.anbao()
        table.game_begin()
        msg1 = message.MessageSegment.text('保子选择了暗保，游戏开始！')
        for i in range(5): 
            msg1 = msg1 + message.MessageSegment.text('\n%d号位：[%s]' % (i + 1, get_string_identity(table.players[table.player_id[i]].get_open_identity()))) + message.MessageSegment.at(table.player_id[i])
        msg1 = msg1 + message.MessageSegment.text('\n[%s]' % (get_string_identity(table.players[table.huangdi_id].get_open_identity()))) + message.MessageSegment.at(table.huangdi_id) + message.MessageSegment.text('请出牌')
        await bot.send_group_msg(group_id = table.group_id, message = msg1, self_id = session.event.self_id)


@on_command('我的手牌', only_to_me = False, permission = perm.EVERYBODY)
async def wodeshoupai(session):
    global table
    if session.current_arg== '' and table != None:
        qqid = int(session.event['user_id'])
        log.logger.debug(str((table.player_id, qqid)))
        log.logger.debug(str(qqid in table.player_id))
        if not qqid in table.player_id:
            return
        str1 = tile_dict_to_string(table.players[qqid].get_tiles())
        log.logger.debug(str1)
        await session.send(message.MessageSegment.text(str1))


def ke_to_str(ke:int) -> str:
    if ke == 1: return '头科'
    if ke == 2: return '二科'
    if ke == 3: return '三科'
    if ke == 4: return '二落'
    if ke == 5: return '大落'
    return ''

async def game_end():
    global table,db
    table.game_end()
    msg1 = message.MessageSegment.text('游戏结束\n')
    if table.mutiple == 4: 
        if table.players[table.huangdi_id].get_order() == 1:
            for player in table.player_id:
                if player == table.huangdi_id: table.players[player].point = basepoint * table.mutiple * 4
                else: table.players[player].point = -basepoint * table.mutiple
        else:
            for player in table.player_id:
                if player == table.huangdi_id: table.players[player].point = -basepoint * table.mutiple * 4
                else: table.players[player].point = basepoint * table.mutiple
    elif table.huangdi_id == table.baozi_id:
        if table.players[table.huangdi_id].get_order() == 1:
            for player in table.player_id:
                if player == table.huangdi_id: table.players[player].point = basepoint * table.mutiple * 4
                else: table.players[player].point = -basepoint * table.mutiple
        elif table.players[table.huangdi_id].get_order() >= 3:
            for player in table.player_id:
                if player == table.huangdi_id: table.players[player].point = -basepoint * table.mutiple * 4
                else: table.players[player].point = basepoint * table.mutiple
    else: 
        K = 6 - table.players[table.huangdi_id].get_order() - table.players[table.baozi_id].get_order()
        for player in table.player_id:
            if player == table.huangdi_id: table.players[player].point = basepoint * table.mutiple * 2 * K
            elif player == table.baozi_id: table.players[player].point = basepoint * table.mutiple * K
            else: table.players[player].point = -basepoint * table.mutiple * K
    log.logger.debug('%d 游戏结束' % (table.group_id))
    for i in range(5): 
        msg1 = msg1 + message.MessageSegment.text('\n%d号位：[%s]' % (i + 1, get_string_identity(table.players[table.player_id[i]].get_open_identity()))) + message.MessageSegment.at(table.player_id[i]) + message.MessageSegment.text('位次[%s]，得分：%d 点' % (ke_to_str(table.players[table.player_id[i]].get_order()), table.players[table.player_id[i]].point))
        db.add_point(table.player_id[i], table.players[table.player_id[i]].point)
    await bot.send_group_msg(group_id = table.group_id, message = msg1)
    table = None

@on_command('强行结算', only_to_me = False, permission = perm.SUPERUSER)
async def qiangxingjiesuan(session):
    global table
    if session.current_arg == '' and table != None:
        await session.send(message.MessageSegment.text('强行结算'))
        await game_end()

@on_command('出', only_to_me = False, permission = perm.GROUP)
async def chupai(session):
    global table
    if session.event.group_id in is_baohuang_open and table != None:
        qqid = int(session.event['user_id'])
        if table.game_period != 5: return
        if qqid != table.current_discard: return
        tile_str = session.current_arg_text.strip()
        is_success = table.discard_tile(tile_str)
        if is_success[0] == -1:
            await session.send(message.MessageSegment.text('输入手牌不合法'))
            return
        if is_success[0] == -2:
            await session.send(message.MessageSegment.text('别瞎几把出牌'))
            return
        if is_success[0] == -3:
            await session.send(message.MessageSegment.text('你的牌管不了别人，会不会玩？'))
            return
        if is_success[0] == -4:
            await session.send(message.MessageSegment.text('你就不知道憋6，会不会玩？'))
            return
        if is_success[0] == -5:
            await session.send(message.MessageSegment.text('你就没有你要出的牌，会不会玩？'))
            return
        nxtid = table.get_next_player()
        msg1 = message.MessageSegment.text('上回合：%d号位：[%s]' % (table.players[qqid].table_id + 1, get_string_identity(table.players[qqid].get_open_identity()))) + message.MessageSegment.at(qqid) + message.MessageSegment.text('出牌：%s\n' % (tile_list_to_string(is_success[1]))) 
        
        is_paole = table.paole(qqid)
        if is_paole:
            msg1 = msg1 + message.MessageSegment.text('%d号位：[%s]' % (table.players[qqid].table_id + 1, get_string_identity(table.players[qqid].get_open_identity()))) + message.MessageSegment.at(qqid) + message.MessageSegment.text('跑了，取得了 %s\n' % (ke_to_str(table.players[qqid].get_order())))
            if table.is_game_end():
                await session.send(msg1)
                await game_end()
                return
        else:
            if table.players[qqid].get_tile_count() <= 10:
                msg1 = msg1 + message.MessageSegment.text('%d号位：[%s]' % (table.players[qqid].table_id + 1, get_string_identity(table.players[qqid].get_open_identity()))) + message.MessageSegment.at(qqid) + message.MessageSegment.text('还剩下%d张牌\n' % (table.players[qqid].get_tile_count()))
        msg1 = msg1 + message.MessageSegment.text('%d号位：[%s]' % (table.players[nxtid].table_id + 1, get_string_identity(table.players[nxtid].get_open_identity()))) + message.MessageSegment.at(nxtid) + message.MessageSegment.text('请出牌')
        table.current_discard = nxtid
        await session.send(msg1)
        str1 = tile_dict_to_string(table.players[qqid].get_tiles())
        log.logger.debug(str1)
        await bot.send_private_msg(user_id = qqid, message = message.MessageSegment.text(str1))

@on_command('过牌', aliases=('过', '要不起', 'pass'), only_to_me = False, permission = perm.GROUP)
async def guopai(session):
    global table
    if session.current_arg == '' and session.event.group_id in is_baohuang_open and table != None:
        qqid = int(session.event['user_id'])
        if table.game_period != 5: return
        if qqid != table.current_discard: return
        is_success = table.pass_tile()
        if not is_success: 
            await session.send(message.MessageSegment.text('你是第一手出牌，不能过牌'))
        nxtid = table.get_next_player()
        msg1 = message.MessageSegment.text('最近一次出牌：%d号位：[%s]' % (table.players[table.last_discard].table_id + 1, get_string_identity(table.players[table.last_discard].get_open_identity()))) + message.MessageSegment.at(table.last_discard) + message.MessageSegment.text('出牌：%s\n' % (tile_list_to_string(table.last_tile))) 
        msg1 = msg1 + message.MessageSegment.text('上回合：%d号位：[%s]' % (table.players[qqid].table_id + 1, get_string_identity(table.players[qqid].get_open_identity()))) + message.MessageSegment.at(qqid) + message.MessageSegment.text('过牌：\n' )
        msg1 = msg1 + message.MessageSegment.text('%d号位：[%s]' % (table.players[nxtid].table_id + 1, get_string_identity(table.players[nxtid].get_open_identity()))) + message.MessageSegment.at(nxtid) + message.MessageSegment.text('请出牌')
        table.current_discard = nxtid
        await session.send(msg1)

@on_command('弃牌', only_to_me = False, permission = perm.GROUP)
async def qipai(session):
    global table
    if session.current_arg == '' and session.event.group_id in is_baohuang_open and table != None:
        qqid = int(session.event['user_id'])
        if table.game_period != 5: return
        if qqid == table.current_discard or qqid == table.last_discard: return
        if not qqid in table.player_id: return
        if table.players[qqid].get_order() != 0: return
        table.qipai(qqid)
        msg1 = message.MessageSegment.at(qqid) + message.MessageSegment.text('弃牌, 位次是[%s]' % (ke_to_str(table.players[qqid].get_order())))
        await session.send(msg1)
        if table.is_game_end():
            await game_end()

@on_command('保皇状态', only_to_me = False, permission = perm.GROUP)
async def zhuangtai(session):
    global table
    if session.current_arg == '' and session.event.group_id in is_baohuang_open:
        if table != None:
            msg1 = message.MessageSegment.text('保皇已开始')
            for i in range(5): 
                msg1 = msg1 + message.MessageSegment.text('\n%d号位：[%s]%s' % (i + 1, get_string_identity(table.players[table.player_id[i]].get_open_identity()), ke_to_str(table.players[table.player_id[i]].get_order()))) + message.MessageSegment.at(table.player_id[i])
        else:
            msg1 = message.MessageSegment.text('保皇未开始，当前桌上有%d人' % (len(on_table)))
            for qqid in on_table:
                msg1 = msg1 + message.MessageSegment.text('\n') +  message.MessageSegment.at(qqid)
        await session.send(msg1)