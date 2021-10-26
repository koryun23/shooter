from settings import *
import pygame as pg
import random
import time
from os import path
vec = pg.math.Vector2
class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()
    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0,0),(x,y,width,height))
        image = pg.transform.scale(image, (int(width*1.5), int(height*1.5)))
        image.set_colorkey(BLACK)
        return image
class Defence(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.x=  x
        self.y = y
        self.image = self.game.defence_img
        self.rect = self.image.get_rect()
        self.pos = vec(self.x, self.y)
        self.rect.x = self.x
        self.rect.y = self.y
        self.vel = vec(0,10)
    def update(self):
        if self.pos.y > HEIGHT-40:
            self.pos.y = HEIGHT-30
            self.vel.y = 0
        else:
            self.pos.y += self.vel.y
        self.rect.center = self.pos
class Health(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.x = x
        self.y = y
        self.image = self.game.health_img
        self.rect = self.image.get_rect()
        self.vel = vec(0,10)
        self.pos = vec(self.x, self.y)
        self.rect.x = self.x
        self.rect.y = self.y
        self.images = [self.image]
        self.current_frame = 0
        self.last_update = 0
        self.get_images()
    def get_images(self):

        for i in range(2, 10):
            img_width = int(self.image.get_width()*i/10)
            img_height = int(self.image.get_height()*i/10)
            img = pg.transform.scale(self.image, (img_width, img_height))
            self.images.append(img)
    def update(self):
        if self.pos.y > HEIGHT-40:
            self.pos.y = HEIGHT-30
            self.vel.y = 0
            self.bounce()
        else:
            self.pos.y+=self.vel.y
        self.rect.center = self.pos
    def bounce(self):
        now = pg.time.get_ticks()
        if now-self.last_update>200:
            self.last_update =now
            self.image= self.images[self.current_frame]
            self.current_frame = (self.current_frame+1)%len(self.images)

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.dir = 1
        spritesheet_width = self.game.main_hero_spritesheet_img.get_width()
        spritesheet_height = self.game.main_hero_spritesheet_img.get_height()
        self.walk_r = [
            self.game.main_hero_spritesheet.get_image(x*spritesheet_width*0.33,0+spritesheet_height*0.25,spritesheet_width*0.33, spritesheet_height*0.25)
            for x in range(3)
        ] 
        self.walk_l = [
            self.game.main_hero_spritesheet.get_image(x*spritesheet_width*0.33,0+spritesheet_height*0.75,spritesheet_width*0.33, spritesheet_height*0.25)
            for x in range(3)
        ]
        self.images = self.walk_r+self.walk_l
        if self.dir ==1:
            self.standing_frame = self.walk_r[0]
        else:
            self.standing_frame = self.walk_l[0]
        self.image = self.standing_frame
        self.current_frame = 0
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT-40)
        self.vel = vec(0,0)
        self.pos = vec(WIDTH/2, HEIGHT-40)
        self.health = 100
        self.jumping = False
        self.walking = False
        self.last_jumped = 0
        self.last_updated = 0
        self.weapons = ["gun", "sword"]
        self.has_gun = True
        self.has_sword = False
        self.has_defence = False
        self.defence_timer = 0
    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        if self.vel.y > 0:
            self.jumping =True
        else:
            self.jumping = False
        if self.walking:
            if now - self.last_updated > 200:
                self.last_updated = now
                self.current_frame = (self.current_frame+1)%len(self.walk_r)
                if self.vel.x > 0:
                    self.image = self.walk_r[self.current_frame]
                elif self.vel.x < 0:
                    self.image = self.walk_l[self.current_frame]
                bottom = self.rect.bottom
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        else:
            if self.dir == 1:
                self.image = self.walk_r[0]
            else:
                self.image = self.walk_l[0]
            bottom = self.rect.bottom
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
    def update(self):
        self.animate()
        if self.has_defence and pg.time.get_ticks()-self.defence_timer > 6000:
            self.has_defence=False
            for i in range(len(self.images)):
                self.images[i].set_alpha(255)
        elif self.has_defence and pg.time.get_ticks()-self.defence_timer < 6000:

            for i in range(len(self.images)):
                self.images[i].set_alpha(128)
        pg.display.flip()
        self.acc = vec(0,PLAYER_GRAV)
        keys = pg.key.get_pressed()
        self.vel.x = 0
        if keys[pg.K_a]:
            self.vel.x = -5
            self.dir = -1

        if keys[pg.K_d]:
            self.vel.x = 5
            self.dir = 1
        if keys[pg.K_w]:
            now = pg.time.get_ticks()
            if now - self.last_jumped > 800:
                self.last_jumped = now
                self.vel.y =-PLAYER_JUMP

        self.vel += self.acc 
        self.pos += self.vel + 0.5*self.acc
        if self.pos.x > WIDTH:
            self.pos.x = WIDTH
        elif self.pos.x < 0:
            self.pos.x = 0
        if self.pos.y > HEIGHT-40:
            self.pos.y=HEIGHT-40
        self.rect.center = self.pos
        self.mask = pg.mask.from_surface(self.image)
class Mummie(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((60,80))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.pos = vec(random.randrange(0, WIDTH), -10)
        self.vel = vec(0,10)
        self.health = 100
        spritesheet_width = self.game.mummie_spritesheet_img.get_width()
        spritesheet_height = self.game.mummie_spritesheet_img.get_height()
        self.walk_r = [
            self.game.mummie_spritesheet.get_image(x*spritesheet_width*0.33,0+spritesheet_height*0.25,spritesheet_width*0.33, spritesheet_height*0.25)
            for x in range(3)
        ]
        self.walk_l = [
            self.game.mummie_spritesheet.get_image(x*spritesheet_width*0.33,0+spritesheet_height*0.75,spritesheet_width*0.33, spritesheet_height*0.25)
            for x in range(3)
        ]
        self.current_image = self.walk_r[0]
        self.walking = False
        self.jumping = False
        self.last_updated = 0
        self.current_frame = 0
        self.dir=1
    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        if self.vel.y > 0:
            self.jumping =True
        else:
            self.jumping = False
        if self.walking:
            if now - self.last_updated > 200:
                self.last_updated = now
                self.current_frame = (self.current_frame+1)%len(self.walk_r)
                if self.vel.x > 0:
                    self.image = self.walk_r[self.current_frame]
                elif self.vel.x < 0:
                    self.image = self.walk_l[self.current_frame]
                bottom = self.rect.bottom
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        else:
            if self.dir == 1:
                self.image = self.walk_r[0]
            else:
                self.image = self.walk_l[0]
            bottom = self.rect.bottom
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
    def update(self):
        self.animate()
        if self.pos.y > HEIGHT-40:
            self.pos.y -=5
            self.vel.y=0
        self.mask = pg.mask.from_surface(self.image)
        self.pos.y+=self.vel.y


        #move in x direction if the mob did not collide with player        
        if not self.rect.colliderect(self.game.player.rect) or (self.rect.x+5+self.game.player.rect.width >= self.game.player.rect.x or self.rect.x-5<=self.game.player.rect.x+self.game.player.rect.width):
        #if not pg.sprite.spritecollide(self,self.game.player, False, pg.sprite.collide_mask):
            self.pos.x+=self.vel.x


        if self.vel.y == 0:
            if self.pos.x > self.game.player.pos.x:
                self.vel.x = -1.2
            else:
                self.vel.x=1.2
        
        self.rect.center = self.pos
        #Check if a mob collided with player
        hits = pg.sprite.spritecollide(self.game.player, self.game.mobs, False, pg.sprite.collide_mask)
        for hit in hits:
            if not self.game.player.has_defence:
                self.game.player.health-=10

                if self.game.player.health <=0:
                    self.game.score = 0
                    self.game.playing = False

            if hit.vel.x > 0:
                self.game.player.pos.x += 5
                self.game.gun.rect.x +=5
            elif hit.vel.x < 0:
                self.game.player.pos.x -=5
                self.game.gun.rect.x -=5

class Zombie(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((60,80))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.pos = vec(random.randrange(0, WIDTH), -10)
        self.vel = vec(0,10)
        self.health = 100
        spritesheet_width = self.game.zombies_spritesheet_img.get_width()
        spritesheet_height = self.game.zombies_spritesheet_img.get_height()
        self.walk_r = [
            self.game.zombies_spritesheet.get_image(x*spritesheet_width*0.33,0+spritesheet_height*0.25,spritesheet_width*0.33, spritesheet_height*0.25)
            for x in range(3)
        ]
        self.walk_l = [
            self.game.zombies_spritesheet.get_image(x*spritesheet_width*0.33,0+spritesheet_height*0.75,spritesheet_width*0.33, spritesheet_height*0.25)
            for x in range(3)
        ]
        self.current_image = self.walk_r[0]
        self.walking = False
        self.jumping = False
        self.last_updated = 0
        self.current_frame = 0
        self.dir=1
    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        if self.vel.y > 0:
            self.jumping =True
        else:
            self.jumping = False
        if self.walking:
            if now - self.last_updated > 200:
                self.last_updated = now
                self.current_frame = (self.current_frame+1)%len(self.walk_r)
                if self.vel.x > 0:
                    self.image = self.walk_r[self.current_frame]
                elif self.vel.x < 0:
                    self.image = self.walk_l[self.current_frame]
                bottom = self.rect.bottom
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        else:
            if self.dir == 1:
                self.image = self.walk_r[0]
            else:
                self.image = self.walk_l[0]
            bottom = self.rect.bottom
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
    def update(self):
        self.animate()
        if self.pos.y > HEIGHT-40:
            self.pos.y -=5
            self.vel.y=0
        self.mask = pg.mask.from_surface(self.image)
        self.pos.y+=self.vel.y

        #move in x direction if the mob did not collide with player        
        if not self.rect.colliderect(self.game.player.rect) or (self.rect.x+5+self.game.player.rect.width >= self.game.player.rect.x or self.rect.x-5<=self.game.player.rect.x+self.game.player.rect.width):
        #if not pg.sprite.spritecollide(self,self.game.player, False, pg.sprite.collide_mask):
            self.pos.x+=self.vel.x


        if self.vel.y == 0:
            if self.pos.x > self.game.player.pos.x:
                self.vel.x = -1
            else:
                self.vel.x=1
        
        self.rect.center = self.pos
        #Check if a mob collided with player
        hits = pg.sprite.spritecollide(self.game.player, self.game.mobs, False, pg.sprite.collide_mask)
        for hit in hits:
            if not self.game.player.has_defence:

                self.game.player.health-=5

                if self.game.player.health <=0:
                    self.game.score = 0
                    self.game.playing = False

            if hit.vel.x > 0:
                self.game.player.pos.x += 5
                self.game.gun.rect.x +=5
            else:
                self.game.player.pos.x -=5
                self.game.gun.rect.x -=5

class Gun(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)

        self.game = game
        spritesheet_width = self.game.guns_spritesheet_img.get_width()
        spritesheet_height = self.game.guns_spritesheet_img.get_height()
        self.dir = 1
        self.first_image = self.game.guns_spritesheet.get_image(spritesheet_width*3/4, spritesheet_height*2/7, spritesheet_width/4, spritesheet_height/7)
        self.image = self.first_image
        self.image = pg.transform.scale(self.image, (self.image.get_width()*2, self.image.get_height()*2))
        self.first_image = self.image
        self.rect = self.image.get_rect()
        self.center = self.game.player.rect.midright
        self.rect.midright = self.center
        self.last_shot = pg.time.get_ticks()
        self.vel = vec(0,0)
        self.pos = vec(self.center[0], self.center[1])

        self.last_updated = 0
        self.rot = 0
        self.rot_speed =2
    def update(self):
        self.pos = self.game.player.pos
        self.acc = vec(0,PLAYER_GRAV)
        keys = pg.key.get_pressed()

        if keys[pg.K_a]:

            if self.dir == 1:
                self.image = pg.transform.flip(self.image, True, False)
                rect = self.image.get_rect()
                rect.midleft = (self.game.player.rect.center[0], self.game.player.rect.center[1]+30)
                self.rect = rect
                self.dir = -1
            else:
                self.rect.midleft = self.game.player.rect.midleft
        if keys[pg.K_d]:

            if self.dir == -1:
                self.image = pg.transform.flip(self.image, True, False)
                rect = self.image.get_rect()
                rect.midleft = (self.game.player.rect.center[0],self.game.player.rect.center[1]-30)
                self.rect = rect
                self.dir = 1
            else:
                self.rect.midright = self.game.player.rect.midright
        if keys[pg.K_w]:
            self.vel.y =-PLAYER_JUMP
        elif keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if now - self.last_shot > 200:
                self.shoot()
        self.vel += self.acc 
        self.pos += self.vel + 0.5*self.acc

        if self.pos.y > HEIGHT-40:
            self.pos.y=HEIGHT-40
        self.rect.y = self.pos[1]

    def shoot(self):
        self.game.shoot_sound.play()
        self.rect.x -= self.dir
        self.game.player.pos.x -= self.dir
        self.rotate_gun()
        self.newbullet()
        self.last_shot = pg.time.get_ticks()
        
    def rotate_gun(self):
        pass


    def newbullet(self):
        bullet = Bullet(self.game)
        self.game.bullets.add(bullet)
        self.game.all_sprites.add(bullet)

class Bullet(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = self.game.bullet_img
        self.image = pg.transform.scale(self.image, (self.image.get_width()//30, self.image.get_height()//30))
        if self.game.player.dir == -1:
            self.image = pg.transform.flip(self.image, True, False)
        # self.image.fill(BLUE)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.last_update = 0
        if self.game.gun.rect.midright >= self.game.player.rect.midright:
            self.center = self.game.gun.rect.midleft
            self.center = (self.center[0], self.center[1]-10)
            self.dir = 1
        else:
            self.center = self.game.gun.rect.midright
            self.center = (self.center[0], self.center[1]-10)
            self.dir = -1
        self.dir = self.game.gun.dir
        self.vel = self.dir * 10
        self.rect.center = self.center
    def update(self):   
        self.rect.x += self.vel
        if self.rect.x > WIDTH or self.rect.x < 0:
            self.kill()
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.dir = -1
        elif keys[pg.K_d]:
            self.dir = 1

        #Check if a bullet collided with a mob
        hits = pg.sprite.spritecollide(self, self.game.mobs, False)
        for hit in hits:

            self.kill()
            hit.health -= 20
            if hit.health <= 0:
                if self.game.zombies.has(hit):
                    self.game.score += 20
                elif self.game.mummies.has(hit):
                    self.game.score += 30
                hit.kill()
        #Check if a bullet collided with a health powerup
        hits = pg.sprite.spritecollide(self, self.game.health_powerup, True)
        for hit in hits:
            self.game.powerup_sound.play()
            self.kill()
            self.game.player.health+=20
        
        #Check if a bullet collided with a defence powerup
        hits = pg.sprite.spritecollide(self, self.game.defence_powerup, True)
        for hit in hits:
            self.game.powerup_sound.play()
            self.kill()
            self.game.player.has_defence = True
            self.game.player.defence_timer = pg.time.get_ticks()

class Sword(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.dir = self.game.player.dir

        self.orig_image = game.sword_img
        self.orig_image = pg.transform.rotate(self.orig_image, 5)
        self.orig_image.set_colorkey(BLACK)
        #self.orig_image = pg.transform.rotate(self.orig_image, 10)
        self.orig_rect = self.orig_image.get_rect()

        self.image = self.orig_image.copy()
        self.image.set_colorkey(BLACK)
        self.image = pg.transform.scale(self.image, (int(self.image.get_width()*1.2), int(self.image.get_height()*1.2)))
        self.rect = self.image.get_rect()
        self.rect.midright = self.game.player.rect.midright
        self.vel = vec(0,0)
        self.last_update = 0
        img_dir =path.join(self.game.dir, "img")
        guns_dir = path.join(img_dir, "guns")
        self.images = [pg.image.load(path.join(guns_dir, f"sword_normal{i+1}.png")).convert() for i in range(45)]
        for i in range(len(self.images)):
            self.images[i].set_colorkey(BLACK)
            self.images[i] = pg.transform.scale(self.images[i], (int(self.images[i].get_width()*1.2), int(self.images[i].get_height()*1.2)))
        
        
        self.current_frame =0
        self.last_pressed_key = None
        self.attacked = False

    def update(self):
        self.pos = self.game.player.pos
        self.acc = vec(0,PLAYER_GRAV)
        keys = pg.key.get_pressed()

        if self.last_pressed_key=="SPACE" and self.game.player.weapons[0]=="sword":

            self.attack()
            if self.current_frame == len(self.images)-1:
                self.current_frame = 0
                if self.dir == 1:
                    self.image =self.images[self.current_frame]
                elif self.dir == -1:
                    self.image = pg.transform.flip(self.images[self.current_frame], True, False)
                self.attacked=True

        if keys[pg.K_a]:
            self.last_pressed_key = None
            if self.dir == 1:
                self.image = pg.transform.flip(self.images[0], True, False)
                # self.image = self.images[0]
                rect = self.image.get_rect()
                rect.midleft = (self.game.player.rect.midleft[0], self.game.player.rect.midleft[1])
                self.rect = rect
                self.dir = -1
            else:
                self.rect.midleft = self.game.player.rect.midleft
            
        if keys[pg.K_d]:
            self.last_pressed_key = None
            if self.dir == -1:
                self.image = self.images[0] 
                rect = self.image.get_rect()
                rect.midright = (self.game.player.rect.midright[0],self.game.player.rect.midright[1])

                self.rect = rect
                self.dir = 1
            else:
                self.rect.midright = self.game.player.rect.midright
            
        if keys[pg.K_w]:
            self.vel.y =-PLAYER_JUMP
            self.last_pressed_key = None
        if keys[pg.K_SPACE]:
            self.attacked = False
            self.last_pressed_key = "SPACE"

            self.attack()

        self.vel += self.acc 
        self.pos += self.vel + 0.5*self.acc

        if self.pos.y > HEIGHT-40:
            self.pos.y=HEIGHT-40
        self.rect.y = self.pos[1]-15
        self.mask = pg.mask.from_surface(self.image)
    def attack(self):

        if not self.attacked:
            # 
            if self.dir == -1:
                self.image = pg.transform.flip(self.images[self.current_frame], True, False)
            elif self.dir == 1:
                self.image = self.images[self.current_frame]
            self.current_frame = (self.current_frame+2)%(len(self.images))
            #check if the sword collided with a mob
            self.mask = pg.mask.from_surface(self.image)
            hits = pg.sprite.spritecollide(self, self.game.mobs, False, pg.sprite.collide_mask)
            # if not hits:
            #     self.game.sword_hit_nothing_sound.play()
            for hit in hits:
                self.game.sword_sound.play()
                hit.health -= 20

                if hit.health<= 0:
                    if self.game.zombies.has(hit):
                        self.game.score+= 20
                    elif self.game.mummies.has(hit):
                        self.game.score+=30
                    hit.kill()
                if self.dir == -1:
                    self.image = pg.transform.flip(self.images[0], True, False)
                    hit.pos.x += self.dir*20
                else:
                    self.iamge = self.images[0]
                    hit.pos.x += self.dir*20
            if len(hits) == 0:
                self.game.sword_hit_nothing_sound.play()
            # check if the sword collided with a health booster powerup
            hits =pg.sprite.spritecollide(self, self.game.health_powerup, True)
            for hit in hits:
                self.game.powerup_sound.play()
                self.game.player.health+=20
            
            #check if the sword collided with a defence powerup
            hits = pg.sprite.spritecollide(self, self.game.defence_powerup, True)
            for hit in hits:
                self.game.powerup_sound.play()
                self.game.player.has_defence = True
                self.game.player.defence_timer = pg.time.get_ticks()