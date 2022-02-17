'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2022-02-17 17:33:28
LastEditors: Renhetian
LastEditTime: 2022-02-17 23:14:20
'''

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.model import Group, Member
from graia.ariadne.message.parser.base import ContainKeyword, MatchContent

from lib.app import *
from setting.mirai_setting import account


@bcc.receiver("GroupMessage", decorators=[ContainKeyword(At(account))])
async def group_message_handler(message: MessageChain, app: Ariadne, group: Group, member: Member):
    await app.sendGroupMessage(group, MessageChain.create([
        Plain('输入/help命令查看帮助文档')
    ]))

@bcc.receiver("GroupMessage", decorators=[MatchContent('/help')])
async def group_message_handler(message: MessageChain, app: Ariadne, group: Group, member: Member):
    await app.sendGroupMessage(group, MessageChain.create([
        Plain('monitor模块：\n'),
        Plain('/monitor\n'),
        Plain('--add-dynamic        关注动态\n'),
        Plain('--remove-dynamic     取关动态\n'),
        Plain('--list-dynamic       查看动态关注列表\n'),
        Plain('--add-live           关注动态\n'),
        Plain('--remove-live        取关动态\n'),
        Plain('--list-live          查看动态关注列表\n'),
        Plain('\n'),
        Plain('maimai模块：\n'),
        Plain('/maimai\n'),
        Plain('b40      懂得都懂\n'),
        Plain('b50      懂得都懂\n'),
        Plain('分数线   后面加help查看咋用\n'),
        Plain('查歌     后面加要查的歌曲名\n'),
    ]))