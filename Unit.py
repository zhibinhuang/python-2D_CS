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
    def update(self, current_time):
        if self.master_image != None:
            frame_x = (self.frame % self.columns) * self.frame_width
            frame_y = (self.frame // self.columns) * self.frame_height
            rect = Rect(frame_x, frame_y, self.frame_width, self.frame_height)
            self.image =  pygame.transform.flip(self.master_image.subsurface(rect), self.direction,False) 
class Bullet(MySprite):
    def __init__(self,damage,postion,move):
        MySprite.__init__(self) #extend the base Sprite class
        self.type = "Bullet"
        self.damage = damage
        x_distance = postion[0]-move[0]
        y_distance = postion[1]-move[1]
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
        #self.rect = Rect(0,0,4,30)
        self.image = pygame.Surface((4, 30))
        pygame.draw.rect(self.image, Config.BLUE, (0, 0,4,30),0)
        self.rect = self.image.get_rect()
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
        #真實座標
        self.postion = [x,y]
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
            self.postion[0] += self.move_speed
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
            self.postion[0] -= self.move_speed
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
        if x < self.Foot.X + 20:#左
            self.direction = True
        else:#右
            self.direction = False
    def getShootPosition(self):
        if not self.direction:
            return [self.Body.X + 41,self.Body.Y + 12]
        else:
            return [self.Body.X,self.Body.Y + 12]
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
            return Bullet(Config.DAMAGE[self.weapon],self.getShootPosition(),TargetPosition)
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
    def update(self,screen_rect):
        self.Foot.direction = self.direction
        self.Body.direction = self.direction
        self.DefenseBody.direction = self.direction
        if self.hp >= 0:
            #腳
            self.Foot.first_frame = self.weapon * self.Foot.columns
            self.Foot.last_frame = self.Foot.first_frame + self.Foot.columns - 1
            if self.Foot.frame > self.Foot.last_frame:
                self.Foot.frame = self.Foot.first_frame
            elif self.Foot.frame < self.Foot.first_frame:
                self.Foot.frame = self.Foot.last_frame
            if self.direction:
                self.Foot.X = self.postion[0] + 6
            else:
                self.Foot.X = self.postion[0] - 4
            #身
            if self.defense_actioning or self.defense_hold:
                self.DefenseBody.first_frame = self.Foot.frame * self.DefenseBody.columns
                self.DefenseBody.last_frame = self.DefenseBody.first_frame + self.DefenseBody.columns - 1
                if self.DefenseBody.frame > self.DefenseBody.last_frame:
                    self.DefenseBody.frame = self.DefenseBody.first_frame
                elif self.DefenseBody.frame < self.DefenseBody.first_frame:
                    self.DefenseBody.frame = self.DefenseBody.last_frame
                self.DefenseBody.X = self.postion[0] - 6
                if self.direction:
                    self.Shield.X = self.postion[0] - 4
                else:
                    self.Shield.X = self.postion[0] + 19
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
                self.Body.X = self.postion[0]
    def draw(self,screen):
        if not self.defense_actioning and not self.defense_hold:
            self.BodyGroup.add(self.Foot)
            self.BodyGroup.add(self.Body)
            self.BodyGroup.remove(self.DefenseBody)
            self.BodyGroup.remove(self.Shield)
        else:
            self.BodyGroup.remove(self.Foot)
            self.BodyGroup.remove(self.Body)
            self.BodyGroup.add(self.DefenseBody)
            self.BodyGroup.add(self.Shield)
            
        self.BodyGroup.update(pygame.time.get_ticks())
        self.BodyGroup.draw(screen)
        if self.hp > 0:
            #血框
            pygame.draw.rect(screen, Config.WHITE, (int(self.Body.X - 8), int(self.Body.Y - 5),40,5),1)
            #血條
            pygame.draw.rect(screen, Config.RED, (int(self.Body.X - 7), int(self.Body.Y - 4),int(38*(self.hp/100)),3),0)
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
