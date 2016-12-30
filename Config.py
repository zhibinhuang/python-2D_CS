import os
BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED = (180,0,0)
BLUE = (62,186,238)
GREEN = (0,180,0)
BRIGHT_GREEN = (0,255,0)
BRIGHT_RED = (255,0,0)
YELLOW=(255,215,0)
Gspeed = 0.2
FPS = 40 # frames per second setting
PATH = os.path.join(os.path.dirname(__file__))
BackGroundImage = PATH+'/images/BACK.png'
TitleImage = PATH+'/images/Title.png'
BlockImage = PATH+'/images/block.png'
BlockHeight = 14
BlockFloat = 500 #磚塊起始點 Y軸座標
AimCursorImage = PATH+'/images/cursor_aim.png'
Font = PATH+'/fonts/DFT_B3.ttc'
GameBGM = PATH+'/musices/bgm.mp3'
VERSION = "Ver 3.0"

class Pistol(object):
        ID = 0
        ShootRate = 200
        MoveSpeed = 3
        Damage = 10
        BulletSpeed = 5
        LimitRange = 500
        FireSound = '/musices/Gun1.wav'
        ReloadSound = '/musices/Reload.wav'
        FireAction = 3
        ReloadAction = 5
        Magazine = 12
        Ammo = '/images/ammo/9MM.png'
        AutoFire = False
class SMG(object):
        ID = 1
        ShootRate = 100
        MoveSpeed = 3
        Damage = 10
        BulletSpeed = 5
        LimitRange = 500
        FireSound = '/musices/Gun1.wav'
        ReloadSound = '/musices/Reload.wav'
        FireAction = 3
        ReloadAction = 6
        Magazine = 30
        Ammo = '/images/ammo/9MM.png'
        AutoFire = True
class Shotgun(object):
        ID = 0
        ShootRate = 500
        MoveSpeed = 3
        Damage = 10
        BulletSpeed = 5
        LimitRange = 300
        FireSound = '/musices/Gun1.wav'
        ReloadSound = '/musices/Reload.wav'
        FireAction = 3
        ReloadAction = 5
        Magazine = 5
        Ammo = '/images/ammo/9MM.png'
        AutoFire = False
class Grenade(object):
        ID = 100
        Damage = 30
        BulletSpeed = 15
        ThrowSpeed = 8
        LimitRange = 200
WEAPON=[Pistol(),SMG(),Shotgun()]
