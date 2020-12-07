import hoshino, sqlite3, os ,json
from PIL import Image,ImageFont,ImageDraw

try:
    config = hoshino.config.clanbattlereport.report_config
except:
    hoshino.logger.error('not found config of clanbattlereport')

def get_db_path():
    if not (os.path.isfile(os.path.abspath(os.path.join(os.path.dirname(__file__), "../"
                                                        "yobot/yobot/src/client/yobot_data/yobotdata.db"))) or os.access(os.path.abspath(os.path.join(os.path.dirname(__file__), "../"
                                                                                                                                                      "yobot/yobot/src/client/yobot_data/yobotdata.db")), os.R_OK)):
        raise OSError
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"
                                           "yobot/yobot/src/client/yobot_data/yobotdata.db"))
    return db_path

def get_web_address():
    if not os.path.isfile(os.path.abspath(os.path.join(os.path.dirname(__file__), "../"
                                                       "yobot/yobot/src/client/yobot_data/yobot_config.json"))):
        raise OSError
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"
                                               "yobot/yobot/src/client/yobot_data/yobot_config.json"))
    with open(f'{config_path}', 'r', encoding='utf8')as fp:
        yobot_config = json.load(fp)
    website_suffix = str(yobot_config["public_basepath"])
    web_address = "http://127.0.0.1" + ":" + str(hoshino.config.PORT) + website_suffix
    return web_address

try:
    db_path = get_db_path()
except OSError:
    db_path = config.db_path

def add_text(img: Image,text:str,textsize:int,font=r'QYW3.ttf',textfill='#f060b8',position:tuple=(0,0)):
    img_font = ImageFont.truetype(font=font,size=textsize)
    draw = ImageDraw.Draw(img)
    draw.text(xy=position,text=text,font=img_font,fill=textfill)
    return img

def get_apikey(gid: int) -> str:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f'select apikey from clan_group where group_id={gid}')
    apikey = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return apikey

def get_GmServer(gid: int) -> str:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f'select game_server from clan_group where group_id={gid}')
    game_server = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return game_server