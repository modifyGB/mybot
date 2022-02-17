from threading import Thread
import requests
import hashlib
import json
import time
import os

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.model import Group, Member
from graia.ariadne.message.parser.base import DetectPrefix

from lib.event import *
from lib.app import *
from setting.bot_setting import delay_time


if os.path.exists('config/bili_monitor/setting.json') == False:
    os.makedirs('config/bili_monitor')
    open('config/bili_monitor/setting.json','w').write(r'{"dynamic":{},"live":{}}')
if os.path.exists('tmp/bili_monitor/') == False:
    os.makedirs('tmp/bili_monitor/')
with open('config/bili_monitor/setting.json','r+') as file:
    group_dict = json.loads(file.read())


@bcc.receiver("DynamicEvent")
async def dynamic(event: DynamicEvent):
    uid = event.uid
    js = event.js
    images_url = None
    mc = ''

    if 'item' in js:
        body = js['item']['description'] if 'description' in js['item'] else js['item']['content']
        images_url = [i['img_src'] for i in js['item']['pictures']] if 'pictures' in js['item'] else None
        images_url = [download(i) for i in images_url] if images_url != None else None
        name = js['user']['name'] if 'name' in js['user'] else js['user']['uname']
        mc = MessageChain.create([
                Plain('你关注的@{}(id:{})发布了一条动态\n\n'.format(name,uid)),
                Plain(body)
            ])
        if images_url != None:
            mc += MessageChain.create([Image(path=i) for i in images_url if i != None])
    elif 'aid' in js:
        images_url = [download(js['pic'])]
        title = js['title']
        url = js['short_link']
        name = js['owner']['name']
        mc = MessageChain.create([
                Plain('你关注的@{}(id:{})发布了一个视频，快来看看吧\n\n'.format(name,uid)),
                Plain(title+'\n')
            ])
        if images_url != None:
            mc += MessageChain.create([Image(path=i) for i in images_url if i != None])
        mc += MessageChain.create([Plain('\n视频网址: '+url)])
    elif 'author' in js:
        title = js['title']
        url = 'https://www.bilibili.com/read/cv' + str(js['id'])
        name = js['author']['name']
        images_url = [download(i) for i in js['image_urls']]
        mc = MessageChain.create([
                Plain('你关注的@{}(id:{})发布了一条专栏文章，快来看看吧\n\n'.format(name,uid)),
                Plain(title+'\n')
            ])
        if images_url != None:
            mc += MessageChain.create([Image(path=i) for i in images_url if i != None])
        mc += MessageChain.create([Plain('\n专栏网址: '+url)])
    
    for i in group_dict['dynamic'][uid]:
        group = await app.getGroup(i)
        if group != None:
            await app.sendGroupMessage(group, mc)
        else:
            group_dict['dynamic'][uid].remove(i)
            print('群不存在，已删除')
            update()

    [os.remove(i) for i in images_url if i != None] if images_url != None else None


@bcc.receiver("LiveEvent")
async def live(event: LiveEvent):
    uid = event.uid
    js = event.js
    name = js['name']
    url = js['live_room']['url']
    title = js['live_room']['title']
    cover_path = download(js['live_room']['cover'])
    mc = MessageChain.create([
            Plain('你关注的@{}(id:{})开启了直播，快来看看吧~\n\n'.format(name,uid)),
            Plain(title+'\n')
        ])
    if cover_path != None:
        mc += MessageChain.create([Image(path=cover_path)])
    mc += MessageChain.create([Plain('\n直播间地址: '+url)])
    for i in group_dict['live'][uid]:
        group = await app.getGroup(i)
        if group != None:
            await app.sendGroupMessage(group, mc)
        else:
            group_dict['live'][uid].remove(i)
            print('群不存在，已删除')
            update()
    os.remove(cover_path)


@bcc.receiver("GroupMessage", decorators=[DetectPrefix('/monitor')])
async def monitor_handle(message: MessageChain, app: Ariadne, group: Group, member: Member):
    list = message.asDisplay().split(' ')

    if list[1] == '--add-dynamic' and len(list) > 2 and list[2].isdigit():
        if list[2] not in group_dict['dynamic']:
            group_dict['dynamic'][list[2]] = []
            Thread(target=dynamic_thread,args=(list[2],)).start()
        if group.id not in group_dict['dynamic'][list[2]]:
            group_dict['dynamic'][list[2]].append(group.id)
        await app.sendGroupMessage(group, MessageChain.create([Plain('关注成功')]))
        update()
    elif list[1] == '--remove-dynamic' and len(list) > 2 and list[2].isdigit():
        if list[2] in group_dict['dynamic'].keys() and group.id in group_dict['dynamic'][list[2]]:
            group_dict['dynamic'][list[2]].remove(group.id)
            update()
        await app.sendGroupMessage(group, MessageChain.create([Plain('移除成功')]))
    elif list[1] == '--list-dynamic':
        add_list = []
        for i in group_dict['dynamic'].keys():
            if group.id in group_dict['dynamic'][i]:
                add_list.append(i)
        if len(add_list):
            await app.sendGroupMessage(group, MessageChain.join(
                MessageChain.create([Plain('dynamic关注id列表:\n')]),
                MessageChain.create([Plain(i+'\n') for i in add_list])
                ))
        else:
            await app.sendGroupMessage(group, MessageChain.create([Plain('没有关注任何人')]))

    elif list[1] == '--add-live' and len(list) > 2 and list[2].isdigit():
        if list[2] not in group_dict['live']:
            group_dict['live'][list[2]] = []
            Thread(target=live_thread,args=(list[2],)).start()
        if group.id not in group_dict['live'][list[2]]:
            group_dict['live'][list[2]].append(group.id)
        await app.sendGroupMessage(group, MessageChain.create([Plain('关注成功')]))
        update()
    elif list[1] == '--remove-live' and len(list) > 2 and list[2].isdigit():
        if list[2] in group_dict['live'].keys() and group.id in group_dict['live'][list[2]]:
            group_dict['live'][list[2]].remove(group.id)
            update()
        await app.sendGroupMessage(group, MessageChain.create([Plain('移除成功')]))
    elif list[1] == '--list-live':
        add_list = []
        for i in group_dict['live'].keys():
            if group.id in group_dict['live'][i]:
                add_list.append(i)
        if len(add_list):
            await app.sendGroupMessage(group, MessageChain.join(
                MessageChain.create([Plain('live关注id列表:\n')]),
                MessageChain.create([Plain(i+'\n') for i in add_list])
                ))
        else:
            await app.sendGroupMessage(group, MessageChain.create([Plain('没有关注任何人')]))

    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain('参数有误')]))


def dynamic_thread(uid):
    last_dynamic_time = 0
    url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid=' + uid
    res = requests.get(url)
    if res.status_code == 200:
        last_dynamic_time = json.loads(res.text)['data']['cards'][0]['desc']['timestamp']
    else:
        print('dynamic error: '+str(res.status_code)+' id: '+uid)
        print('dynamic监听器结束运行 id:'+uid)
        exit()
    print('dynamic监听器正常运行 id:'+uid)
    time.sleep(delay_time)

    while(True):
        if len(group_dict['dynamic'][uid]) == 0:
            del group_dict['dynamic'][uid]
            update()
            break
        res = requests.get(url)
        if res.status_code == 200:
            js = json.loads(res.text)
            if last_dynamic_time < js['data']['cards'][0]['desc']['timestamp']:
                for i in js['data']['cards']:
                    if i['desc']['timestamp'] <= last_dynamic_time:
                        break
                    js_card = json.loads(i['card'])
                    bcc.postEvent(DynamicEvent(uid,js_card))
                last_dynamic_time = js['data']['cards'][0]['desc']['timestamp']
        else:
            print('dynamic error: '+str(res.status_code)+' id: '+uid)
            break
        time.sleep(delay_time)
    print('dynamic监听器结束运行 id:'+uid)


def live_thread(uid):
    is_live = 1
    url = 'https://api.bilibili.com/x/space/acc/info?mid=' + uid
    print('live监听器正常运行 id:'+uid)

    while(True):
        if len(group_dict['live'][uid]) == 0:
            del group_dict['live'][uid]
            update()
            break
        res = requests.get(url)
        if res.status_code == 200:
            js = json.loads(res.text)['data']
            if is_live == 0 and js['live_room']['liveStatus'] == 1 and js['live_room']['roundStatus'] == 0:
                bcc.postEvent(LiveEvent(uid,js))
            is_live = js['live_room']['liveStatus']
        else:
            print('live error: '+str(res.status_code)+' id: '+uid)
        time.sleep(delay_time)
    print('live监听器结束运行 id:'+uid)
 

def update():
    with open('config/bili_monitor/setting.json','w+') as file:
        file.write(json.dumps(group_dict))


def download(url):
    path = hashlib.md5(url.encode('utf-8')).hexdigest()
    if os.path.exists('tmp/bili_monitor') == False:
        os.makedirs('tmp/bili_monitor')
    try:
        with open('tmp/bili_monitor/'+path,'wb+') as file:
            file.write(requests.get(url).content)
        return 'tmp/bili_monitor/'+path
    except Exception:
        print('图片下载出错')
        return None
 

for i in group_dict['dynamic'].keys():
    Thread(target=dynamic_thread,args=(i,)).start()
for i in group_dict['live'].keys():
    Thread(target=live_thread,args=(i,)).start()