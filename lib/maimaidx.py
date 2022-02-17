'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2022-02-17 17:56:19
LastEditors: Renhetian
LastEditTime: 2022-02-17 23:00:57
'''

from collections import defaultdict
import re

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image as GraiaImage
from graia.ariadne.message.parser.base import DetectPrefix, DetectSuffix, MatchContent, MatchRegex
from graia.ariadne.model import Group, Member

from lib.app import *
from lib.tool import hash
from lib.maimaidx_music import *
from lib.image import *
from lib.maimai_best_40 import generate
from lib.maimai_best_50 import generate50


music_aliases = defaultdict(list)
f = open('data/maibot/aliases.csv', 'r', encoding='utf-8')
tmp = f.readlines()
f.close()
for t in tmp:
    arr = t.strip().split('\t')
    for i in range(len(arr)):
        if arr[i] != "":
            music_aliases[arr[i].lower()].append(arr[0])


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
async def fenshuxian(message: MessageChain, app: Ariadne, group: Group, member: Member):
    argv = message.asDisplay().split(' ')
    r = r"([绿黄红紫白])(id)?([0-9]+)"
    if len(argv) == 3 and argv[-1] == 'help':
        s = '''
            此功能为查找某首歌分数线设计。\n
            命令格式：/maimai 分数线 <难度+歌曲id> <分数线>\n
            例如：分数线 紫799 100\n
            命令将返回分数线允许的 TAP GREAT 容错以及 BREAK 50落等价的 TAP GREAT 数。\n
            以下为 TAP GREAT 的对应表：\n
            GREAT/GOOD/MISS\n
            TAP\t1/2.5/5\n
            HOLD\t2/5/10\n
            SLIDE\t3/7.5/15\n
            TOUCH\t1/2.5/5\n
            BREAK\t5/12.5/25(外加200落)\n
            '''
        await app.sendGroupMessage(group, MessageChain.create([
                Plain(s)
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


@bcc.receiver("GroupMessage", decorators=[DetectSuffix('是什么歌')])
async def what_song(message: MessageChain, app: Ariadne, group: Group, member: Member):
    regex = r"(.+)是什么歌"
    name = re.match(regex, message.asDisplay()).groups()[0].strip().lower()
    if name not in music_aliases:
        await app.sendGroupMessage(group, MessageChain.create([
                Plain("未找到此歌曲\n舞萌 DX 歌曲别名收集计划：https://www.bilibili.com/video/BV1134y1o7hi")
            ]))
        return
    result_set = music_aliases[name]
    if len(result_set) == 1:
        music = total_list.by_title(result_set[0])
        await app.sendGroupMessage(group, MessageChain.create([
                Plain("您要找的是不是\n"),
                Plain(f"{music.id}. {music.title}\n"),
                GraiaImage(url=f"https://www.diving-fish.com/covers/{music.id}.jpg"),
                Plain(f"\n{'/'.join(music.level)}"),
            ]))
    else:
        s = '\n'.join(result_set)
        await app.sendGroupMessage(group, MessageChain.create([
                Plain(f"您要找的可能是以下歌曲中的其中一首：\n{ s }")
            ]))


@bcc.receiver("GroupMessage", decorators=[MatchRegex(regex=r"/maimai ^([绿黄红紫白]?)id([0-9]+)")])
async def chage(message: MessageChain, app: Ariadne, group: Group, member: Member):
    regex = r"([绿黄红紫白]?)id([0-9]+)"
    groups = re.match(regex, message.asDisplay()).groups()
    level_labels = ['绿', '黄', '红', '紫', '白']
    if groups[0] != "":
        try:
            level_index = level_labels.index(groups[0])
            level_name = ['Basic', 'Advanced', 'Expert', 'Master', 'Re: MASTER']
            name = groups[1]
            music = total_list.by_id(name)
            chart = music['charts'][level_index]
            ds = music['ds'][level_index]
            level = music['level'][level_index]
            file = f"https://www.diving-fish.com/covers/{music['id']}.jpg"
            if len(chart['notes']) == 4:
                msg = f'''{level_name[level_index]} {level}({ds})
                        TAP: {chart['notes'][0]}
                        HOLD: {chart['notes'][1]}
                        SLIDE: {chart['notes'][2]}
                        BREAK: {chart['notes'][3]}
                        谱师: {chart['charter']}'''
            else:
                msg = f'''{level_name[level_index]} {level}({ds})
                        TAP: {chart['notes'][0]}
                        HOLD: {chart['notes'][1]}
                        SLIDE: {chart['notes'][2]}
                        TOUCH: {chart['notes'][3]}
                        BREAK: {chart['notes'][4]}
                        谱师: {chart['charter']}'''
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f"{music['id']}. {music['title']}\n"),
                GraiaImage(url=file),
                Plain(msg)
            ]))
        except Exception:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("未找到该谱面")
            ]))
    else:
        name = groups[1]
        music = total_list.by_id(name)
        try:
            file = f"https://www.diving-fish.com/covers/{music['id']}.jpg"
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f"{music['id']}. {music['title']}\n"),
                GraiaImage(url=file),
                Plain(f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}")
            ]))
        except Exception:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("未找到该乐曲")
            ]))


@bcc.receiver("GroupMessage", decorators=[MatchContent('今日舞萌')])
async def choub(message: MessageChain, app: Ariadne, group: Group, member: Member):
    await app.sendGroupMessage(group, MessageChain.create([
            Plain("mai你🐎个臭b")
        ]))


@bcc.receiver("GroupMessage", decorators=[MatchRegex(regex=r"^/maimai 查歌.+")])
async def chage2(message: MessageChain, app: Ariadne, group: Group, member: Member):
    regex = "查歌(.+)"
    name = re.match(regex, str(message.asDisplay())).groups()[0].strip()
    if name == "":
        return
    res = total_list.filter(title_search=name)
    if len(res) == 0:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain("没有找到这样的乐曲。")
        ]))
    elif len(res) < 50:
        search_result = ""
        for music in sorted(res, key = lambda i: int(i['id'])):
            search_result += f"{music['id']}. {music['title']}\n"
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(search_result.strip())
        ]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f"结果过多（{len(res)} 条），请缩小查询范围。")
        ]))


@bcc.receiver("GroupMessage", decorators=[MatchRegex(regex=r"^/maimai 随个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?")])
async def fenshuxian(message: MessageChain, app: Ariadne, group: Group, member: Member):
    regex = r"随个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)"
    res = re.match(regex, message.asDisplay().lower())
    try:
        if res.groups()[0] == "dx":
            tp = ["DX"]
        elif res.groups()[0] == "sd" or res.groups()[0] == "标准":
            tp = ["SD"]
        else:
            tp = ["SD", "DX"]
        level = res.groups()[2]
        if res.groups()[1] == "":
            music_data = total_list.filter(level=level, type=tp)
        else:
            music_data = total_list.filter(level=level, diff=['绿黄红紫白'.index(res.groups()[1])], type=tp)
        if len(music_data) == 0:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("没有这样的乐曲哦。"),
            ]))
        else:
            music = music_data.random()
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(f"{music.id}. {music.title}\n"),
                GraiaImage(url=f"https://www.diving-fish.com/covers/{music.id}.jpg"),
                Plain(f"\n{'/'.join(music.level)}"),
            ]))
    except Exception as e:
        print(e)
        await app.sendGroupMessage(group, MessageChain.create([
                Plain("随机命令错误，请检查语法"),
            ]))
