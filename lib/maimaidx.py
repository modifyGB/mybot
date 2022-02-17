'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2022-02-17 17:56:19
LastEditors: Renhetian
LastEditTime: 2022-02-17 19:47:16
'''

import os

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image as GraiaImage
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.model import Group, Member

from lib.app import *
from lib.tool import hash
from lib.maimaidx_music import *
from lib.image import *
from lib.maimai_best_40 import generate
from lib.maimai_best_50 import generate50


@bcc.receiver("GroupMessage", decorators=[DetectPrefix('b40')])
async def b40(message: MessageChain, app: Ariadne, group: Group, member: Member):
    username = message.asDisplay().split(' ')
    username = username[1] if len(username)>1 else ""
    if username == "":
        payload = {'qq': member.id}
    else:
        payload = {'username': username}
    img, success = await generate(payload)
    if success == 400:
        await app.sendGroupMessage(group, MessageChain.create([
                Plain("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
            ]))
    elif success == 403:
        await app.sendGroupMessage(group, MessageChain.create([
                Plain("该用户禁止了其他人获取数据。")
            ]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([
                GraiaImage(base64=f"base64://{str(image_to_base64(img), encoding='utf-8')}")
            ]))
