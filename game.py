import pygame, sys,random,os,Config
import math
from Unit import *
from System import *
def AI(ENEMYS,PLAYER,BULLETS):
    for bot in ENEMYS:
        if PLAYER.rect.x>bot.rect.x:
            bot.direction = False
        else:
            bot.direction = True
        bot.lastAction+=1
        if bot.hp<=0:
            if bot.lastAction==bot.actionRate:
                ENEMYS.remove(bot)
                break
        else:
            if bot.action==1:
                bot.lastAction+=10
                if bot.magazine > 0:
                    bot.FireBreak()#不知道autofire要怎麼用?
                    bullet=bot.Fire((PLAYER.rect.x,PLAYER.rect.y))
                    if bullet != False:
                        BULLETS.add(bullet)	
                    else:
                        bot.Reload()
            elif bot.action==2:
                bot.lastAction+=1
                if(bot.direction):
                    bot.MoveLeft()
                else:
                    bot.MoveRight()
            if bot.lastAction >= bot.actionRate:#決定行為
                bot.lastAction=0
                i=random.randint(0,100)
                if i<40:
                    bot.action=1
                elif i<80:
                    bot.action=2
                else:
                    bot.action=0
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
    PLAYER = Player(0,Config.BlockFloat-12,Config.Pistol())
    BlackGroundImage = pygame.image.load(Config.BackGroundImage)
    BG_rect = BlackGroundImage.get_rect()
    entities = pygame.sprite.Group()
    BULLETS = pygame.sprite.Group()
    last_block = random.randrange(1,6)
    block_num = 1000
    for i in range(0,block_num,1):
        last_block = last_block + random.randrange(-1,2)
        if last_block > 6:
            last_block = 6
        elif last_block < 1:
            last_block = 1
        for j in range(0,last_block,1):    
            p = Platform(i*32, 500 - j*14)
            entities.add(p)
    camera = Camera(BG_rect[2],BG_rect[3], block_num*32, BG_rect[3])
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
            if(PLAYER.rect.x+camera.rect.x>=10):#左側lock
                PLAYER.MoveLeft()
        if pressed[pygame.K_d]:
            PLAYER.MoveRight()
        if pressed[pygame.K_r]:
            PLAYER.Reload()
        if pressed[pygame.K_SPACE]:
            grenade = PLAYER.ThrowGrenade(mouse)
            if grenade != False:
                BULLETS.add(grenade)
        if pressed[pygame.K_s]:
            if PLAYER.reload_actioned and PLAYER.fire_actioned:
                PLAYER.defense_actioning = True
        else:
            PLAYER.defense_actioning = False
        #新增敵人
        '''
        if (random.randint(0,100)<5 and len(ENEMYS)<15):
            enemy = Enemy(PLAYER.rect.x+800,Config.BlockFloat-12,Config.Pistol())
            ENEMYS.append(enemy)
        #AI
        AI(ENEMYS,PLAYER,BULLETS)
        '''
        camera.update(PLAYER)
        for e in entities:
            e.update(BULLETS)
            DISPLAYSURF.blit(e.image, camera.apply(e))
        for b in BULLETS:
            b.update()
            DISPLAYSURF.blit(b.image, camera.apply(b))
	#角色更新
        PLAYER.update(camera,entities,BULLETS)
        PLAYER.draw(DISPLAYSURF,camera)
        #敵人更新
        for i, enemy in enumerate(ENEMYS, start=0):
            enemy.update(camera,entities,BULLETS)
            enemy.draw(DISPLAYSURF,camera)
        #玩家彈匣描繪
        for i in range(0,PLAYER.magazine,1):
            DISPLAYSURF.blit(pygame.image.load(Config.PATH+PLAYER.weapon.Ammo), (200 + 9*i, 550))
	#分數描繪
        SourceText = pygame.font.Font(Config.Font,30)
        TextSurf, TextRect = text_objects("擊殺人數:"+str(SOURCE), SourceText,Config.WHITE)
        TextRect.x = 0
        TextRect.y = 550
        DISPLAYSURF.blit(TextSurf, TextRect)
        DISPLAYSURF.blit(AimCursor, AimCursor_rect)
        pygame.display.update()
        fpsClock.tick(Config.FPS)
if __name__ == '__main__':
    main()
