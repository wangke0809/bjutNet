📦 bjutNet
======

连接北工大校园网的SDK

安装
------

    $ pip install bjutNet

使用
------

    from bjutNet import bjutNet

    net = bjutNet('<id>', '<pass>')

    #可选ipv4/ipv6/ipv46，均返回逻辑类型
    
    net.login_ipv4()
    net.login_ipv6()
    net.login_ipv46()

    #认证成功后可查看账户信息
    
    time,flow,fee = net.get_account_info()
    print("已用时长 %s 小时 , 已用流量 %s MB , 余额 %s 元"%(time,flow,fee))

    #统一退出接口
    
    net.logout()

高级用法
------

    #默认开启debug，可配置为关闭，关闭后不在输出错误信息
    
    net = bjutNet('<id>', '<pass>', False)

    #关闭后，在登录返回False之后接着调用此函数主动查看错误信息
    
    print(net.get_debug_info())

我的微信
------

.. image:: https://raw.githubusercontent.com/wangke0809/bjutNet/master/wx.png
