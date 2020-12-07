from os import path
import os
import asyncio
import datetime
import pytz
import re
import sys
import cairosvg
import requests
import numpy as np
import urllib
from PIL import Image
from nonebot import permission as perm
from nonebot import on_command, CommandSession, scheduler
from nonebot import message
from nonebot import get_bot
from nonebot import log

process_url= 'https://www.zhihu.com/equation?tex='

def transparence2white(image):
	x = np.array(image)
	r, g, b, a = np.rollaxis(x, axis=-1)
	r[a == 0] = 255
	g[a == 0] = 255
	b[a == 0] = 255
	x = np.dstack([r, g, b])
	return Image.fromarray(x, 'RGB')

@on_command('tex', aliases=('latex'), only_to_me = False, permission = perm.GROUP)
async def tex2img(session):
	tex = message.unescape(session.current_arg).replace('\n', '')
	png_file = '/root/HoshinoBot/hoshino/modules/tex2img/tex.png'
	svg_file = '/root/HoshinoBot/hoshino/modules/tex2img/tex.svg'
	os.system('curl ' + process_url + urllib.parse.quote(tex) + ' > ' + svg_file)
	svg = open(svg_file, "r")
	st = svg.read();
	svg.close();
	svg = open(svg_file, "w")
	svg.write(st.replace('text font-family=\"monospace\"', 'text font-family=\"Sarasa Mono SC Nerd, Segoe UI Emoji\"'))
	svg.close();
	cairosvg.svg2png(url= svg_file, write_to=png_file, dpi = 480)
	img=Image.open(png_file)
	img=transparence2white(img)
	img.save(png_file)
	await session.send(message.MessageSegment.image(png_file))

