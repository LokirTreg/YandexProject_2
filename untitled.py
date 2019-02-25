import pygame
import random
import sys
import os
from math import atan2, sqrt, degrees

pygame.init()
size = width, height = 1200, 675
fps = 120
screen = pygame.display.set_mode(size)
score = 0
d = 0
fon = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join(name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image

fon1 = pygame.sprite.Sprite()
fon1.image = load_image("fon.jpg")
fon1.rect = fon1.image.get_rect()
fon.add(fon1)



def start_screen():
    intro_text = ["WASD - движение",
                  "Пробел - выстрел",
                  "R - быстрая стрельба",
                  "Нажмите на любую клавишу, чтобы продолжить."]
    screen.fill((0, 0, 0))

    title = pygame.font.Font(None, 120).render('Star Ship Shooter', 1, (255, 0, 0))
    screen.blit(title, ((width - title.get_rect().width) // 2, 200))

    font = pygame.font.Font(None, 30)
    text_coord = 200 + title.get_rect().bottom
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = (width - string_rendered.get_rect().width) // 2
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    color = [255, 0, 0]
    cycle = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        if cycle == 0:
            color[0] -= 1
            color[1] += 1
            if color == [0, 255, 0]:
                cycle = 1
        elif cycle == 1:
            color[1] -= 1
            color[2] += 1
            if color == [0, 0, 255]:
                cycle = 2
        elif cycle == 2:
            color[2] -= 1
            color[0] += 1
            if color == [255, 0, 0]:
                cycle = 0
        title = pygame.font.Font(None, 120).render('Star Ship Shooter', 1, color)
        screen.blit(title, ((width - title.get_rect().width) // 2, 200))

        pygame.display.flip()
        clock.tick(fps)


def gameover_screen(score):
    screen.fill((0, 0, 0))
    intro_text = ['Нажмите на кнопку "Escape", чтобы выйти из игры',
                  "Enter - начать заново", "",
                  "Счёт - {}".format(str(score))]
    title = pygame.font.Font(None, 120).render('Game Over.', 1, pygame.Color('white'))
    screen.blit(title, ((width - title.get_rect().width) // 2, 200))
    font = pygame.font.Font(None, 30)
    text_coord = 200 + title.get_rect().bottom
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = (width - string_rendered.get_rect().width) // 2
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    idle = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit
                elif idle and event.key == pygame.K_RETURN:
                    start()

        pygame.display.flip()
        clock.tick(fps)


def start():
    global score, d
    players = pygame.sprite.Group()
    ground = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles_enemy = pygame.sprite.Group()
    bosses = pygame.sprite.Group()
    score = 0
    boss_level = False
    boss_cooldown = 4500
    d = 0

    class Ground(pygame.sprite.Sprite):
        def __init__(self, group, size, color, x, y):
            super().__init__(group)
            self.below_player = False
            self.image = pygame.Surface(size,
                                        pygame.SRCALPHA, 32)
            pygame.draw.rect(self.image, color,
                             (0, 0, size[0], size[1]))
            self.rect = pygame.Rect(x, y, size[0], size[1])
            self.mask = pygame.mask.from_surface(self.image)

        def update(self):
            if pl.rect.bottom <= self.rect.top:
                self.below_player = True
            else:
                self.below_player = False


    class Player(pygame.sprite.Sprite):
        def __init__(self, group, x, y):
            super().__init__(group)
            self.on_ground = False
            self.cooldown = 0
            self.xvel = 0
            self.yvel = 0
            self.direction = 0
            self.directiony = 0
            self.image = load_image("ship.png", -1)
            self.image = pygame.transform.scale(self.image, (60, 60))
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.rect.move(x, y)
            players.add(self)

        def move(self, xvelocity, yvelocity):
            self.rect = self.rect.move(xvelocity, yvelocity)

    class Projectiles_enemy(pygame.sprite.Sprite):
        def __init__(self, group, x, y, color):
            super().__init__(group)
            self.friendly = self in projectiles
            self.color = color
            self.xremainder = 0
            self.yremainder = 0
            self.image = pygame.Surface((8, 14))
            self.image.set_colorkey((0, 0, 0))
            pygame.draw.polygon(self.image, color, ((0, 0), (8, 0), (4, 14)), 0)
            pygame.draw.polygon(self.image, (0, 0, 0), ((0, 0), (8, 0), (4, 14)), 1)
            self.rect = pygame.Rect(x, y, 8, 14)
            self.mask = pygame.mask.from_surface(self.image)
            self.velx = 0
            self.vely = 4
            if self.friendly:
                self.vely *= 2.5
                pl.cooldown = 10
                if pl.yvel <= 0 and pl.on_ground:
                    pl.on_ground = False
            else:
                self.vely /= 2

        def move(self):
            self.rect = self.rect.move(self.velx + self.xremainder, self.vely + self.yremainder)
            self.xremainder = self.velx + self.xremainder - int(self.velx + self.xremainder)
            self.yremainder = self.vely + self.yremainder - int(self.vely + self.yremainder)

        def update(self):
            self.move()
            if self.friendly:
                for enemy in enemies:
                    if pygame.sprite.collide_mask(self, enemy):
                        enemy.kill()
                        self.kill()
            else:
                if pygame.sprite.collide_mask(self, pl):
                    gameover_screen(score)

            if self.rect.x < -10:
                self.kill()

            if self.rect.x > width + 10:
                self.kill()


    class Projectiles_enemy1(pygame.sprite.Sprite):
        def __init__(self, group, x, y, dir, color, boss):
            super().__init__(group)
            self.friendly = self in projectiles
            self.color = color
            self.xremainder = 0
            self.yremainder = 0
            self.image = pygame.Surface((8, 14))
            self.image.set_colorkey((0, 0, 0))
            pygame.draw.polygon(self.image, color, ((0, 0), (8, 0), (4, 14)), 0)
            pygame.draw.polygon(self.image, (0, 0, 0), ((0, 0), (8, 0), (4, 14)), 1)
            self.image = pygame.transform.rotate(self.image,  degrees(sqrt(atan2(1,3))) * dir)
            self.rect = pygame.Rect(x, y, 8, 14)
            self.mask = pygame.mask.from_surface(self.image)
            self.velx = 2 * dir
            self.vely = 4
            if self.friendly:
                self.vely *= 2.5
                pl.cooldown = 10
                if pl.yvel <= 0 and pl.on_ground:
                    pl.on_ground = False
            else:
                self.vely /= 2
                self.velx /= 2

        def move(self):
            self.rect = self.rect.move(self.velx + self.xremainder, self.vely + self.yremainder)
            self.xremainder = self.velx + self.xremainder - int(self.velx + self.xremainder)
            self.yremainder = self.vely + self.yremainder - int(self.vely + self.yremainder)

        def update(self):
            self.move()
            if self.friendly:
                for enemy in enemies:
                    if pygame.sprite.collide_mask(self, enemy):
                        enemy.kill()
                        self.kill()
            else:
                if pygame.sprite.collide_mask(self, pl):
                    gameover_screen(score)

            if self.rect.x < -10:
                self.kill()

            if self.rect.x > width + 10:
                self.kill()



    class Enemy(pygame.sprite.Sprite):
        def __init__(self, group, x, y, initial_cooldown, ccd, fire_delay, max_rockets):
            super().__init__(group)
            self.initial_cooldown = initial_cooldown
            self.const_cooldown = ccd
            self.cooldown = 0
            self.fire_delay = fire_delay
            self.release_cooldown = initial_cooldown
            self.max_rockets = max_rockets
            self.rockets = 0
            self.image = load_image("ship1.png", (255, 255, 255))
            self.image = pygame.transform.scale(self.image, (120, 120))
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)
            self.coords_x = x
            self.coords_y = y
            self.move(x, y)
            self.hit = False
            self.time = 0

        def move(self, xvelocity, yvelocity):
            self.rect = self.rect.move(xvelocity, yvelocity)

        def update(self):
            if self.hit or self.coords_y >= height:
                self.kill()
            else:
                if self.cooldown == 0:
                    self.rockets = self.max_rockets
                    self.release_cooldown = 0
                    self.cooldown = self.const_cooldown
                else:
                    self.cooldown -= 1
                if self.rockets:
                    if self.release_cooldown == 0:
                        Projectiles_enemy(projectiles_enemy, self.coords_x + 30, self.time -40, (0, 255, 0))
                        Projectiles_enemy(projectiles_enemy, self.coords_x + 84, self.time -40, (0, 255, 0))
                        self.rockets -= 1
                        self.release_cooldown = self.fire_delay
                    else:
                        self.release_cooldown -= 1
            if self.cooldown % 10 == 0:
                self.move(0, 1)
                self.time += 1
            if self.time + 120 >= height or pygame.sprite.collide_mask(self, pl):
                gameover_screen(score)


    class Enemy_2(pygame.sprite.Sprite):
        def __init__(self, group, x, y, initial_cooldown):
            super().__init__(group)
            self.initial_cooldown = initial_cooldown
            self.image = load_image("ship3.jpg", (0, 0, 0))
            self.image = pygame.transform.scale(self.image, (160, 120))
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)
            self.coords_x = x
            self.coords_y = y
            self.move(x, y)
            self.hit = False
            self.time = 0

        def move(self, xvelocity, yvelocity):
            self.rect = self.rect.move(xvelocity, yvelocity)

        def update(self):
            if self.hit or self.coords_y >= height:
                self.kill()
            else:
                self.time += 1
                if self.time <= 40:
                    self.move(0, 3)
                elif self.initial_cooldown == 0:
                    self.move(0, 10)
                else:
                    self.initial_cooldown -= 1
                if pygame.sprite.collide_mask(self, pl):
                    gameover_screen(score)



    class Boss(pygame.sprite.Sprite):
        def __init__(self, group, x, y, initial_cooldown, ccd, fire_delay, max_rockets):
            super().__init__(group)
            self.initial_cooldown = initial_cooldown
            self.const_cooldown = ccd
            self.cooldown = initial_cooldown * 1.8
            self.fire_delay = fire_delay
            self.release_cooldown = initial_cooldown
            self.max_rockets = max_rockets
            self.rockets = 0
            self.image = load_image("ship2.png", -1)
            self.image = pygame.transform.scale(self.image, (174, 240))
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)
            self.coords_x = x
            self.coords_y = y
            self.move(x, y)
            self.hit = 0
            self.time = 0

        def move(self, xvelocity, yvelocity):
            self.rect = self.rect.move(xvelocity, yvelocity)

        def update(self):
            global d
            if self.hit >= 20 or self.coords_y >= height:
                self.kill()
                d -= 1
            else:
                if self.cooldown == 0:
                    self.rockets = self.max_rockets
                    self.release_cooldown = 0
                    self.cooldown = self.const_cooldown
                else:
                    self.cooldown -= 1
                if self.rockets:
                    if self.release_cooldown == 0:
                        Projectiles_enemy(projectiles_enemy, self.coords_x + 84, min(self.time - 20, 260), (0, 255, 255))
                        Projectiles_enemy1(projectiles_enemy, self.coords_x + 66, min(self.time - 40, 260), -1, (0, 255, 255), self)
                        Projectiles_enemy1(projectiles_enemy, self.coords_x + 96 , min(self.time - 40, 260), 1, (0, 255, 255), self)
                        self.rockets -= 1
                        self.release_cooldown = self.fire_delay
                    else:
                        self.release_cooldown -= 1
            if self.time < 280:
                self.move(0, 1)
            self.time += 1
            if pygame.sprite.collide_mask(self, pl):
                gameover_screen(score)



    class Projectile(pygame.sprite.Sprite):
        def __init__(self, group, x, y, color):
            super().__init__(group)
            self.friendly = self in projectiles
            self.color = color
            self.xremainder = 0
            self.yremainder = 0
            self.image = pygame.Surface((8, 14))
            self.image.set_colorkey((0, 0, 0))
            pygame.draw.polygon(self.image, color, ((0, 14), (8, 14), (4, 0)), 0)
            pygame.draw.polygon(self.image, (0, 0, 0), ((0, 14), (8, 14), (4, 0)), 1)
            self.rect = pygame.Rect(x, y, 14, 8)
            self.mask = pygame.mask.from_surface(self.image)
            self.velx = 0
            self.vely = -4
            if self.friendly:
                self.vely *= 2.5
                pl.cooldown = 10
                if pl.yvel <= 0 and pl.on_ground:
                    pl.on_ground = False
            else:
                self.velx /= 2
                self.vely /= 2

        def move(self):
            self.rect = self.rect.move(self.velx + self.xremainder, self.vely + self.yremainder)
            self.xremainder = self.velx + self.xremainder - int(self.velx + self.xremainder)
            self.yremainder = self.vely + self.yremainder - int(self.vely + self.yremainder)


        def update(self):
            global score
            self.move()
            if self.friendly:
                for enemy in enemies:
                    if pygame.sprite.collide_mask(self, enemy):
                        enemy.hit = True
                        score += 10
                        self.kill()
                for boss in bosses:
                    if pygame.sprite.collide_mask(self, boss):
                        boss.hit += 1
                        score += 10
                        self.kill()

            if self.rect.x < -120 or self.rect.y < -120:
                self.kill()

            if  self.rect.x > width + 10 or self.rect.y > height + 10:
                self.kill()



    running = True
    ray = False
    pl = Player(players, (width + 60) // 2, 615)
    enemy_cooldown = 60
    ray_cooldown = 0

    try:
        while running:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        pl.direction = -3
                    elif event.key == pygame.K_d:
                        pl.direction = 3
                    elif event.key == pygame.K_w:
                        pl.directiony = -3
                    elif event.key == pygame.K_s:
                        pl.directiony = 3
                    elif ray == False and ray_cooldown == 0 and event.key == pygame.K_r:
                        ray = True
                        ray_cooldown = 120
                    elif event.key == pygame.K_SPACE and ray == False:
                        if pl.cooldown == 0:
                            Projectile(projectiles, pl.rect.x + 12, pl.rect.y + 10,
                                       pygame.Color('red'))
                            Projectile(projectiles, pl.rect.x + 40, pl.rect.y + 10,
                                       pygame.Color('red'))
                    elif event.key == pygame.K_p:
                        while True:
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    pygame.quit()
                                    raise SystemExit
                                elif e.type == pygame.MOUSEMOTION:
                                    mouse_pos = e.pos
                                elif e.type == pygame.KEYDOWN:
                                    if e.key == pygame.K_a:
                                        pl.direction = -3
                                    elif e.key == pygame.K_d:
                                        pl.direction = 3
                                    elif event.key == pygame.K_w:
                                        pl.directiony = -3
                                    elif event.key == pygame.K_s:
                                        pl.directiony = 3
                                    elif e.key == pygame.K_SPACE:
                                        space = True
                                    elif e.key == pygame.K_p:
                                        break
                                elif e.type == pygame.KEYUP:
                                    if pl.direction < 0 and e.key == pygame.K_a:
                                        pl.direction = 0
                                    elif pl.direction > 0 and e.key == pygame.K_d:
                                        pl.direction = 0
                                    elif e.key == pygame.K_SPACE:
                                        space = False
                            else:
                                continue
                            break
                elif event.type == pygame.KEYUP:
                    if pl.direction < 0 and event.key == pygame.K_a:
                        pl.direction = 0
                    elif pl.direction > 0 and event.key == pygame.K_d:
                        pl.direction = 0
                    elif event.key == pygame.K_w:
                        pl.directiony = 0
                    elif event.key == pygame.K_s:
                        pl.directiony = 0

            if boss_cooldown == 0 and boss_level == False:
                boss1 = Boss(bosses, 240, -240, 240, 200, 15, 5)
                boss2 = Boss(bosses, 720, -240, 240, 200, 15, 5)
                boss3 = Boss(bosses, 480, -240, 240, 200, 15, 5)
                boss_level = True
                d = 3
            elif boss_level == True and boss_cooldown == 0:
                boss_cooldown = 3000
            elif d == 0 and boss_level == True:
                boss_level = False
            elif boss_level == False:
                boss_cooldown -= 1

            if enemy_cooldown == 0:
                if random.randint(1,100) < 80:
                    if random.randint(0, 1):
                        chance = random.randint(1,100)
                        if  chance < 85:
                            if random.randint(0, 1):
                                Enemy(enemies, random.randint(0, width - 100),
                                       -120, 300, 240, 25, 1)
                            else:
                                Enemy_2(enemies, random.randint(0, width - 100),
                                       -120, 360)
                        elif chance < 99:
                            if random.randint(0, 1):
                                Enemy(enemies, random.randint(0, width - 100),
                                       -120, 300, 160, 15, 2)
                            else:
                                Enemy_2(enemies, random.randint(0, width - 100),
                                       -120, 360)
                        else:
                            for i in range(10):
                                if random.randint(0, 1):
                                    Enemy(enemies, random.randint(0, width - 100),
                                          -120, 300, 160, 15, 2)
                                else:
                                    Enemy_2(enemies, random.randint(0, width - 100),
                                            -120, 360)
                enemy_cooldown = max(400 - score * 3,50)
                if boss_level == True:
                    enemy_cooldown = 400
            else:
                enemy_cooldown -= 1

            if pl.cooldown != 0 and ray == True:
                pl.cooldown -= 5
                ray_cooldown -= 1
            elif pl.cooldown != 0:
                pl.cooldown -= 1
            if pl.cooldown == 0 and ray == True:
                Projectile(projectiles, pl.rect.x + 12, pl.rect.y + 10,
                           pygame.Color('red'))
                Projectile(projectiles, pl.rect.x + 40, pl.rect.y + 10,
                           pygame.Color('red'))

            if ray == False and ray_cooldown > 0:
                ray_cooldown -= 1

            if ray == True and ray_cooldown == 0:
                ray = False
                ray_cooldown = 1200

            pl.move(pl.xvel + pl.direction, 0)
            pl.move(0, pl.yvel + pl.directiony)

            if pl.rect.x < 0:
                pl.rect.x = 0

            elif pl.rect.x + 60 > width:
                pl.rect.x = width - 60

            if pl.rect.y < 0:
                pl.rect.y = 0

            elif pl.rect.y + 60 > height:
                pl.rect.y = height - 60

            if pl.xvel >= 0.1:
                pl.xvel -= 0.1
            elif pl.xvel <= -0.1:
                pl.xvel += 0.1
            else:
                pl.xvel = 0

            if pl.yvel >= 0.1:
                pl.yvel -= 0.1
            elif pl.yvel <= -0.1:
                pl.yvel += 0.1
            else:
                pl.yvel = 0

            score_label = pygame.font.Font(None, 75).render(str(score), 1, (175, 175, 175))

            fon.draw(screen)
            players.draw(screen)
            ground.draw(screen)
            projectiles.draw(screen)
            projectiles.update()
            projectiles_enemy.draw(screen)
            projectiles_enemy.update()
            enemies.draw(screen)
            enemies.update()
            bosses.draw(screen)
            bosses.update()
            screen.blit(score_label, ((width - score_label.get_rect().width) // 2, 30))
            pygame.display.flip()
            clock.tick(fps)

    finally:
        pygame.quit()


clock = pygame.time.Clock()
start_screen()
start()