'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2022-02-17 17:33:28
LastEditors: Renhetian
LastEditTime: 2022-02-17 18:58:46
'''

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.model import Group, Member
from graia.ariadne.message.parser.base import ContainKeyword, DetectPrefix, Mention, MentionMe

from lib.app import *
from setting.mirai_setting import account


@bcc.receiver("GroupMessage", decorators=[ContainKeyword(At(account))])
async def group_message_handler(message: MessageChain, app: Ariadne, group: Group, member: Member):
    await app.sendGroupMessage(group, MessageChain.create([
        Plain('输入/monitor --help命令查看帮助文档')
    ]))