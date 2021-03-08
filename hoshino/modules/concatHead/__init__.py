import base64
import pickle
import os
import re
from io import BytesIO
from os import path

import aiohttp
from PIL import Image

from _res import Res as R
import hoshino
from hoshino.service import Service
from hoshino.typing import HoshinoBot, CQEvent
from hoshino.util import DailyNumberLimiter, FreqLimiter
from _util import extract_url_from_event
from .config import *
from .data_source import detect_face, concat, KyaruHead, auto_head, gen_head

conf_path = path.join(path.dirname(__file__), 'user_conf')
sv = Service('接头霸王')
_nlt = DailyNumberLimiter(DAILY_MAX_NUM)
_flt = FreqLimiter(30)

try:
	with open(conf_path, 'rb') as f:
		user_conf_dic = pickle.load(f)
except FileNotFoundError:
	user_conf_dic = {}

@sv.on_prefix(('接头霸王', '接头'))
async def concat_head(bot: HoshinoBot, ev: CQEvent):
	uid = ev.user_id
	if not _nlt.check(uid):
		await bot.finish(ev, '你今天接太多头了')

	if not _flt.check(uid):
		await bot.finish(ev, '你接太多头了')
	max_head = 3
	scale = [1.0] * 10
	rotate = [0] * 10
	x_offset = [0] * 10
	y_offset = [0] * 10
	args = ev.raw_message.split(' ')
	for arg in args:
		if arg.startswith('max_head='):
			tmp = arg.strip('max_head=')
			if len(tmp) > 2 or not tmp.isdigit():
				await bot.finish(ev, '头数不合法，为1-10之间的整数')
			tmp = int(tmp)
			if(tmp < 1 or tmp > 10):
				await bot.finish(ev, '头数不合法，为1-10之间的整数')
			max_head = tmp
			
			hoshino.logger.debug('max_head=%d' % (tmp))
		else:
			for i in range(10):
				if arg.startswith('scale%d=' % (i)):
					tmp = arg[7:]
					if not re.match(r'^([0-9]{1,}[.][0-9]*)$', tmp):
						await bot.finish(ev, '缩放倍数不合法, 为0-10之间的小数（含小数点）')
					tmp = float(tmp)
					if tmp < 0 or tmp > 10:
						await bot.finish(ev, '缩放倍数不合法, 为0-10之间的小数（含小数点）')
					scale[i] = tmp
					hoshino.logger.debug('scale[%d]=%.6lf' % (i, tmp))
				if arg.startswith('rotate%d=' % (i)):
					tmp = arg[8:]
					if len(tmp) > 3 or not tmp.isdigit():
						await bot.finish(ev, '旋转角度不合法，为0-360之间的整数')
					tmp = int(tmp)
					if(tmp < 0 or tmp > 360):
						await bot.finish(ev, '旋转角度不合法，为0-360之间的整数')
					rotate[i] = tmp
					
					hoshino.logger.debug('rotate[%d]=%d' % (i, tmp))
				if arg.startswith('x_offset%d=' % (i)):
					tmp = arg[10:]
					flag = 1
					if tmp.startswith('-'):
						flag = -1
						tmp = tmp[1:]
					if len(tmp) > 4 or not tmp.isdigit():
						await bot.finish(ev, 'x偏移量不合法，为绝对值<10000的整数')
					tmp = int(tmp)
					tmp = tmp * flag
					x_offset[i] = tmp
					
					hoshino.logger.debug('x_offset[%d]=%d' % (i, tmp))
				if arg.startswith('y_offset%d=' % (i)):
					tmp = arg[10:]
					flag = 1
					if tmp.startswith('-'):
						flag = -1
						tmp = tmp[1:]
					if len(tmp) > 4 or not tmp.isdigit():
						await bot.finish(ev, 'y偏移量不合法，为绝对值<10000的整数')
					tmp = int(tmp)
					tmp = tmp * flag
					y_offset[i] = tmp
					
					hoshino.logger.debug('y_offset[%d]=%d' % (i, tmp))
	url = extract_url_from_event(ev)
	if not url:
		await bot.finish(ev, '请附带图片')
	url = url[0]
	await bot.send(ev, '正在接头')

	_nlt.increase(uid)
	_flt.start_cd(uid, 30)

	# download picture and generate base64 str
	# b百度人脸识别api无法使用QQ图片服务器的图片，所以使用base64
	async with  aiohttp.ClientSession() as session:
		async with session.get(url) as resp:
			cont = await resp.read()
			b64 = (base64.b64encode(cont)).decode()
			img = Image.open(BytesIO(cont))

	face_data_list = await detect_face(b64, max_head)
	#print(face_data_list)
	if not face_data_list:
		await bot.finish(ev, '未检测到人脸信息')

	uid = ev.user_id
	head_name = user_conf_dic.get(uid, 'auto')
	output = '' ######
	head_gener = gen_head()
	for i in range(len(face_data_list)):
		dat = face_data_list[i]
		if head_name == 'auto':
			#head = auto_head(dat)
			head = head_gener.__next__() 
		else:
			head = KyaruHead.from_name(head_name)
		output = concat(img, head, dat, scale[i], rotate[i], x_offset[i], y_offset[i])
	pic = R.image_from_memory(output)
	print(pic)
	await bot.send(ev, pic)


@sv.on_prefix('选头')
async def choose_head(bot: HoshinoBot, ev: CQEvent):
	global user_conf_dic
	uid = ev.user_id
	head_name = ev.raw_message.strip('选头')
	if head_name == 'auto':
		user_conf_dic[uid] = 'auto'
		with open(conf_path, 'wb') as f:
			pickle.dump(user_conf_dic, f)
		await bot.finish(ev, '已切换为自动选头')

	user_conf_dic[uid] = head_name
	if not KyaruHead.exist_head(head_name):
		await bot.finish(ev, '没有这个头哦~')
	with open(conf_path, 'wb') as f:
		pickle.dump(user_conf_dic, f)
	head = KyaruHead.from_name(head_name)
	await bot.send(ev, f'头已经切换为{head.cqcode}')



