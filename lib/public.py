'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2022-02-17 17:33:28
LastEditors: Renhetian
LastEditTime: 2022-02-17 18:15:22
'''

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Group, Member
from graia.ariadne.message.parser.base import MentionMe

from lib.app import *


@bcc.receiver("GroupMessage", decorators=[MentionMe()])
async def group_message_handler(message: MessageChain, app: Ariadne, group: Group, member: Member):
    await app.sendGroupMessage(group, MessageChain.create([
        Plain('输入/monitor --help命令查看帮助文档')
    ]))