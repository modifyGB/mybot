'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2022-02-17 17:33:28
LastEditors: Renhetian
LastEditTime: 2022-02-17 17:33:28
'''

    elif At in message:
        for i in message[At]:
            if i.target == account:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain('输入/monitor --help命令查看帮助文档')
                ]))
                break