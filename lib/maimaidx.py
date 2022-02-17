'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2022-02-17 17:56:19
LastEditors: Renhetian
LastEditTime: 2022-02-17 21:36:11
'''

import re

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


@bcc.receiver("GroupMessage", decorators=[DetectPrefix('/maimai b40')])
async def b40(message: MessageChain, app: Ariadne, group: Group, member: Member):
    username = message.asDisplay().split(' ')
    username = username[2] if len(username)>2 else ""
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
                GraiaImage(base64=image_to_base64(img).decode('utf-8'))
            ]))


@bcc.receiver("GroupMessage", decorators=[DetectPrefix('/maimai b50')])
async def b50(message: MessageChain, app: Ariadne, group: Group, member: Member):
    username = message.asDisplay().split(' ')
    username = username[2] if len(username)>2 else ""
    if username == "":
        payload = {'qq': member.id}
    else:
        payload = {'username': username}
    img, success = await generate50(payload)
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
                GraiaImage(base64=image_to_base64(img).decode('utf-8'))
            ]))


@bcc.receiver("GroupMessage", decorators=[DetectPrefix('/maimai 分数线')])
async def b50(message: MessageChain, app: Ariadne, group: Group, member: Member):
    argv = message.asDisplay().split(' ')
    r = r"([绿黄红紫白])(id)?([0-9]+)"
    if len(argv) == 3 and argv[-1] == 'help':
        s = '''
此功能为查找某首歌分数线设计。
命令格式：/maimai 分数线 <难度+歌曲id> <分数线>
例如：分数线 紫799 100
命令将返回分数线允许的 TAP GREAT 容错以及 BREAK 50落等价的 TAP GREAT 数。
以下为 TAP GREAT 的对应表：
GREAT/GOOD/MISS
TAP\t1/2.5/5
HOLD\t2/5/10
SLIDE\t3/7.5/15
TOUCH\t1/2.5/5
BREAK\t5/12.5/25(外加200落)
'''
        await app.sendGroupMessage(group, MessageChain.create([
                GraiaImage(base64=image_to_base64(text_to_image(s)).decode('utf-8'))
            ]))
    elif len(argv) == 4:
        try:
            grp = re.match(r, argv[2]).groups()
            level_labels = ['绿', '黄', '红', '紫', '白']
            level_labels2 = ['Basic', 'Advanced', 'Expert', 'Master', 'Re:MASTER']
            level_index = level_labels.index(grp[0])
            chart_id = grp[2]
            line = float(argv[3])
            music = total_list.by_id(chart_id)
            chart: Dict[Any] = music['charts'][level_index]
            tap = int(chart['notes'][0])
            slide = int(chart['notes'][2])
            hold = int(chart['notes'][1])
            touch = int(chart['notes'][3]) if len(chart['notes']) == 5 else 0
            brk = int(chart['notes'][-1])
            total_score = 500 * tap + slide * 1500 + hold * 1000 + touch * 500 + brk * 2500
            break_bonus = 0.01 / brk
            break_50_reduce = total_score * break_bonus / 4
            reduce = 101 - line
            if reduce <= 0 or reduce >= 101:
                raise ValueError
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f'''{music['title']} {level_labels2[level_index]}
分数线 {line}% 允许的最多 TAP GREAT 数量为 {(total_score * reduce / 10000):.2f}(每个-{10000 / total_score:.4f}%),
BREAK 50落(一共{brk}个)等价于 {(break_50_reduce / 100):.3f} 个 TAP GREAT(-{break_50_reduce / total_score * 100:.4f}%)''')
            ]))
        except Exception:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("格式错误，输入“/maimai 分数线 help”以查看帮助信息")
            ]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([
                Plain("格式错误，输入“/maimai 分数线 help”以查看帮助信息")
            ]))