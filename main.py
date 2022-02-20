import pygame as pg
from settings import *
from sprites import *
from os import path


class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.score = 0
        self.num_of_zombies = 2
        self.num_of_mummies = 1

        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font("alias")
        self.tut_screen_on = False
        self.last_created_defence = 0
        self.sec = random.choice([1000, 2000, 3000, 4000, 5000])
        self.load_data()
        # self.save_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        self.snd_dir = path.join(self.dir, "snd")
        img_dir = path.join(self.dir, "img")
        main_hero_dir = path.join(img_dir, "main_hero")
        self.main_hero_spritesheet_img = pg.image.load(path.join(main_hero_dir, "blordrough_corporal-NESW.png"))
        self.main_hero_spritesheet = Spritesheet(path.join(main_hero_dir, "blordrough_corporal-NESW.png"))
        zombies_dir = path.join(img_dir, "zombies")
        self.zombies_spritesheet_img = pg.image.load(path.join(zombies_dir, "bloody_zombie-NESW.png"))
        self.zombies_spritesheet = Spritesheet(path.join(zombies_dir, "bloody_zombie-NESW.png"))
        guns_dir = path.join(img_dir, "guns")
        mummies_dir = path.join(img_dir, "mummies")
        self.mummie_spritesheet_img = pg.image.load(path.join(mummies_dir, "mummy-02.png"))
        self.mummie_spritesheet = Spritesheet(path.join(mummies_dir, "mummy-02.png"))
        self.guns_spritesheet_img = pg.image.load(path.join(guns_dir, "pack.png"))
        self.guns_spritesheet = Spritesheet(path.join(guns_dir, "pack.png"))
        self.bullet_img = pg.image.load(path.join(guns_dir, "bullet1.png")).convert()
        self.sword_img = pg.image.load(path.join(guns_dir, "sword_normal.png")).convert()
        self.background = pg.image.load(path.join(img_dir, "bg.png")).convert()
        self.background = pg.transform.scale(self.background, (
        int(self.background.get_width() * 1.9), int(self.background.get_height() * 1.1)))
        self.background_rect = self.background.get_rect()
        powerups_dir = path.join(img_dir, "powerups")
        self.health_img = pg.image.load(path.join(powerups_dir, "health.png")).convert()
        self.health_img.set_colorkey(BLACK)
        health_img_width = self.health_img.get_width()
        health_img_height = self.health_img.get_height()
        self.health_img = pg.transform.scale(self.health_img,
                                             (int(health_img_width * 0.3), int(health_img_height * 0.3)))
        self.defence_img = pg.image.load(path.join(powerups_dir, "defence.png")).convert()
        self.defence_img.set_colorkey(WHITE)
        defence_img_width = self.defence_img.get_width()
        defence_img_height = self.defence_img.get_height()
        self.defence_img = pg.transform.scale(self.defence_img,
                                              (int(defence_img_width * 0.7), int(defence_img_height * 0.7)))

        self.shoot_sound = pg.mixer.Sound(path.join(self.snd_dir, "shoot.wav"))
        self.powerup_sound = pg.mixer.Sound(path.join(self.snd_dir, "powerup.wav"))
        self.sword_hit_nothing_sound = pg.mixer.Sound(path.join(self.snd_dir, "sword.wav"))
        self.sword_sound = pg.mixer.Sound(path.join(self.snd_dir, "sword_hit_mob.mp3"))

    def newmob(self):
        self.mob = Zombie(self)
        self.all_sprites.add(self.mob)
        self.mobs.add(self.mob)
        self.zombies.add(self.mob)

    def new_health_booster(self):
        x = random.randrange(0, WIDTH)
        y = 5
        self.health = Health(self, x, y)
        self.powerups.add(self.health)
        self.health_powerup.add(self.health)
        self.all_sprites.add(self.health)

    def new_defense_booster(self):
        now = pg.time.get_ticks()
        if now - self.last_created_defence > 10000 + self.sec and len(self.defence_powerup) == 0:
            self.sec = random.choice([1000, 2000, 3000, 4000, 5000])
            self.last_created_defence = now
            x = random.randrange(0, WIDTH)
            y = 5
            self.defence = Defence(self, x, y)
            self.powerups.add(self.defence)
            self.defence_powerup.add(self.defence)
            self.all_sprites.add(self.defence)

    def newmummie(self):
        self.mummie = Mummie(self)
        self.all_sprites.add(self.mummie)
        self.mobs.add(self.mummie)
        self.mummies.add(self.mummie)

    def new(self):
        self.bgmusic = pg.mixer.music.load(path.join(self.snd_dir, "main.wav"))
        self.all_sprites = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.zombies = pg.sprite.Group()
        self.mummies = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.health_powerup = pg.sprite.Group()
        self.defence_powerup = pg.sprite.Group()
        self.player = Player(self)
        self.gun = Gun(self)
        # self.sword = Sword(self)
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.gun)
        self.run()

    def run(self):
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    def health_bar(self, surf, length, height, x, y, pct):
        if pct < 0:
            pct = 0
        BAR_LENGTH = length
        BAR_HEIGHT = height
        fill = (pct / 100) * BAR_LENGTH
        outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
        if pct > 40:
            pg.draw.rect(surf, GREEN, fill_rect)
        else:
            pg.draw.rect(surf, RED, fill_rect)

        pg.draw.rect(surf, WHITE, outline_rect, 2)

    def update(self):
        self.new_defense_booster()
        # if self.score >= 200:
        self.num_of_mummies = self.score // 300 + 1
        self.num_of_zombies = self.score // 300 + 2
        if self.num_of_zombies >= 5:
            self.num_of_zombies = 4
        if self.num_of_mummies >= 4:
            self.num_of_mummies = 3
        if self.player.health < 50:
            if random.randrange(0, 100) == 80 and len(self.powerups) == 0:
                self.new_health_booster()

        if len(self.zombies) < self.num_of_zombies:
            self.newmob()
        if len(self.mummies) < self.num_of_mummies:
            self.newmummie()
        if self.player.weapons[0] == "gun":
            if self.player.has_sword:
                self.sword.kill()
                self.player.has_sword = False
            if not self.player.has_gun:
                self.gun = Gun(self)
                self.gun.dir = self.player.dir
                if self.gun.dir == -1:
                    self.gun.image = pg.transform.flip(self.gun.image, True, False)
                    self.gun.rect.midleft = (self.player.rect.midleft[0], self.player.rect.midleft[1])
                self.all_sprites.add(self.gun)
            self.player.has_gun = True

        elif self.player.weapons[0] == "sword":
            if self.player.has_gun:
                self.gun.kill()
                self.player.has_gun = False
            if not self.player.has_sword:
                self.sword = Sword(self)
                self.sword.dir = self.player.dir
                if self.sword.dir == -1:
                    self.sword.image = pg.transform.flip(self.sword.image, True, False)
                    self.sword.rect.midleft = self.player.rect.midleft
                self.all_sprites.add(self.sword)
            self.player.has_sword = True

        self.all_sprites.update()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    self.player.weapons[0], self.player.weapons[1] = self.player.weapons[1], self.player.weapons[0]

    def draw(self):
        self.screen.fill(BLACK)

        self.screen.blit(self.background, self.background_rect)
        self.all_sprites.draw(self.screen)
        self.health_bar(self.screen, 150, 20, 5, 5, self.player.health, )
        for mob in self.mobs:
            if mob.health < 100:
                self.health_bar(self.screen, 40, 10, mob.rect.x, mob.rect.y, mob.health)
        self.draw_text(str(self.score), 60, RED, WIDTH / 2, 5)
        pg.display.flip()

    def show_start_screen(self):
        self.tut_screen_on = False
        self.screen.fill(BLACK)
        self.screen.blit(self.background, self.background_rect)
        self.draw_text(TITLE, 96, RED, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Press any key to start", 44, RED, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press t for tutorial", 30, RED, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        if not self.running:
            return

        self.tut_screen_on = False
        self.screen.fill(BLACK)
        self.screen.blit(self.background, self.background_rect)
        self.draw_text("GAME OVER", 96, RED, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Press any key to restart", 44, RED, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press t for tutorial", 30, RED, WIDTH / 2, HEIGHT * 3 / 4)
        pg.display.flip()
        self.wait_for_key()

    def show_tutorial_screen(self):
        # if not self.running:
        #     return
        self.screen.fill(BLACK)
        self.screen.blit(self.background, self.background_rect)
        # self.draw_text("TUTORIAL", 96, RED, WIDTH/2, HEIGHT/6)
        self.draw_text("Press A D to move, W to jump", 50, RED, WIDTH / 2, HEIGHT / 8 - 20)
        self.draw_text("Press R to change weapon", 50, RED, WIDTH / 2, HEIGHT / 6 + 20)
        self.draw_text("Press SPACE to shoot/attack", 50, RED, WIDTH / 2, HEIGHT / 4 + 40)
        self.draw_text("Press B to go back", 35, RED, WIDTH / 2, HEIGHT - 80)

        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    self.tut_screen_on = False
                elif event.type == pg.KEYUP:
                    if event.key == pg.K_t:
                        self.tut_screen_on = True
                        self.show_tutorial_screen()
                        waiting = False
                    elif event.key == pg.K_b:
                        if self.tut_screen_on:
                            self.show_start_screen()
                            waiting = False

                        else:
                            waiting = False
                            self.tut_screen_on = False


                    else:
                        waiting = False
                        self.tut_screen_on = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()
pg.quit()
