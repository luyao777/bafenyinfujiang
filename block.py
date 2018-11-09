# -*- coding: utf-8 -*-
import random
import cocos
from pill import Pill

class Block(cocos.sprite.Sprite):
    def __init__(self, game):
        super(Block, self).__init__('black.png')

        self.random_seed = game.random_seed
        random.seed(self.random_seed)
        self.game = game
        self.ruc = game.ruc
        self.floor = game.floor
        self.active = True
        self.image_anchor = 0, 0
        self.reset()

        self.schedule(self.update)

    def update(self, dt):
        if self.active and self.x < self.ruc.x - self.floor.x:
            self.active = False
            self.game.add_score()
        if self.x + self.width + self.game.floor.x < -10:
            self.reset()

    def reset(self):
        x, y = self.game.last_block
        if x == 0:
            self.scale_x = 5
            self.scale_y = 1
            self.position = 0, 0
            self.active = False
        else:
            self.scale_x = 0.75 + random.random() * 2
            self.scale_y = min(max(y - 50 + random.random() * 100, 50), 300) / 100.0
            self.position = x + 80 + random.random() * 100, 0
            self.active = True
            # random add pill
            if self.x > 1000 and random.random() > 0.6:
                self.floor.add(Pill(self))
        self.game.last_block = self.x + self.width, self.height
