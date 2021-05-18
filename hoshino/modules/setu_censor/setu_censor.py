import asyncio
import nonebot
import re
import sys
import requests
import random
import datetime
from aip import AipContentCensor
from hoshino import Service
sv = Service("涩图识别")
cqbot = nonebot.get_bot()
imgfolderdir = '/root/data/setu_collected/'

from .database import *
db = Database(sys.path[0])
def saveImg(url, imgname):
    print('Saving image' + url)
    r = requests.get(url)
    nonebot.log.logger.debug(imgfolderdir + imgname + '.' + r.headers['Content-Type'][6:])
    with open(imgfolderdir + imgname + '.' + r.headers['Content-Type'][6:], 'wb') as f:
        f.write(r.content)

def downloadImg(url):
    r = requests.head(url).headers
    if 'Size' in r:
        print('Size: ' + r['Size'])
        return int(r['Size'])
    return 0

    
async def Check_Baidu(imgurl, imgname):
    imgContent = downloadImg(imgurl)
    if imgContent < 5e4 or imgContent > 1e7:
        return
    
    #classify_APP_ID = '17981247'
    #classify_API_KEY = '3HuleW8fwIPymQcRM1DNhigp'
    #classify_SECRET_KEY = 'LcClAOmKwGSIXR2st8ishMXUPXkiLaaI'
    censor_APP_ID = '22842022'
    censor_API_KEY = 'SEBH4QACKkEpGX7NRr7f4tYY'
    censor_SECRET_KEY = '0oI6FfOHbCuWSFlbgIpnlsBUGkKfOgxt'
    censor_client = AipContentCensor(censor_APP_ID, censor_API_KEY, censor_SECRET_KEY)
    
    censor_result = censor_client.imageCensorUserDefined(imgurl)
    #print(censor_result)
    if 'data' in censor_result:
        s = ''
        for each in censor_result['data']:
            s = s + each['msg'] + str(each['probability']) + ' '
        
        nonebot.log.logger.debug(s)
        for each in censor_result['data']:
            #print('type', each['type'], 'prob', each['probability'])
            if each['msg']=='存在卡通色情不合规' and each['probability']>0.25:
                nonebot.log.logger.debug('卡通色情%.6f' % each['probability'])
                saveImg(imgurl, imgname)
                return 1
            elif each['msg']=='存在卡通女性性感不合规' and each['probability']>0.25:
                nonebot.log.logger.debug('卡通女性性感%.6f' % each['probability'])
                saveImg(imgurl, imgname)
                return 1
            elif each['msg']=='存在卡通亲密行为不合规' and each['probability']>0.25:
                nonebot.log.logger.debug('卡通亲密行为%.6f' % each['probability'])
                saveImg(imgurl, imgname)
                return 1
    return 0

contrib_count = 0
def update_contrib_count():
    global contrib_count
    time = datetime.datetime.now().hour * 6 + datetime.datetime.now().minute // 10
    db.update_total_contrib(time, contrib_count)
    contrib_count = 0
@sv.scheduled_job('cron', minute = '*/10')
async def _call():
    await asyncio.sleep(10)
    update_contrib_count()
update_contrib_count()

@cqbot.on_message
async def process_image_message(context):
    if context["message_type"] == "group":
        for x in context['message']:
            if x['type'] == 'image':
                url = x['data']['url']
                name = url[-41:-9]
                nonebot.log.logger.debug(name)
                t = await Check_Baidu(url, name)
                if t == 1:
                    global contrib_count
                    contrib_count += 1
                    db.update_contrib(context['user_id'])
                    await cqbot.send_group_msg(group_id = int(context['group_id']), message = nonebot.message.MessageSegment.text('涩图！'))
                    rnd = random.randint(1,5)
                    if rnd == 1:
                        await cqbot.send_group_msg(group_id = int(context['group_id']), message = nonebot.message.MessageSegment.text('只要涩图存入库中「涩图！」一响，你的灵魂立刻从炼狱直升天堂'))
                    return
