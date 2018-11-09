#coding: utf8
import cocos
from cocos.sprite import Sprite
from pyaudio import PyAudio, paInt16
import pygame
import struct
from ruc import RUC
from block import Block
from gameover import Gameover
from defines import *
import random,time
import socket
from threading import Thread

random_seed = 0

class socket_vol:
    def __init__(self,ip_addr ='127.0.0.1',port = 19090):
        '''
        param ip_addr : str
        param prot    : int
        '''
        global random_seed
        self.ip_port = (ip_addr, port)
        self.clientSocket = socket.socket()     # 创建套接字
        self.clientSocket.connect(self.ip_port)      # 连接服务器

        random_seed = self.clientSocket.recv(1024).decode('utf8')
        

    def sendMsg(self, clientSocket,msg_send):
        msg = str(msg_send)
        clientSocket.send(msg.encode('utf8'))

    def recvMsg(self, clientSocket):
        msg = clientSocket.recv(1024)
        print(msg.decode('utf8'))
        return msg.decode('utf8')
    def start(self):
        tr = Thread(target=self.recvMsg,args=(self.clientSocket,)) #将套接字作为参数传给新线程，各自的线程中分别执行收，发数据
        ts = Thread(target=self.sendMsg,args=(self.clientSocket,))
        ts.start()
        tr.start()

class VoiceGame(cocos.layer.ColorLayer):
    is_event_handler = True

    def __init__(self):
        super(VoiceGame, self).__init__(255, 255, 255, 255, WIDTH, HEIGHT)
        pygame.mixer.init()
        global random_seed
        self.random_seed = random_seed

        self.gameover = None

        self.score = 0  #记录分数
        self.txt_score = cocos.text.Label(u'分数：0',
                                          font_name=FONTS,
                                          font_size=24,
                                          color=BLACK)
        self.txt_score.position = 500, 440
        self.add(self.txt_score, 99999)

        self.top = '', 0
        self.top_notice = cocos.text.Label(u'',
                                          font_name=FONTS,
                                          font_size=18,
                                          color=BLACK)
        self.top_notice.position = 400, 410
        self.add(self.top_notice, 99999)

        self.name = ''

        # init voice
        self.NUM_SAMPLES = 2048  # pyAudio内部缓存的块的大小
        self.LEVEL = 1500  # 声音保存的阈值

        self.voicebar = Sprite('black.png', color=(0, 0, 255))
        self.voicebar.position = 20, 450
        self.voicebar.scale_y = 0.1
        self.voicebar.image_anchor = 0, 0
        self.add(self.voicebar)

        self.ruc = RUC(self)
        self.add(self.ruc)

        self.floor = cocos.cocosnode.CocosNode()
        self.add(self.floor)
        self.last_block = 0, 100
        for i in range(5):
            b = Block(self)
            self.floor.add(b)
            pos = b.x + b.width, b.height

        # 开启声音输入
        pa = PyAudio()
        SAMPLING_RATE = int(pa.get_device_info_by_index(0)['defaultSampleRate'])
        self.stream = pa.open(format=paInt16, channels=1, rate=SAMPLING_RATE, input=True, frames_per_buffer=self.NUM_SAMPLES)
        self.stream.stop_stream()

        # pygame.mixer.music.load('bgm.wav')
        # pygame.mixer.music.play(-1)

        self.schedule(self.update)
        
        self.vol_manager = socket_vol()
        self.vol_manager.start()
        

    def on_mouse_press(self, x, y, buttons, modifiers):
        pass

    def collide(self):
        px = self.ruc.x - self.floor.x
        for b in self.floor.get_children():
            if b.x <= px + self.ruc.width * 0.8 and px + self.ruc.width * 0.2 <= b.x + b.width:
                if self.ruc.y < b.height:
                    self.ruc.land(b.height)
                    break

    def update(self, dt):
        # 读入NUM_SAMPLES个取样
        if self.stream.is_stopped():
            self.stream.start_stream()
        string_audio_data = self.stream.read(self.NUM_SAMPLES)
        # k = max(struct.unpack('2048h', string_audio_data))
        # # print k

        k_ = max(struct.unpack('2048h', string_audio_data))

        ############ k from server ##########
        # time.sleep(3)
        # time.sleep(0.1)
        self.vol_manager.sendMsg(self.vol_manager.clientSocket,k_)
        k = self.vol_manager.recvMsg(self.vol_manager.clientSocket)
        k = int(k)
        #####################################


        self.voicebar.scale_x = k / 10000.0
        if k > 3000:
            if not self.ruc.dead:
                self.floor.x -= min((k / 20.0), 150) * dt
        if k > 8000:
            self.ruc.jump((k - 8000) / 25.0)
        self.floor.x -= self.ruc.velocity * dt
        self.collide()
        self.top_notice.x -= 80 * dt
        if self.top_notice.x < -700:
            self.top_notice.x = 700
        

    def reset(self):
        self.floor.x = 0
        self.last_block = 0, 100
        for b in self.floor.get_children():
            b.reset()
        self.score = 0
        self.txt_score.element.text = u'分数：0'
        self.ruc.reset()
        if self.gameover:
            self.remove(self.gameover)
            self.gameover = None

        self.stream.start_stream()
        self.resume_scheduler()
        pygame.mixer.music.play(-1)
        if self.top[0] and self.top[1]:
            notice = u'%s 刚刚以 %d 分刷新了今日最佳！' % self.top
            self.top_notice.element.text = notice
            self.top_notice.x = 800

    def end_game(self):
        self.stream.stop_stream()
        self.pause_scheduler()
        # self.unschedule(self.update)
        self.gameover = Gameover(self)
        self.add(self.gameover, 100000)

    def show_top(self):
        self.remove(self.gameover)
        self.gameover = None


    def add_score(self):
        self.score += 1
        self.txt_score.element.text = u'分数：%d' % self.score

cocos.director.director.init(caption="八分音符酱-联机")
cocos.director.director.run(cocos.scene.Scene(VoiceGame()))

