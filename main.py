'''
Description: file description
Version: 1.0
Autor: Renhetian
Date: 2022-02-17 14:35:10
LastEditors: Renhetian
LastEditTime: 2022-02-17 17:57:49
'''

from setting.bot_setting import *
from lib.app import *
if is_monitor:
    import lib.monitor
if is_maimaidx:
    import lib.maimaidx
import lib.public


app.launch_blocking()