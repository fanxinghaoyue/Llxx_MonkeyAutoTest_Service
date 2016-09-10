# --*coding:utf-8*--
import os
import time

# 导入线程socket需要的模块
import sys 
import socket
import threading, time

# 导入MonkeyRunner 并且命名别名为mr
from com.android.monkeyrunner import MonkeyRunner as mr
from com.android.monkeyrunner import MonkeyDevice as md
from com.android.monkeyrunner import MonkeyImage as mi
path = sys.path[0].replace("lib\\monkeyrunner.jar:", "")
print path
sys.path.append(path + "/../")
import simplejson as json
from __builtin__ import file

# test by lwl
# 用户对象
class client:
    # # 创建一个用户，传入对方连接的套接字接口和用户名
    def __init__(self, skt, username='none'):
        self.skt = skt
        self.username = username
        
    # 发送消息
    def send_msg(self, msg):
        self.skt.send(msg)
        
    # 退出登录
    def logout(self):
        self.skt.close()


# # 客户端列表
clienList = [] 
PARAMS = "params"
ACTION = "action"
class MonkeyService(threading.Thread):
    def __init__(self):
        
        # ## 
        print("start service monkey service")
        # # 开启服务端线程
        ll_socket_service = threading.Thread(target=self.startSocket, args=());
        # 开始运行线程，当这里调用开始之后就会执行hand_user_con
        ll_socket_service.start()  

        self.device = None
        
    def handler_acion(self, message, user):
        if message[ACTION] == "takesnapshot":
            result = self.device.takeSnapshot()
            result.writeToFile (message[PARAMS]["filepath"], 'png')
            print "save file to " + message[PARAMS]["filepath"]
            
    def handler_user_command(self, message, user):
        try:
            target = json.JSONDecoder().decode(message)
            self.handler_acion(target, user)
        except Exception, e:
            print e
            print message
        
    def hand_user_con(self, user):
        # # print "hand_user_con %s" % (user.username)
        dataAll = ""
        while(True):
            try:
                data = user.skt.recv(1024)  # 阻塞线程，接受消息
                dataAll = dataAll + data
                if(data.__len__() != 1057):
                    self.handler_user_command(dataAll, user)
                    dataAll = ""
                    
            except Exception, e:
                print e
                if str(e).strip() == "(10054, 'Software caused connection abort')":
                    self.socket_monkeyrunner_close = True
                    break;
    
    def send_msg(self, msg):
        
        # # 如果客户端关闭之后需要，需要把已经关闭的客户端添加到列表中，然后在最后移除
        removeclienList = []
        # # 给指定用户名的人发送消息
        for usr in clienList:
            try:
                usr.skt.send(msg)
            except:
                removeclienList.append(usr)
                print "send to client error ... "
        
        # # 移除已经关闭的客户端socket
        for usr in removeclienList:
            clienList.remove(usr)
        
    def startSocket(self):
        # 创建一个套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 监听本地(0.0.0.0) 的 9999端口
        s.bind(('0.0.0.0', 9999))
        
        # 设置最多监听5个用户？
        s.listen(5)
        
        while True:
            print u'waiting for client connection...'
            # 等待用户连接，程序会在这里阻塞，当有用户连接到这里的时候，就会执行下面的流程
            sock, addr = s.accept()
            
            # 接收到用户连接，返回连接成功的Socket，创建一个用户
            user = client(sock)
            
            # 将当前用户添加到用户列表(userlist) 中
            clienList.append(user)
            
            # 开启一个线程处理用户连接,target=hand_user_con 的意思是，在调用线程的start方法后执行hand_user_con，args里面传的是
            # hand_user_con 这个方法需要传递的参数
            t = threading.Thread(target=self.hand_user_con, args=(user,));
            
            # 开始运行线程，当这里调用开始之后就会执行hand_user_con
            t.start()  
        s.close()
        print u'service close ...'
    
    
    def run(self):
        self.ctrl = 1
        while self.ctrl == 1:
            
            print ("wait for connection ...")
            # 在导入的时候MonkeyRunner 被命名为了mr,这里开始等待手机的连接
            self.device = mr.waitForConnection()
            print self.device
            time.sleep(1)
            
MonkeyService().run()
