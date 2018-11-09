# -*- coding: utf-8 -*-
import cocos

class Pill(cocos.sprite.Sprite):
    def __init__(self, block):
        super(Pill, self).__init__('pill.png')
        self.game = block.game
        self.ruc = block.game.ruc
        self.floor = block.floor
        self.position = block.x + block.width / 2, block.height + 100

        self.schedule(self.update)

    def update(self, dt):
        px = self.ruc.x + self.ruc.width / 2 - self.floor.x
        py = self.ruc.y + self.ruc.height / 2

        if abs(px - self.x) < 50 and abs(py - self.y) < 50:
            # ruc get pill
            self.parent.remove(self)
            self.ruc.rush()

    def reset(self):
        self.parent.remove(self)
