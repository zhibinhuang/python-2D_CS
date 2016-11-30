import pygame,math
from Config import *
from pygame.locals import *
#動畫部位
class MySprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #extend the base Sprite class
        self.master_image = None
        self.frame = 0
        self.old_frame = -1
        self.frame_width = 1
        self.frame_height = 1
        self.first_frame = 0
        self.last_frame = 0
        self.columns = 1
        self.last_time = 0
        self.direction = False
        self.master_image = None
    #X property
    def _getx(self): return self.rect.x
    def _setx(self,value): self.rect.x = value
    X = property(_getx,_setx)
    #Y property
    def _gety(self): return self.rect.y
    def _sety(self,value): self.rect.y = value
    Y = property(_gety,_sety)
    #position property
    def _getpos(self): return self.rect.topleft
    def _setpos(self,pos): self.rect.topleft = pos
    position = property(_getpos,_setpos)
    def load(self, filename, width, height, columns):
        self.master_image = pygame.image.load(filename).convert_alpha()
        self.frame_width = width
        self.frame_height = height
        self.rect = Rect(0,0,width,height)
        self.columns = columns
        rect = self.master_image.get_rect()
        self.last_frame = (rect.width // width) * (rect.height // height) - 1
    def update(self):
        if self.master_image != None:
            frame_x = (self.frame % self.columns) * self.frame_width
            frame_y = (self.frame // self.columns) * self.frame_height
            rect = Rect(frame_x, frame_y, self.frame_width, self.frame_height)
            self.image =  pygame.transform.flip(self.master_image.subsurface(rect), self.direction,False) 
class Bullet(MySprite):
    def __init__(self,damage,postion,postion_adj,move):
        MySprite.__init__(self) #extend the base Sprite class
        self.type = "Bullet"
        self.damage = damage
        x_distance = postion_adj[0]-move[0]
        y_distance = postion_adj[1]-move[1]
        distance = math.sqrt(math.pow(x_distance,2) + math.pow(y_distance,2))/10 + 1
        self.speed = (x_distance/distance,y_distance/distance)
        self.image = pygame.Surface((4, 4))
        pygame.draw.circle(self.image, Config.BLUE, (2, 2), 2, 0)
        self.rect = self.image.get_rect()
        self.postion = postion
        self.rect.center = postion
    def update(self):
        self.postion[0] -= self.speed[0]
        self.postion[1] -= self.speed[1]
        self.rect.center = self.postion
class Shield(MySprite):
    def __init__(self):
        MySprite.__init__(self) #extend the base Sprite class
        self.rect = Rect(0,0,4,30)
    def update(self):
        pass
class Camera(object):
    def __init__(self, S_W, S_H, width, height):
        self.rect = Rect(0, 0, width, height)
        self.sw = S_W
        self.sh = S_H
    def apply(self, target):
        return target.rect.move(self.rect.topleft)
    def update(self, target):
        target_rect = target.rect
        l, t, _, _ = target_rect
        _, _, w, h = self.rect
        l, t, _, _ = -l+self.sw/2, -t+self.sh/2, w, h
        l = min(0, l)                           # stop scrolling at the left edge
        l = max(-(self.rect.width-self.sw), l)   # stop scrolling at the right edge
        t = max(-(self.rect.height-self.sh), t) # stop scrolling at the bottom
        t = min(0, t) 
        self.rect = Rect(l, t, w, h)
class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.image.load(Config.BlockImage)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.type = "Block"
    def update(self):
        pass
class Unit(object):
    def __init__(self,x,y,weapon,isPlayer):
        self.move_speed = Config.MOVESPEED[weapon] #移動速度
        self.direction = False #False 面右
        self.isPlayer = isPlayer
        self.magazine = Config.MAGAZINE[weapon] #彈匣量
        self.hp = 100
        self.weapon = weapon
        #火控
        self.lastFire = 0#最後射擊時間
        self.shootRate = Config.SHOOTRATE[weapon]    #射擊間隔(MS)
        self.fire_actioned = True
        self.AutoFire = Config.AutoFire[weapon]
        self.FireBreaked = True
        #換彈
        self.reload_actioned = True
        self.reloadMid = False
        self.reloadTicks = 0
        #防禦
        self.defense_actioning = False
        self.defense_hold = False#維持
        self.defense_actioned = False#動作完成
        #座標
        self.rect = Rect(x, y, 32, 32)#絕對座標
        self.rect_adj = Rect(x, y, 32, 32) #畫面座標
        #部位
        self.Foot = MySprite()
        self.Foot.load("images/Foot.png", 17, 12, 4)
        self.Foot.position = x, y
        self.Foot.direction = self.direction
        self.Body = MySprite()
        self.Body.load("images/Fire.png", 19, 20, 5)
        self.Body.position = x+4, y-20
        self.Body.direction = self.direction
        self.DefenseBody = MySprite()
        self.DefenseBody.load('images/defense.png', 40, 35, 6)
        self.DefenseBody.position = x, y-23
        self.DefenseBody.direction = self.direction
        self.Shield = Shield()
        self.Shield.position = x+25 , y-19
        self.BodyGroup = pygame.sprite.Group()
    def MoveRight(self):
        if not self.defense_actioning:
            self.rect.x += self.move_speed
            #腳
            if self.direction:
                self.Foot.frame -= 1
            else:
                self.Foot.frame += 1
            if self.Foot.frame > self.Foot.last_frame:
                self.Foot.frame = self.Foot.first_frame
            elif self.Foot.frame < self.Foot.first_frame:
                self.Foot.frame = self.Foot.last_frame
    def MoveLeft(self):
        if not self.defense_actioning:
            self.rect.x -= self.move_speed
            #腳
            if self.direction:
                self.Foot.frame -= 1
            else:
                self.Foot.frame += 1
            self.Foot.X -= self.move_speed
            if self.Foot.frame > self.Foot.last_frame:
                self.Foot.frame = self.Foot.first_frame
            elif self.Foot.frame < self.Foot.first_frame:
                self.Foot.frame = self.Foot.last_frame
    def SeekCheck(self,x):
        if x < self.rect_adj.x + 20:#左
            self.direction = True
        else:#右
            self.direction = False
    def getShootPosition(self):
        if not self.direction:
            return [self.rect.x + 20,self.rect.y-7]
        else:
            return [self.rect.x,self.rect.y-7]
    def FireBreak(self):
        self.FireBreaked = True
    def Fire(self,TargetPosition):
        ticks = pygame.time.get_ticks()
        if self.magazine > 0 and ticks > self.lastFire + self.shootRate and self.FireBreaked and self.reload_actioned and not self.defense_actioning:
            self.magazine -= 1
            self.fire_actioned = False
            pygame.mixer.Sound(Config.PATH+'/musices/'+Config.SOUND[self.weapon]).play()
            self.lastFire = ticks
            postion = self.Body.position
            self.Body.load("images/Fire.png", 19, 20, 5)
            self.Body.position = postion
            if not self.AutoFire:
                self.FireBreaked = False
            return Bullet(Config.DAMAGE[self.weapon],self.getShootPosition(),self.rect_adj,TargetPosition)
        return False
    def fireUpdate(self):        
        self.Body.frame += 1
        if self.Body.frame > self.Body.last_frame:
            self.Body.frame = self.Body.first_frame
            self.fire_actioned = True
    def Reload(self):
        if self.reload_actioned and self.fire_actioned and not self.defense_actioning:
            self.reload_actioned = False
            self.reloadMid = False
            postion = self.Body.position
            self.Body.load("images/Reload.png", 19, 20, 5)
            self.Body.position = postion
            pygame.mixer.Sound(Config.PATH+'/musices/Reload.wav').play()
    def reloadUpdate(self):
        if not self.reloadMid:
            self.Body.frame += 1
        else:
            self.Body.frame -= 1
        if self.Body.frame > self.Body.last_frame:
            if not self.reloadMid:
                self.reloadMid = True
                self.Body.frame -= 1
        if self.Body.frame < self.Body.first_frame:
            pygame.mixer.Sound(Config.PATH+'/musices/Reload.wav').play()
            self.magazine = Config.MAGAZINE[self.weapon] #彈匣量
            self.reload_actioned = True
            self.Body.frame = self.Body.last_frame
    def defenseUpdaet(self):
        if self.defense_actioning:#維持
            self.defense_hold = True
            if self.DefenseBody.frame < self.DefenseBody.last_frame:#尚未舉滿
                self.DefenseBody.frame += 1
        else:
            if self.DefenseBody.frame > self.DefenseBody.first_frame:
                self.DefenseBody.frame -= 1
            else:
                self.defense_hold = False
    def update(self,camera,Bullets):
        self.Foot.direction = self.direction
        self.Body.direction = self.direction
        self.DefenseBody.direction = self.direction
        self.collision(Bullets)
        self.rect_adj = camera.apply(self)
        if self.hp >= 0:
            #腳
            self.Foot.first_frame = self.weapon * self.Foot.columns
            self.Foot.last_frame = self.Foot.first_frame + self.Foot.columns - 1
            if self.Foot.frame > self.Foot.last_frame:
                self.Foot.frame = self.Foot.first_frame
            elif self.Foot.frame < self.Foot.first_frame:
                self.Foot.frame = self.Foot.last_frame
            if self.direction:
                self.Foot.X = self.rect.x + 6
            else:
                self.Foot.X = self.rect.x - 4
            #身
            if self.defense_actioning or self.defense_hold:
                self.DefenseBody.first_frame = self.Foot.frame * self.DefenseBody.columns
                self.DefenseBody.last_frame = self.DefenseBody.first_frame + self.DefenseBody.columns - 1
                if self.DefenseBody.frame > self.DefenseBody.last_frame:
                    self.DefenseBody.frame = self.DefenseBody.first_frame
                elif self.DefenseBody.frame < self.DefenseBody.first_frame:
                    self.DefenseBody.frame = self.DefenseBody.last_frame
                self.DefenseBody.X = self.rect.x - 6
                if self.direction:
                    self.Shield.X = self.rect.x - 4
                else:
                    self.Shield.X = self.rect.x + 19
                self.defenseUpdaet()
            else:
                self.Body.first_frame = self.weapon * self.Body.columns
                self.Body.last_frame = self.Body.first_frame + self.Body.columns - 1
                if self.Body.frame > self.Body.last_frame:
                    self.Body.frame = self.Body.first_frame
                elif self.Body.frame < self.Body.first_frame:
                    self.Body.frame = self.Body.last_frame
                if not self.reload_actioned:
                    self.reloadUpdate()
                elif not self.fire_actioned:
                    self.fireUpdate()
                self.Body.X = self.rect.x
    def draw(self,screen,camera):
        if not self.defense_actioning and not self.defense_hold:
            self.Foot.update()
            self.Body.update()
            screen.blit(self.Foot.image, camera.apply(self.Foot))
            screen.blit(self.Body.image, camera.apply(self.Body))
        else:
            self.DefenseBody.update()
            screen.blit(self.DefenseBody.image, camera.apply(self.DefenseBody))
        if self.hp > 0:
            #血框
            pygame.draw.rect(screen, Config.WHITE, (int(camera.apply(self).x - 8), int(camera.apply(self).y - 29),40,5),1)
            #血條
            pygame.draw.rect(screen, Config.RED, (int(camera.apply(self).x - 7), int(camera.apply(self).y - 28),int(38*(self.hp/100)),3),0)
    def collision(self,target):
        if self.defense_actioning or self.defense_hold:
            attacker = None
            attacker = pygame.sprite.spritecollideany(self.Shield, target)
            if attacker != None:
                if attacker.type == "Bullet":
                    print("hit")
                    #self.hp -= attacker.damage
                    target.remove(attacker)
        attacker = None
        attacker = pygame.sprite.spritecollideany(self.Foot, target)
        if attacker != None:
            #if pygame.sprite.collide_circle_ratio(0.65)(self.Foot,attacker):
            if attacker.type == "Bullet":
                self.hp -= attacker.damage
                target.remove(attacker)
        attacker = None
        attacker = pygame.sprite.spritecollideany(self.Body, target)
        if attacker != None:
            #if pygame.sprite.collide_circle_ratio(0.65)(self.Body,attacker):
            if attacker.type == "Bullet":
                self.hp -= attacker.damage
                target.remove(attacker)
