# -*- coding: utf-8 -*-
import cocos
import urllib
from defines import *

class Gameover(cocos.layer.ColorLayer):
    def __init__(self, game):
        super(Gameover, self).__init__(0, 0, 0, 255, WIDTH, HEIGHT)
        self.game = game
        self.score = cocos.text.Label(u'分数：%d' % self.game.score,
                                      font_name=FONTS,
                                      font_size=36)
        self.score.position = 200, 340
        self.add(self.score)

        menu = cocos.menu.Menu(u'你挂了……')
        menu.font_title['font_name'] = FONTS
        menu.font_item['font_name'] = FONTS
        menu.font_item_selected['font_name'] = FONTS        
        replay = cocos.menu.MenuItem(u'再来一次', self.replay)
        replay.y = -100
        menu.create_menu([replay])
        self.add(menu)

    def input_name(self, txt):
        self.game.name = txt
        if len(txt) > 16:
            self.game.name = txt[:16]


    def replay(self):
        self.game.reset()
