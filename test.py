from SDK12306 import Login

login = Login.Login()
login.username = ""
login.password = ""
login.init_cookies()
login.get_captcha_answer()
login.verify_answer()
result = login.login()
if not result:
    print("登陆失败")
    exit()
print(login.nickname)
print(login.cookies)