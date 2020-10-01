from PIL import Image
import pygame as pg
from numpy import asarray


class Parede:
    def __init__(self):
        map_img = Image.open('mapa.png')
        mapa_array_img = asarray(map_img)
        self.mapa = [[rgb[0] // 50 for rgb in linha] for linha in mapa_array_img]
        self.Bsize = 25
        self.color = (165, 165, 210)

    def blit(self, window):
        for row, lista in enumerate(self.mapa):
            for col, value in enumerate(lista):
                if value:
                    pg.draw.rect(window, self.color, ((col*self.Bsize, row*self.Bsize), (self.Bsize, self.Bsize)))
                    if value == 1:
                        color = (100, 255, 100)
                    elif value == 2:
                        color = (255, 100, 100)
                    else:
                        color = self.color
                    pg.draw.circle(window, color, (int((col+0.5)*self.Bsize), int((row+0.5)*self.Bsize)), self.Bsize//5)

    def is_empty(self):
        mapa = [set(l) for l in self.mapa]
        for l in mapa:
            if 1 in l:
                return False
        return True

