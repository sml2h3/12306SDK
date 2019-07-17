# coding=utf-8

import base64
import requests
import random
import json
import time
import numpy as np
import cv2
from io import BytesIO
import os
import sys
from SDK12306 import Exceptions


class Login(object):

    def __init__(self):

        self.conf_url = "https://kyfw.12306.cn/otn/login/conf"

        self.auth_url = "https://kyfw.12306.cn/passport/web/auth/uamtk-static"

        self.captcha_url = "https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand"

        self.detect_url = "http://127.0.0.1:8080/huoche"

        self.verfy_captcha_url = "https://kyfw.12306.cn/passport/captcha/captcha-check?answer={}&rand=sjrand&login_site=E&_={}"

        self.logdevice_url = "https://kyfw.12306.cn/otn/HttpZF/logdevice"

        self.login_url = "https://kyfw.12306.cn/passport/web/login"

        self.passport_url = "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin"

        self.uamtk_url = "https://kyfw.12306.cn/passport/web/auth/uamtk"

        self.uamauthclient_url = "https://kyfw.12306.cn/otn/uamauthclient"

        self.user_login_url = "https://kyfw.12306.cn/otn/login/userLogin"

        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://kyfw.12306.cn/otn/resources/login.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        }

        self.session = None

        self._cookies = requests.utils.cookiejar_from_dict([])

        self._username = ""

        self._password = ""

        self._nickname = ""

        self._tk = ""

        self._answers = []

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        self._username = username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = password

    @property
    def cookies(self):
        return self._cookies

    @cookies.setter
    def cookies(self, cookies):
        self._cookies = cookies

    @property
    def answer(self):
        return self._answers

    @answer.setter
    def answer(self, answers):
        self._answers = answers

    @property
    def nickname(self):
        return self._nickname

    @nickname.setter
    def nickname(self, nickname):
        self._nickname = nickname

    @property
    def tk(self):
        return self._tk

    @tk.setter
    def tk(self, tk):
        self._tk = tk

    def init_cookies(self):

        self.session = requests.session()

        self.session.get(self.conf_url)

        resp = self.session.post(self.auth_url, data={"appid": "otn"})

        payload = {
            "algID": "taeJtzL0GW",
            "hashCode": "N2V7Ruwhdl5nhJnRQhcfugWE2I6PnkbbN_5YXWm6j5M",
            "FMQw": "0",
            "q4f3": "zh-CN",
            "VySQ": "FGEYxqRkIjw4_ljDppwW1yQUWLEwlhoU",
            "VPIf": "1",
            "custID": "133",
            "VEek": "unknown",
            "dzuS": "29.0 r0",
            "yD16": "0",
            "EOQP": "8f58b1186770646318a429cb33977d8c",
            "lEnu": "168430947",
            "jp76": "6bf21fb5ce3520a40d4eba60aeb4d6ac",
            "hAqN": "Win32",
            "platform": "WEB",
            "ks0Q": "aed1bae228495349d158e5d3f601249b",
            "TeRS": "1040x1920",
            "tOHY": "24xx1080x1920",
            "Fvje": "i1l1o1s1",
            "q5aJ": "-8",
            "wNLf": "99115dfb07133750ba677d055874de87",
            "0aew": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            "E3gR": "8665805c3af9a467bc48f8a3852ed4b7",
            "timestamp": str(int(time.time() * 1000))
        }

        device = self.session.get(self.logdevice_url, params=payload)

        device_dict = json.loads(device.text[18: -2])

        self.RAIL_DEVICEID = device_dict['dfp']

        self.RAIL_EXPIRATION = device_dict['exp']

        self.cookies = requests.utils.add_dict_to_cookiejar(resp.cookies, {'RAIL_DEVICEID': self.RAIL_DEVICEID,
                                                                           'RAIL_EXPIRATION': self.RAIL_EXPIRATION})
        return True

    def get_captcha_answer(self):
        captcha_img_dict = self.session.get(self.captcha_url, cookies=self.cookies)

        captcha_img_dict = captcha_img_dict.json()

        if captcha_img_dict['result_code'] == "0":
            image_b64 = captcha_img_dict['image']
            image = base64.b64decode(image_b64)

            files = {'file': ('a.jpg', BytesIO(image), 'application')}
            resp = requests.post(self.detect_url, files=files)
            pointers = resp.text.split(',')
            answer = []
            for p in pointers:
                p = int(p)
                if p < 5:
                    y = random.randint(45, 98)
                else:
                    y = random.randint(115, 170)
                y = y - 40
                if p > 4:
                    p = p - 4
                x_min = 67 * (p - 1) + 5 * p + 10
                x_max = x_min + 40
                x = random.randint(x_min, x_max)
                answer += (str(x), str(y))
            answers = ','.join(answer)
            self.answer = answers
            return True
        else:
            Exceptions.exception(-5, "验证码识别错误")

    def verify_answer(self):
        verfy_captcha_url = self.verfy_captcha_url.format(self.answer, str(int(time.time() * 1000)))
        resp = self.session.get(verfy_captcha_url)
        if resp.json()['result_code'] == "4":

            self.cookies = requests.utils.add_dict_to_cookiejar(self.session.cookies,
                                                                {'RAIL_DEVICEID': self.RAIL_DEVICEID,
                                                                 'RAIL_EXPIRATION': self.RAIL_EXPIRATION})
            return True
        else:
            print("验证码验证失败")
            return False

    def login(self):
        data = {
            "username": self.username,
            "password": self.password,
            "appid": "otn",
            "answer": ','.join(self.answer)
        }
        resp = self.session.post(self.login_url, headers=self.headers, data=data, cookies=self.cookies)
        resp.encoding = "utf-8"
        if '网络可能存在问题，请您重试一下' in resp.text:
            Exceptions.exception(-4, "网络出错")
        elif resp.json()['result_message'] == "登录成功":
            self.session.get(self.user_login_url, headers=self.headers)
            self.session.get(self.passport_url, headers=self.headers)
            resp = self.session.post(self.uamtk_url, headers=self.headers, data={"appid": "otn"})
            if resp.json()['result_message'] == "验证通过":
                self.tk = resp.json()['newapptk']
                resp = self.session.post(self.uamauthclient_url, headers=self.headers, data={"tk": self.tk})
                if resp.json()['result_message'] == "验证通过":
                    nickname = resp.json()['username']
                    self.tk = resp.json()['apptk']
                    self.nickname = nickname
                    resp = self.session.get(self.user_login_url, headers=self.headers)
                    resp.encoding = "utf-8"
                    return True
                else:
                    Exceptions.exception(-4, resp.json()['result_message'])
            else:
                Exceptions.exception(-4, resp.json()['result_message'])
        else:
            Exceptions.exception(-2, "登陆失败，可能是密码错误")


if __name__ == '__main__':
    login = Login()
    login.username = ""
    login.password = ""
    login.init_cookies()
    login.get_captcha_answer()
    login.verify_answer()
    result = login.login()
    if result:
        print(login.nickname)
        print(login.cookies)