# coding=utf-8
# bjutNet.py
# Created: 2017-08-30

'''
北京工业大学校园网连接相关方法
'''

__author__  = 'wangke'
__version__ = '1.0'

import requests
import re

class bjutNet(object):
    """docstring for bjutNet"""

    # ipv4单独认证与ipv6 ipv4同时认证的认证地址为 LOGIN_URL_V4
    # ipv6单独认证的认证地点为 LOGIN_URL_V6
    LOGIN_URL_V6 = 'https://lgn6.bjut.edu.cn/'
    LOGOUT_URL_V6 = 'https://lgn6.bjut.edu.cn/F.htm'
    LOGIN_URL_V4 = 'https://lgn.bjut.edu.cn/'
    LOGOUT_URL_V4 = 'https://lgn.bjut.edu.cn/F.htm'

    def __init__(self, userid, passwd, debug=True):
        self.userid = userid
        self.passwd = passwd
        self.debug  = debug
        self.debug_info = ''

    def get_debug_info(self):
        return self.debug_info

    def _debug_out(self, text):
        if self.debug : 
            print(text)
        self.debug_info += text
        self.debug_info += ' '

    def _debug_info(self, html):
        #print(html)
        try:
            msgs = re.findall('Msg=(.*?);time=',html, re.S)
            msgas = re.findall('msga=\'(.*?)\'', html, re.S)
            if len(msgs)>0 and len(msgas)>0:
                msg = msgs[0]
                msga = msgas[0]
            else:  
                return
            tips = ['',
                    '',
                    '该账号正在使用中，请您与网管联系',
                    '本账号只能在指定地址使用',
                    '本账号费用超支或时长流量超过限制',
                    '本账号暂停使用',
                    'System buffer full',
                    '',
                    '本账号正在使用,不能修改',
                    '新密码与确认新密码不匹配,不能修改',
                    '密码修改成功',
                    '本账号只能在指定地址使用',
                    '',
                    '',
                    '注销成功 Logout successfully',
                    '登录成功 Login successfully'
            ]
            case = int(msg)
            #self._debug_out(str(case))
            if case==1 and msga!='' : 
                if msga=='error0': 
                    self._debug_out('本IP不允许Web方式登录')
                elif msga=='error1' : 
                    self._debug_out('本账号不允许Web方式登录')
                elif  msga=='error2' : 
                    self._debug_out('本账号不允许修改密码')
                else :
                    self._debug_out(msga)
            else : 
                self._debug_out('账号或密码不对，请重新输入')
            if case>1 : 
                self._debug_out(tips[case])
        except Exception as e:
            pass

    def get_headers(self):
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }
        return headers

    def get_ipv6_address(self):
        '''
        只有登录之前才可以通过此函数获取ipv6地址
        '''
        try:
            html = requests.get(self.LOGIN_URL_V6)
            html.raise_for_status()
            ipv6 = re.findall('v46ip=\'(.*?)\'', html.text, re.S)[0]
            return ipv6
        except Exception as e:
            return ''

    def get_ipv4_serip(self):
        '''
        只有登录之前才可以通过此函数获取ipv4 serip
        '''
        try:
            html = requests.get(self.LOGIN_URL_V4)
            html.raise_for_status()
            serip = re.findall('v4serip=\'(.*?)\'', html.text, re.S)[0]
            return serip
        except Exception as e:
            return ''

    def _login(self, l_type='ipv4'):
        if l_type=='ipv4':
            v46s = 1
            url = self.LOGIN_URL_V4
        else:
            v46s = 2
            url = self.LOGIN_URL_V6
        serip = self.get_ipv4_serip()
        data = {'DDDDD': self.userid,
                'upass': self.passwd,
                'v46s': v46s,
                'v6ip':'',
                'f4serip': serip,
                '0MKKey': ''
        }
        try:
            r = requests.post(url, data=data, headers=self.get_headers())
            r.raise_for_status()
            r.encoding = 'gb2312'
            self._debug_info(r.text)
            if r.text.find('您已经成功登录') != -1:
                return True
            else: 
                return False
        except Exception as e:
            print(e)
            return False

    def login_ipv4(self):
        return self._login('ipv4')

    def login_ipv6(self): 
        return self._login('ipv6')

    def login_ipv46(self):
        v6ip = self.get_ipv6_address()
        data = {'DDDDD': self.userid,
                'upass': self.passwd,
                'v6ip':v6ip,
                '0MKKey': 'Login'
        }
        try:
            r = requests.post(self.LOGIN_URL_V4, data=data, headers=self.get_headers())
            r.raise_for_status()
            r.encoding = 'gb2312'
            self._debug_info(r.text)
            if r.text.find('您已经成功登录') != -1:
                return True
            else: 
                return False
        except Exception as e:
            return False

    def _parser_account_info(self, html):
        try:
            time = int(re.findall('time=\'(.*?)\'', html, re.S)[0])
            flow = int(re.findall('flow=\'(.*?)\'', html, re.S)[0])
            fee  = int(re.findall('fee=\'(.*?)\'', html, re.S)[0])
            time = time / 60
            flow = float(0.000976562) * flow
            fee  = (fee-fee%100)/10000
            return '%.2f'%time,'%.3f'%flow,'%.2f'%fee
        except Exception as e:
            return 0,0,0

    def get_account_info(self):
        '''
        返回使用时间(H)，使用流量(MB)，余额(RMB元)
        '''

        try:
            r = requests.get(self.LOGIN_URL_V4)
            r.raise_for_status()
            r.encoding = 'gb2312'
            if r.text.find('您已登陆')!=-1 : 
                return self._parser_account_info(r.text)
            r = r.requests.get(self.LOGIN_URL_V6)
            r.raise_for_status()
            r.encoding = 'gb2312'
            if r.text.find('您已登陆')!=-1 : 
                return self._parser_account_info(r.text)
            return 0,0,0
        except Exception as e:
            return

    def logout(self):
        '''
        登出统一调用此函数，自动判断登出url
        '''
        try:
            r = requests.get(self.LOGOUT_URL_V4)
            r.raise_for_status()
            r = requests.get(self.LOGOUT_URL_V6)
            r.raise_for_status()
        except Exception as e:
            return

def test():
    net = bjutNet('x','x')
    print(net.get_ipv6_address())
    print(net.get_ipv4_serip())
    print(net.login_ipv4())
    print(net.login_ipv6())
    print(net.login_ipv46())
    print(net.get_account_info())
    print(net.get_debug_info())
    net.logout()