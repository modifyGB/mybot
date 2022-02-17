'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2022-02-17 14:46:35
LastEditors: Renhetian
LastEditTime: 2022-02-17 14:46:35
'''

from graia.broadcast.entities.event import BaseEvent
from graia.broadcast.entities.dispatcher import BaseDispatcher


class DynamicEvent(BaseEvent):
    uid = ''
    js = {}
    def __init__(self,uid,js) -> None:
        super().__init__()
        self.uid = uid
        self.js = js
    class Dispatcher(BaseDispatcher):
        pass


class LiveEvent(BaseEvent):
    uid = 0
    js = {}
    def __init__(self,uid,js) -> None:
        super().__init__()
        self.uid = uid
        self.js = js
    class Dispatcher(BaseDispatcher):
        pass
