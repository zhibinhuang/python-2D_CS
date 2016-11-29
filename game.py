import pygame, sys,random,os
import math
from pygame.locals import *
from Config import *
from Unit import *
class Button(object):
    def __init__(self,x,y,displaySurface):
        self.ds = displaySurface
        self.x = x
        self.y = y
    def setIcon(self,w,h,ic,ac):
        self.w = w
        self.h = h
        self.ic = ic
        self.ac = ac
        self.IconType = "Icon"
    def setIconWithImage(self,IC_image,AC_image):
        self.ic = pygame.image.load(IC_image)
        self.ac = pygame.image.load(AC_image)
        self.w = self.ic.get_rect()[2]
        self.h = self.ic.get_rect()[3]
        self.IconType = "Image"
    def setAction(self,action):
        self.Action = action
    def setFont(self,msg,font,size=20):
        self.msg = msg
        self.font = font
        self.size = size
    def update(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.x + self.w > mouse[0] > self.x and self.y + self.h > mouse[1] > self.y:
            if self.IconType == "Icon":
                pygame.draw.rect(self.ds,self.ac,(self.x,self.y,self.w,self.h))
            else:
                self.ds.blit(self.ac, (self.x, self.y))
            if click[0] == 1 and self.Action != None:
                self.Action()
        else:
            if self.IconType == "Icon":
                pygame.draw.rect(self.ds,self.ic,(self.x,self.y,self.w,self.h))
            else:
                self.ds.blit(self.ic, (self.x, self.y))
        if self.IconType == "Icon":
            buttonText = pygame.font.Font(self.font,self.size)
            textSurf, textRect = text_objects(self.msg, buttonText,WHITE)
            textRect.center = (self.x + self.w / 2, self.y + self.h /2 )
            self.ds.blit(textSurf, textRect)
def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()
def getHightRank():
    file = open(PATH+"/rank.txt", 'r', encoding='UTF-8')
    HightRank = int(file.readline())
    file.close()
    return HightRank
def quitgame():
    pygame.quit()
    quit()
def titleStart():
    pygame.mixer.music.load(Config.PATH+'/musices/Title.mp3')
    pygame.mixer.music.play(-1,0.0)
    StartButton = Button(320,450,DISPLAYSURF)
    StartButton.setIconWithImage(Config.PATH+'/images/Start_ic.png',Config.PATH+'/images/Start_ac.png')
    StartButton.setAction(gameStart)
    EndButton = Button(320,520,DISPLAYSURF)
    EndButton.setIconWithImage(Config.PATH+'/images/End_ic.png',Config.PATH+'/images/End_ac.png')
    EndButton.setAction(quitgame)
    TitleImage = pygame.image.load(Config.TitleImage)
    while True:
        for event in pygame.event.get():#偵測是否關閉
            if event.type == 12:
                quitgame()
	#畫面初始化
        DISPLAYSURF.fill(Config.WHITE)
	#背景
        DISPLAYSURF.blit(TitleImage, (0, 0))
	#按鈕
        StartButton.update()
        EndButton.update()
    	#版本號
        VersionText = pygame.font.Font(Config.PATH+'/fonts/DFT_B3.ttc',20)
        textSurf, textRect = text_objects(Config.VERSION, VersionText,Config.WHITE)
        DISPLAYSURF.blit(textSurf, (TitleImage.get_rect()[2]-textRect[2], TitleImage.get_rect()[3] - textRect[3]))
	#鼠標
        mouse = pygame.mouse.get_pos()
        AimCursor = pygame.image.load(Config.PATH+'/images/cursor_point.png')
        AimCursor_rect = AimCursor.get_rect()
        AimCursor_rect.center = mouse
        DISPLAYSURF.blit(AimCursor, AimCursor_rect)
        pygame.display.update()
        fpsClock.tick(Config.FPS)
def main():
    global fpsClock,DISPLAYSURF
    pygame.init()
    pygame.mixer.init()
    pygame.mouse.set_visible(False)
    fpsClock = pygame.time.Clock()
    TitleImage = pygame.image.load(Config.TitleImage)
    DISPLAYSURF = pygame.display.set_mode((TitleImage.get_rect()[2], TitleImage.get_rect()[3]), 0, 32)
    pygame.display.set_caption('2D-CS')
    titleStart()
def gameStart():
    BlockArray = []
    SOURCE = 0
    ENEMYS = []
    PAUSE = False
    pygame.mixer.music.load(Config.GameBGM)
    pygame.mixer.music.play(-1,0.0)
    PLAYER = Unit(0,Config.BlockFloat-12,0,True)
    BlackGroundImage = pygame.image.load(Config.BackGroundImage)
    BULLETS = pygame.sprite.Group()
    Enemy = Unit(300,Config.BlockFloat-12,0,False)
    Enemy.direction = True
    Enemy.defense_actioning = True
    ENEMYS.append(Enemy)
    while True:
	#偵測是否關閉
        for event in pygame.event.get():
            if event.type == 12:
                quitgame()
	#畫面初始化
        DISPLAYSURF.fill(Config.WHITE)
        DISPLAYSURF.blit(BlackGroundImage, (0, 0))
	#準心更新
        mouse = pygame.mouse.get_pos()
        AimCursor = pygame.image.load(Config.AimCursorImage)
        AimCursor_rect = AimCursor.get_rect()
        AimCursor_rect.center = mouse
        DISPLAYSURF.blit(AimCursor, AimCursor_rect)
        PLAYER.SeekCheck(mouse[0])
        #開火偵測
        click = pygame.mouse.get_pressed()
        if click[0] == 1:
            bullet = PLAYER.Fire(mouse)
            if bullet != False:
                BULLETS.add(bullet)
        else:
            PLAYER.FireBreak()
	#角色操作
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_a]:
            PLAYER.MoveLeft()
        if pressed[pygame.K_d]:
            PLAYER.MoveRight()
        if pressed[pygame.K_r]:
            PLAYER.Reload()
        if pressed[pygame.K_s]:
            if PLAYER.reload_actioned and PLAYER.fire_actioned:
                PLAYER.defense_actioning = True
        else:
            PLAYER.defense_actioning = False
        BULLETS.update()
        BULLETS.draw(DISPLAYSURF)
	#角色更新
        PLAYER.update(BlackGroundImage.get_rect())
        #敵人更新
        for i, enemy in enumerate(ENEMYS, start=0):
            enemy.collision(BULLETS)
            enemy.update(BlackGroundImage.get_rect())
            enemy.draw(DISPLAYSURF)
        #玩家彈匣描繪
        for i in range(0,PLAYER.magazine,1):
            DISPLAYSURF.blit(pygame.image.load(Config.PATH+'/images/ammo/' + Config.AMMO[PLAYER.weapon]+'.png'), (200 + 9*i, 550))
	#分數描繪
        SourceText = pygame.font.Font(Config.Font,30)
        TextSurf, TextRect = text_objects("擊殺人數:"+str(SOURCE), SourceText,Config.WHITE)
        TextRect.x = 0
        TextRect.y = 550
        DISPLAYSURF.blit(TextSurf, TextRect)
        PLAYER.draw(DISPLAYSURF)
        pygame.display.update()
        fpsClock.tick(Config.FPS)
if __name__ == '__main__':
    main()
