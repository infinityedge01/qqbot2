import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import requests
from hoshino.typing import *
from hoshino.util import pic2b64
from io import BytesIO
from PIL import Image,ImageFont,ImageDraw


avatar_size = 67
axis1 = [(209, 853), (209, 974), (209, 1093), (209, 1210), (209, 1330)]
axis2 = [(744, 853), (744, 974), (744, 1093), (744, 1210), (744, 1330)]
axis11 = [(378, 853), (378, 974), (378, 1093), (378, 1210), (378, 1330)]
axis12 = [(498, 853+32), (498, 974+32), (498, 1093+32), (498, 1210+32), (498, 1330+32)]
axis21 = [(378+535, 853), (378+535, 974), (378+535, 1093), (378+535, 1210), (378+535, 1330)]
axis22 = [(498+535, 853+32), (498+535, 974+32), (498+535, 1093+32), (498+535, 1210+32), (498+535, 1330+32)]



def paint(data: dict):
    img = Image.open("hoshino/modules/setu_statistic/bg.png")

    x_data = data["time"]
    y_data = data["message"]
    plt.figure(figsize=(6,3), facecolor='white')
    plt.plot(x_data,y_data,'-')
    
    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
    plt.grid()
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=False, dpi=75)
    bar_img1 = Image.open(buf)
    img.paste(bar_img1, (160, 388))
    buf.close()
    x_data = data["time"]
    y_data1 = data["setu_in"]
    y_data2 = data["setu_out"]
    
    
    plt.rcParams['font.family'] = ['Microsoft YaHei']
    plt.figure(figsize=(6,3))
    plt.plot(x_data,y_data1,'-', label = '接收')
    plt.plot(x_data,y_data2,'-', color='r', label='发送')
    
    
    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
    plt.legend()
    plt.grid()
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=False, dpi=75)
    bar_img1 = Image.open(buf)
    img.paste(bar_img1, (694, 388))
    buf.close()
    ttfront = ImageFont.truetype("hoshino/modules/setu_statistic/SimHei.ttf", 24)
    draw = ImageDraw.Draw(img)
    for i in range(5):
        buf = BytesIO()
        avatar = ''
        if data["sepi"][i][2] == 0:
            avatar = Image.open("hoshino/modules/setu_statistic/unknown.png")
        else:
            r = requests.get(data["sepi"][i][0])
            buf.write(r.content)
            avatar = Image.open(buf)
        avatar = avatar.resize((avatar_size, avatar_size), Image.BILINEAR)    
        img.paste(avatar, axis1[i])
        if data["sepi"][i][2] != 0:
            draw.text(axis11[i], data["sepi"][i][1], fill='#000000',font=ttfront)
        draw.text(axis12[i], str(data["sepi"][i][2]), fill='#000000',font=ttfront)
        buf.close()
    for i in range(5):
        buf = BytesIO()
        avatar = ''
        if data["contribution"][i][2] == 0:
            avatar = Image.open("hoshino/modules/setu_statistic/unknown.png")
        else:
            r = requests.get(data["contribution"][i][0])
            buf.write(r.content)
            avatar = Image.open(buf)
        avatar = avatar.resize((avatar_size, avatar_size), Image.BILINEAR)    
        img.paste(avatar, axis2[i])
        if data["contribution"][i][2] != 0:
            draw.text(axis21[i], data["contribution"][i][1], fill='#000000',font=ttfront)
        draw.text(axis22[i], str(data["contribution"][i][2]), fill='#000000',font=ttfront)
        buf.close()
    img = pic2b64(img)
    img = MessageSegment.image(img)
    return img