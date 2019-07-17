# coding=utf-8


class SystemException(RuntimeError):
    def __init__(self, message, code=-1):
        self.message = message
        self.code = code


def exception(code, msg):
    raise SystemException(msg, code)
