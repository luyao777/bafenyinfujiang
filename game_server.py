# -*- coding:utf-8 -*-

import socket
import threading        # 导入线程模块
import random
import time

random_seed = random.random()

class volume_avg:
    def __init__(self):
        self.n = 0
        self.avg_vol = 0
        self.sum_vol = 0
        self.client_vol = {}

    def avg(self,client,vol):
        self.client_vol[client] = vol
        self.n = len(self.client_vol)
        self.sum_vol = 0
        for key in self.client_vol.keys():
            self.sum_vol += self.client_vol[key]
        self.avg_vol = int(self.sum_vol / self.n)
        return self.avg_vol

client_vol_send = volume_avg()

base_vol = 0

def link_handler(link, client):
    global base_vol
    global random_seed
    link.sendall('随机数种子为:'.encode())
    link.sendall(str(random_seed).encode())

    """
    该函数为线程需要执行的函数，负责具体的服务器和客户端之间的通信工作
    :param link: 当前线程处理的连接
    :param client: 客户端ip和端口信息，一个二元元组
    :return: None
    """
    print("服务器开始接收来自[%s:%s]的请求...." % (client[0], client[1]))
    while True:     # 利用一个死循环，保持和客户端的通信状态
        msg_rece = link.recv(1024).decode()
        if msg_rece == "exit":
            print("结束与[%s:%s]的通信..." % (client[0], client[1]))
            break
        print("来自[%s:%s]的客户端向你发来信息：%s" % (client[0], client[1], msg_rece))

        client_name = str(client[0])+':'+str(client[1])
        link.sendall(str(client_vol_send.avg_vol).encode())
        client_vol_rece = int(msg_rece)
        client_vol_send.avg(client_name,client_vol_rece)
        
        # link.sendall(str(client_vol_send.avg_vol).encode())
    link.close()


ip_port = ('0.0.0.0', 19090)
sk = socket.socket()            # 创建套接字
sk.bind(ip_port)                # 绑定服务地址
sk.listen(5)                    # 监听连接请求

print('启动socket服务，等待客户端连接...')

num_connect = 0
t_list = []
time_start = time.time()
num_players = 2

while True:     # 一个死循环，不断的接受客户端发来的连接请求
    conn, address = sk.accept()  # 等待连接，此处自动阻塞
    # 每当有新的连接过来，自动创建一个新的线程，
    # 并将连接对象和访问者的ip信息作为参数传递给线程的执行函数
    t = threading.Thread(target=link_handler, args=(conn, address))
    t_list.append(t)
    num_connect += 1
    if num_connect == num_players:
        for t in t_list: 
            t.start()
        
        
