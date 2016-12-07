import os
class Config(object):
        WHITE = (255, 255, 255)
        RED = (180,0,0)
        BLUE = (62,186,238)
        GREEN = (0,180,0)
        BRIGHT_GREEN = (0,255,0)
        BRIGHT_RED = (255,0,0)
        Gspeed = 0.2
        FPS = 20 # frames per second setting
        PATH = os.path.join(os.path.dirname(__file__))
        BackGroundImage = PATH+'/images/BACK.png'
        TitleImage = PATH+'/images/Title.png'
        BlockImage = PATH+'/images/block.png'
        BlockHeight = 14
        BlockFloat = 500 #磚塊起始點 Y軸座標
        AimCursorImage = PATH+'/images/cursor_aim.png'
        Font = PATH+'/fonts/DFT_B3.ttc'
        GameBGM = PATH+'/musices/bgm.mp3'
        VERSION = "Ver 2.0"
class Pistol(object):
        ID = 0
        ShootRate = 200
        MoveSpeed = 5
        Damage = 10
        BulletSpeed = 10
        LimitRange = 500
        FireSound = '/musices/Gun1.wav'
        ReloadSound = '/musices/Reload.wav'
        FireAction = 4
        ReloadAction = 8
        Magazine = 12
        Ammo = '/images/ammo/9MM.png'
        FireAction = 3
        ReloadAction = 8
        AutoFire = False
