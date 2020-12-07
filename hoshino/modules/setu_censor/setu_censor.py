import asyncio
import nonebot
import re
import sys
import requests
from aip import AipContentCensor

cqbot = nonebot.get_bot()
imgfolderdir = '/root/data/setu_collected/'

def saveImg(url, imgname):
    r = requests.get(url)
    nonebot.log.logger.debug(imgfolderdir + imgname + '.' + r.headers['Content-Type'][6:])
    with open(imgfolderdir + imgname + '.' + r.headers['Content-Type'][6:], 'wb') as f:
        f.write(r.content)

def downloadImg(url):
    r = requests.get(url)
    return r.content
    
def Check_Baidu(imgurl, imgname):
    imgContent = downloadImg(imgurl)
    if len(imgContent) < 2e4 or len(imgContent) > 1e7:
        return

    censor_APP_ID = '22842022'
    censor_API_KEY = 'SEBH4QACKkEpGX7NRr7f4tYY'
    censor_SECRET_KEY = '0oI6FfOHbCuWSFlbgIpnlsBUGkKfOgxt'
    
    #classify_APP_ID = '17981247'
    #classify_API_KEY = '3HuleW8fwIPymQcRM1DNhigp'
    #classify_SECRET_KEY = 'LcClAOmKwGSIXR2st8ishMXUPXkiLaaI'
    
    censor_client = AipContentCensor(censor_APP_ID, censor_API_KEY, censor_SECRET_KEY)
    censor_result = censor_client.imageCensorUserDefined(imgurl)
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

@cqbot.on_message
async def process_image_message(context):
    if context["message_type"] == "group":
        match = re.match(r'^\[CQ:image,file=(.*),url=(.*)]$', context['raw_message'])
        if not match:
            return
        name = match.group(1)
        url = match.group(2)
        nonebot.log.logger.debug(url)
        t = Check_Baidu(url, name)
        if t == 1:
            await cqbot.send_group_msg(group_id = int(context['group_id']), message = nonebot.message.MessageSegment.text('涩图！'))




        
