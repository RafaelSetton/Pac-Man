import pygame as pg
from time import sleep
from math import sin, radians
from random import choices, randint
from threading import Thread
Parede = __import__('parede').Parede


class Live:
    def __init__(self, x, y, speed):
        self.abs_x = x
        self.abs_y = y
        self.x = int(self.abs_x)
        self.y = int(self.abs_y)
        self.speed = speed

    def right(self):
        self.abs_x += self.speed
        self.x = int(self.abs_x)

    def left(self):
        self.abs_x -= self.speed
        self.x = int(self.abs_x)

    def down(self):
        self.abs_y += self.speed
        self.y = int(self.abs_y)

    def up(self):
        self.abs_y -= self.speed
        self.y = int(self.abs_y)

    def opposite(self, direction):
        if direction == self.up:
            return self.down
        if direction == self.down:
            return self.up
        if direction == self.left:
            return self.right
        if direction == self.right:
            return self.left


class PacMan(Live):
    def __init__(self, screen, walls):
        self.screen: pg.Surface = screen
        self.walls = walls
        super().__init__(38, 38, 1.5)
        self.move = self.right
        self.opening = True
        self.mouth_angle = 0
        self.raio = 11

        self.power = False
        self.power_over = False

        self.main_color = (255, 255, 0)
        self.power_color = (255, 150, 0)
        self.color = self.main_color

        self.frames = 0

    def ghost_collision(self, ghosts):
        pts = [(self.x + self.raio, self.y), (self.x - self.raio, self.y),
               (self.x, self.y + self.raio), (self.x, self.y - self.raio)]
        for ghost in ghosts:
            for pt in pts:
                if ghost.x < pt[0] < ghost.x + ghost.size and ghost.y < pt[1] < ghost.y + ghost.size:
                    return ghost
        return False

    def wall_collision(self):
        pts = [(self.x + self.raio, self.y), (self.x - self.raio, self.y),
               (self.x, self.y + self.raio), (self.x, self.y - self.raio)]
        for pt in pts:
            if not self.walls.mapa[pt[1] // self.walls.Bsize][pt[0] // self.walls.Bsize]:
                return True
        return False

    def frame(self, key):
        self.frames += 1
        self.move()
        if self.wall_collision():
            self.opposite(self.move)()

        self.change_direction(key)
        self.mouth_angle += 1 if self.opening else -1
        if not 0 < self.mouth_angle < 30:
            self.opening = not self.opening

        if self.map_position == 2:
            Thread(target=self.power_up).start()
        if self.power and self.power_over and self.frames % 10 == 0:
            self.color = self.main_color if self.color == self.power_color else self.power_color

        ret = 1 if self.map_position == 1 else 0
        self.map_position = 3
        return ret

    def power_up(self):
        while self.power:
            self.power_over = False
        self.power = True
        self.color = self.power_color
        sleep(5)
        self.power_over = True
        sleep(2)
        self.power = False
        self.power_over = False
        self.color = self.main_color

    @property
    def map_position(self):
        return self.walls.mapa[self.y//self.walls.Bsize][self.x//self.walls.Bsize]

    @map_position.setter
    def map_position(self, value):
        self.walls.mapa[self.y // self.walls.Bsize][self.x // self.walls.Bsize] = value

    def blit(self, bg_color):
        pg.draw.circle(self.screen, self.color, (self.x, self.y), self.raio)
        displace = int(sin(radians(self.mouth_angle))*self.raio)

        dic = {self.right: [(self.x+self.raio, self.y+displace), (self.x+self.raio, self.y-displace)],
               self.left: [(self.x-self.raio, self.y+displace), (self.x-self.raio, self.y-displace)],
               self.up: [(self.x+displace, self.y-self.raio), (self.x-displace, self.y-self.raio)],
               self.down: [(self.x+displace, self.y+self.raio), (self.x-displace, self.y+self.raio)]}

        points = [(self.x, self.y)] + dic.get(self.move)

        pg.draw.polygon(self.screen, bg_color, points)

    def change_direction(self, key):
        if key:
            dic = {pg.K_RIGHT: self.right,
                   pg.K_LEFT: self.left,
                   pg.K_UP: self.up,
                   pg.K_DOWN: self.down}
            self.move = dic.get(key) or self.move
            self.abs_x += self.walls.Bsize / 2 - self.abs_x % self.walls.Bsize
            self.abs_y += self.walls.Bsize / 2 - self.abs_y % self.walls.Bsize
            self.x = int(self.abs_x)
            self.y = int(self.abs_y)


class Ghost(Live):
    def __init__(self, screen, walls):
        self.walls = walls
        self.screen: pg.Surface = screen
        super().__init__(self.screen.get_width()//2, self.screen.get_height()//2, 1)
        self.direction = self.up
        self.size = 20
        self.color = (randint(20, 150),)*3

    def get_wall(self, x, y):
        return self.walls.mapa[y][x]

    def change_direction(self):
        if self.x % self.walls.Bsize or self.y % self.walls.Bsize:
            return
        x = (self.x+10) // self.walls.Bsize
        y = (self.y+10) // self.walls.Bsize
        up = self.get_wall(x, y - 1)
        down = self.get_wall(x, y + 1)
        left = self.get_wall(x - 1, y)
        right = self.get_wall(x + 1, y)

        oks = []
        if up:
            oks.append(self.up)
        if down:
            oks.append(self.down)
        if left:
            oks.append(self.left)
        if right:
            oks.append(self.right)

        dir_ind = oks.index(self.direction) if self.direction in oks else 5
        opp_ind = oks.index(self.opposite(self.direction)) if self.opposite(self.direction) in oks else 5

        weights = [3 if i == dir_ind else 0 if i == opp_ind else 1 for i in range(len(oks))]

        self.direction = choices(oks, weights=weights)[0] if weights != [0] else self.opposite(self.direction)
        return

    def blit(self):
        margin = (self.walls.Bsize - self.size) // 2
        pg.draw.rect(self.screen, self.color, ((self.x+margin, self.y+margin), (self.size, self.size)))


class Game:
    def __init__(self):
        self.walls = Parede()

        self.screen: pg.Surface = pg.display.set_mode((40*self.walls.Bsize, 30*self.walls.Bsize))
        pg.display.set_caption("Pac Man")
        pg.display.set_icon(pg.image.load("icon.png"))

        self.pac = PacMan(self.screen, self.walls)
        self.ghosts = [Ghost(self.screen, self.walls) for _ in range(15)]

        self.running = True
        self.key = None
        self.points = 0

        pg.font.init()
        self.font50 = pg.font.SysFont('Agency FB', 50, True)
        self.font100 = pg.font.SysFont('Agency FB', 100, True)

    def events_handler(self):
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                self.key = event.key
        return events

    def reset(self):
        self.walls = Parede()
        self.pac = PacMan(self.screen, self.walls)
        self.ghosts = [Ghost(self.screen, self.walls) for _ in range(15)]
        self.points = 0

    def game_over(self, win=False):
        info = ("You Won :D", (0, 255, 0)) if win else ("Game Over :(", (255, 0, 0))
        img = self.font100.render(info[0], True, info[1])
        x = (self.screen.get_width() - img.get_width()) // 2
        y = (self.screen.get_height() - img.get_height()) // 2
        self.screen.blit(img, (x, y))
        pg.display.update()

        click = False
        while self.running and not click:
            click = bool([evt for evt in self.events_handler() if evt.type == pg.MOUSEBUTTONDOWN])
        self.reset()

    def spawn_ghost(self):
        for _ in range(10):
            if not self.running:
                break
            sleep(1)
        self.ghosts.append(Ghost(self.screen, self.walls))

    def loop(self):
        while self.running:
            self.events_handler()
            self.screen.fill((0, 0, 0))

            self.points += self.pac.frame(self.key)
            self.key = None

            self.walls.blit(self.screen)
            self.pac.blit(self.walls.color)
            for ghost in self.ghosts:
                ghost.blit()
                ghost.change_direction()
                ghost.direction()
            pts = self.font50.render(str(self.points), True, (255, 255, 255))
            self.screen.blit(pts, (0, 0))

            collision = self.pac.ghost_collision(self.ghosts)
            if isinstance(collision, Ghost):
                if self.pac.power:
                    self.ghosts.remove(collision)
                    self.points += 10
                    Thread(target=self.spawn_ghost).start()
                else:
                    self.game_over()

            if self.walls.is_empty():
                self.game_over(True)

            pg.display.update()
            sleep(0.01)


Game().loop()
