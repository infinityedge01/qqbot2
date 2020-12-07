from Crypto.Cipher import AES
import base64
import msgpack
import uuid
Padding = lambda s: s + (16-len(s))*b"\0"  # 用于补全key
# 用于补全下面的text，上面两个网址就是用以下形式补全的
Padding_txt = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16).encode()

def unpack(decrypted_packet):
    try:
        return msgpack.unpackb(decrypted_packet)
    except msgpack.ExtraData as err:
        return err.unpacked
def decrypt(encrypted):
    mode = AES.MODE_CBC
    ss2 = base64.b64decode(encrypted)
    vi = b'ha4nBYA2APUD6Uv1'
    key = ss2[-32:]
    ss2 = ss2[:-32]
    cryptor=AES.new(key,mode, vi)
    plain_text  = cryptor.decrypt(ss2)
    try:
        return msgpack.unpackb(plain_text)
    except msgpack.ExtraData as err:
        return err.unpacked
    except:
        return {"data_headers" : {}, "data" : {}}

def encrypt_nobase64(decrypted, key):
    mode = AES.MODE_CBC
    vi = b'ha4nBYA2APUD6Uv1'
    cryptor=AES.new(key,mode, vi)
    ss1 = msgpack.packb(decrypted)
    ss1 = Padding_txt(ss1)
    plain_text  = cryptor.encrypt(ss1)
    return plain_text

def encrypt(decrypted, key):
    mode = AES.MODE_CBC
    vi = b'ha4nBYA2APUD6Uv1'
    cryptor=AES.new(key,mode, vi)
    ss1 = Padding_txt(decrypted.encode())

    plain_text  = cryptor.encrypt(ss1)
    return base64.b64encode(plain_text + key)
def CreateKey():
    return  base64.b16encode(uuid.uuid1().bytes).lower()


def Pack(request, key):
    encrypted = encrypt_nobase64(request, key)
    return encrypted + key

