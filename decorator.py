#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @ Author: Sricor
# @ Date: 2022-4-21
# @ Last Update: 2022-4-21

import json
import time
import logging
import requests
import functools

class WechatAppPush:
    """
    WechatAppPush decorator
    Push the msg of the decorated function

    Example:
    @WechatAppPush(corpid, corpsecret, agentid)
    def func():
        return 'xxx'

    Also:
    def func():
        return 'xxx'
    WechatAppPush(corpid, corpsecret, agentid)(func())()

    Also:
    WechatAppPush(corpid, corpsecret, agentid)('xxx')()

    Final:
    Then wechat app will push xxx

    :param corpid: wechat app corpid
    :param corpsecret: wechat app corpsecret
    :param agentid: wechat app agentid
    :param touser: (optional) default: @all
    :param message: (optional) default: wechat push message
    :return func:
    docs: https://developer.work.weixin.qq.com/document/path/90236

    """

    def __init__(self, corpid: str, corpsecret: str, agentid: str, touser='@all', message='Wechat push message') -> None:
        self._corpid = corpid
        self._corpsecret = corpsecret
        self._agentid = agentid
        self._touser = touser
        self._message = message

    def __call__(self, func=None):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # before func
            try:
                self._message = func(*args, **kwargs)
            except:
                if func != None:
                    self._message = func
            # after func
            response = self.send_text()
            if response != "ok":
                print(f'Wechat push error: {response}')
            return self._message
        return wrapper
    
    def get_access_token(self) -> str:
        send_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        send_values = {
            "corpid": self._corpid,
            "corpsecret": self._corpsecret,
        }
        response = requests.post(send_url, params=send_values).json()
        return response["access_token"]

    def send_text(self) -> str:
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + self.get_access_token()
        )
        send_values = {
            "touser": self._touser,
            "msgtype": "text",
            "agentid": self._agentid,
            "text": {"content": self._message},
            "safe": "0",
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]


class Debug:
    """
    Debug decorator

    :param level: 
    :param func_time:
    :param func_info: 

    """
    def __init__(self, level=logging.DEBUG, func_time=True, func_info=True) -> None:
        self._func_timer = func_time
        self._level = level
        self._func_info = func_info

    def __call__(self, func):
        @self.func_time
        @self.func_info
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
            DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
            logging.basicConfig(level=self._level, format=LOG_FORMAT, datefmt=DATE_FORMAT)
            value = func(*args, **kwargs)
            return value
        return wrapper

    def func_time(self, func):
        """Print the runtime of the decorated function"""
        if self._func_timer != True:
            return func
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            # before func
            value = func(*args, **kwargs)
            # after func
            end_time = time.perf_counter()
            run_time = end_time - start_time
            print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
            return value
        return wrapper

    def func_info(self, func):
        """Print the function signature and return value"""
        if self._func_info != True:
            return func
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            print(f"Calling {func.__name__}({signature})")
            # before func
            value = func(*args, **kwargs)
            # after func
            print(f"{func.__name__!r} returned {value!r}")
            return value
        return wrapper
