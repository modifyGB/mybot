'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2022-02-17 15:27:40
LastEditors: Renhetian
LastEditTime: 2022-02-17 15:35:11
'''
from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession
from setting.mirai_setting import *

app = Ariadne(MiraiSession(
    host=host, 
    verify_key=verify_key, 
    account=account
    ))
bcc = app.broadcast