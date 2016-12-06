import pygame,math
from Config import *
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
        self.rect = pygame.Rect(0,0,width,height)
        self.columns = columns
        rect = self.master_image.get_rect()
        self.last_frame = (rect.width // width) * (rect.height // height) - 1
    def update(self):
        if self.master_image != None:
            frame_x = (self.frame % self.columns) * self.frame_width
            frame_y = (self.frame // self.columns) * self.frame_height
            rect = pygame.Rect(frame_x, frame_y, self.frame_width, self.frame_height)
            self.image =  pygame.transform.flip(self.master_image.subsurface(rect), self.direction,False) 
class Bullet(MySprite):
    def __init__(self,weapon,postion,postion_adj,move):
        MySprite.__init__(self) #extend the base Sprite class
        self.damage = weapon.Damage
        x_distance = postion_adj[0]-move[0]
        y_distance = postion_adj[1]-move[1]
        distance = math.sqrt(math.pow(x_distance,2) + math.pow(y_distance,2))
        self.speed = (x_distance/distance*weapon.BulletSpeed,y_distance/distance*weapon.BulletSpeed)
        self.image = pygame.Surface((4, 4))
        pygame.draw.circle(self.image, Config.BLUE, (2, 2), 2, 0)
        self.rect = self.image.get_rect()
        self.postion = postion
        self.rect.center = postion
        self.old_pos = [postion[0],postion[1]]
        self.limit_dis = weapon.LimitRange
    def update(self):
        self.postion[0] -= self.speed[0]
        self.postion[1] -= self.speed[1]
        self.rect.center = self.postion
        if math.sqrt(math.pow(self.position[0]-self.old_pos[0],2)+math.pow(self.position[1]-self.old_pos[1],2))>=self.limit_dis:
            self.kill()
class Shield(MySprite):
    def __init__(self):
        MySprite.__init__(self) #extend the base Sprite class
        self.image = pygame.Surface((5, 30))
        pygame.draw.rect(self.image, Config.BLUE, (0, 0, 5, 30))
        self.rect = self.image.get_rect()
    def update(self):
        pass
class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.image.load(Config.BlockImage)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
    def update(self,entities):
        attacker = None
        attacker = pygame.sprite.spritecollideany(self, entities)
        if attacker != None:
            entities.remove(attacker)
class Unit(object):
    def __init__(self,x,y,weapon,isPlayer):
        self.direction = False #False 面右
        self.isPlayer = isPlayer
        self.magazine = weapon.Magazine #彈匣量
        self.hp = 100
        self.weapon = weapon
        #火控
        self.lastFire = 0#最後射擊時間
        self.shootRate = weapon.ShootRate    #射擊間隔(MS)
        self.fire_actioned = True
        self.AutoFire = weapon.AutoFire
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
        self.rect = pygame.Rect(x, y, 32, 32)#絕對座標
        self.rect_adj = pygame.Rect(x, y, 32, 32) #畫面座標
        self.move_speed = weapon.MoveSpeed #移動速度
        self.xVel = 0 #加速度
        self.yVel = 0 #加速度
        #部位
        self.Foot = MySprite()
        self.Foot.load("images/Foot.png", 17, 12, 4)
        self.Foot.direction = self.direction
        self.Body = MySprite()
        self.Body.load("images/Fire.png", 19, 20, 5)
        self.Body.direction = self.direction
        self.DefenseBody = MySprite()
        self.DefenseBody.load('images/defense.png', 40, 35, 6)
        self.DefenseBody.direction = self.direction
        self.Shield = Shield()
    def MoveRight(self):
        if not self.defense_actioning:
            self.xVel += self.move_speed
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
            self.xVel -= self.move_speed
            #腳
            if self.direction:
                self.Foot.frame += 1
            else:
                self.Foot.frame -= 1
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
            return [self.rect.x - 10,self.rect.y-7]
    def FireBreak(self):
        self.FireBreaked = True
    def Fire(self,TargetPosition):
        ticks = pygame.time.get_ticks()
        if self.magazine > 0:
            if ticks > self.lastFire + self.shootRate and self.FireBreaked and self.reload_actioned and not self.defense_actioning:
                self.magazine -= 1
                self.fire_actioned = False
                pygame.mixer.Sound(Config.PATH + self.weapon.FireSound).play()
                self.lastFire = ticks
                postion = self.Body.position
                self.Body.load("images/Fire.png", 19, 20, 5)
                self.Body.position = postion
                if not self.AutoFire:
                    self.FireBreaked = False
                return Bullet(self.weapon,self.getShootPosition(),self.rect_adj,TargetPosition)
        else:
            self.Reload()
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
            pygame.mixer.Sound(Config.PATH + self.weapon.ReloadSound).play()
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
            pygame.mixer.Sound(Config.PATH + self.weapon.ReloadSound).play()
            self.magazine = self.weapon.Magazine #彈匣量
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
    def update(self,camera,entities,bullet):
        self.Foot.direction = self.direction
        self.Body.direction = self.direction
        self.DefenseBody.direction = self.direction
        self.collisionBlock(entities)
        self.collisionBullet(bullet)
        self.rect_adj = camera.apply(self)
        if self.hp >= 0:
            #腳
            self.Foot.first_frame = self.weapon.ID * self.Foot.columns
            self.Foot.last_frame = self.Foot.first_frame + self.Foot.columns - 1
            if self.Foot.frame > self.Foot.last_frame:
                self.Foot.frame = self.Foot.first_frame
            elif self.Foot.frame < self.Foot.first_frame:
                self.Foot.frame = self.Foot.last_frame
            if self.direction:
                self.Foot.X = self.rect.x
            else:
                self.Foot.X = self.rect.x - 4
            self.Foot.Y = self.rect.y
            #身
            if self.defense_actioning or self.defense_hold:
                self.DefenseBody.first_frame = self.Foot.frame * self.DefenseBody.columns
                self.DefenseBody.last_frame = self.DefenseBody.first_frame + self.DefenseBody.columns - 1
                if self.DefenseBody.frame > self.DefenseBody.last_frame:
                    self.DefenseBody.frame = self.DefenseBody.first_frame
                elif self.DefenseBody.frame < self.DefenseBody.first_frame:
                    self.DefenseBody.frame = self.DefenseBody.last_frame
                if self.direction:
                    self.DefenseBody.X = self.rect.x - 14
                    self.Shield.X = self.rect.x - 7
                else:
                    self.DefenseBody.X = self.rect.x - 10
                    self.Shield.X = self.rect.x + 20
                self.DefenseBody.Y = self.rect.y - 23
                self.Shield.Y = self.rect.y - 19
                self.defenseUpdaet()
            else:
                self.Body.first_frame = self.weapon.ID * self.Body.columns
                self.Body.last_frame = self.Body.first_frame + self.Body.columns - 1
                if self.Body.frame > self.Body.last_frame:
                    self.Body.frame = self.Body.first_frame
                elif self.Body.frame < self.Body.first_frame:
                    self.Body.frame = self.Body.last_frame
                if not self.reload_actioned:
                    self.reloadUpdate()
                elif not self.fire_actioned:
                    self.fireUpdate()
            if self.direction:
                self.Body.X = self.rect.x - 6
            else:
                self.Body.X = self.rect.x            
            self.Body.Y = self.rect.y - 20
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
    def collisionBlock(self,target):
        onFloat = False
        #移動碰撞
        self.Foot.rect.x += self.xVel
        self.rect.x += self.xVel
        attacker = None
        attacker = pygame.sprite.spritecollideany(self.Foot, target)
        if attacker != None:
            self.rect.y -= Config.BlockHeight
        self.xVel = 0
        #踩空設定
        self.Foot.rect.y += 2
        attacker = None
        attacker = pygame.sprite.spritecollideany(self.Foot, target)
        if attacker != None:
            onFloat = True
        if not onFloat:
            self.rect.y += Config.BlockHeight
    def collisionBullet(self,target):
        #盾牌碰撞
        if self.defense_actioning or self.defense_hold:
            attacker = None
            attacker = pygame.sprite.spritecollideany(self.Shield, target)
            if attacker != None:
                #self.hp -= attacker.damage
                pygame.mixer.Sound(Config.PATH+'/musices/defense.wav').play()
                target.remove(attacker)
        #腿部碰撞
        attacker = None
        attacker = pygame.sprite.spritecollideany(self.Foot, target)
        if attacker != None:
            self.hp -= attacker.damage
            pygame.mixer.Sound(Config.PATH+'/musices/Hit.wav').play()
            target.remove(attacker)
        #身體碰撞
        attacker = None
        attacker = pygame.sprite.spritecollideany(self.Body, target)
        if attacker != None:
            self.hp -= attacker.damage
            pygame.mixer.Sound(Config.PATH+'/musices/Hit.wav').play()
            target.remove(attacker)
