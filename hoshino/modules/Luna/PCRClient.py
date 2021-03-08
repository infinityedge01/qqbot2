import requests
from .PCRPack import *
import ast
import hashlib
import base64
import random
from nonebot import log
class PCRClient:
    def __init__(self, viewer_id):
        self.viewer_id = viewer_id
        self.request_id = ""
        self.session_id = ""
        self.urlroot = "https://l3-prod-uo-gs-gzlj.bilibiligame.net/"
        self.default_headers={
            "Accept-Encoding": "gzip",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; VTR-AL00 Build/V417IR)",
            "X-Unity-Version": "2017.4.37c2",
            "APP-VER": "2.4.10",
            "BATTLE-LOGIC-VERSION": "3",
            "BUNDLE_VER" : "",
            "CHANNEL-ID": "1",
            "DEVICE": "2",
            "DEVICE-ID": "6d3dd40c2545eab5c8a651d3359358bd",
            "DEVICE-NAME": "HUAWEI VTR-AL00",
            "EXCEL-VER": "1.0.0",
            "GRAPHICS-DEVICE-NAME": "MuMu GL (NVIDIA GeForce RTX 2070 Direct3D11 vs_5_0 ps_5_0)",
            "IP-ADDRESS": "10.1.10.1",
            "KEYCHAIN": "",
            "LOCALE": "CN",
            "PLATFORM": "2",
            "PLATFORM-ID": "4", 
            "PLATFORM-OS-VERSION": "Android OS 6.0.1 / API-23 (V417IR/eng.root.20200623.095831)",
            "REGION-CODE": "",
            "RES-KEY": "d145b29050641dac2f8b19df0afe0e59",
            "RES-VER": "10002200",
            "SHORT-UDID": "0",
            "Connection": "Keep-Alive"}
        self.conn = requests.session()
    def Callapi(self, apiurl, request, crypted = True):
        key = CreateKey()
        if crypted:
            request['viewer_id'] = encrypt(str(self.viewer_id), key).decode()
        else:
            request['viewer_id'] = str(self.viewer_id)
        req = Pack(request, key)
        flag = self.request_id != None and self.request_id != ''
        flag2 = self.session_id != None and self.session_id != ''
        headers = self.default_headers
        if flag: headers["REQUEST-ID"] = self.request_id
        if flag2: headers["SID"] = self.session_id
        resp = self.conn.post(url= self.urlroot + apiurl,
                        headers = headers, data = req)
        null = None
        if crypted:
            ret = decrypt(resp.content)
        else: ret = eval(resp.content.decode())
        ret_header = ret["data_headers"]
        if "sid" in ret_header:
            if ret_header["sid"] != None and ret_header["sid"] != "":
                self.session_id = hashlib.md5((ret_header["sid"] + "c!SID!n").encode()).hexdigest()
        if "request_id" in ret_header:
            if ret_header["request_id"] != None and ret_header["request_id"] != "" and ret_header["request_id"] != self.request_id:
                self.request_id = ret_header["request_id"]
        if "viewer_id" in ret_header:
            if ret_header["viewer_id"] != None and ret_header["viewer_id"] != 0 and ret_header["viewer_id"] != self.viewer_id:
                self.viewer_id = int(ret_header["viewer_id"])
        return ret["data"]
    def login(self, uid, access_key):
        self.manifest = self.Callapi('source_ini/get_maintenance_status', {}, False)
        ver = self.manifest["required_manifest_ver"]
        log.logger.debug(str(self.manifest))
        self.default_headers["MANIFEST-VER"] = ver
        log.logger.debug(str(self.Callapi('tool/sdk_login', {"uid": uid, "access_key" : access_key, "platform" : self.default_headers["PLATFORM-ID"], "channel_id" : self.default_headers["CHANNEL-ID"]}) ))

        log.logger.debug(str(self.Callapi('check/game_start', {"app_type": 0, "campaign_data" : "", "campaign_user": random.randint(1, 1000000)}) ))
        log.logger.debug(str(self.Callapi("check/check_agreement", {}) ))
        self.Callapi("load/index", {"carrier": "HUAWEI"})
        self.Home = self.Callapi("home/index", {'message_id': 1, 'tips_id_list': [], 'is_first': 1, 'gold_history': 0})
        log.logger.debug(str(self.Home))



        

    
    
