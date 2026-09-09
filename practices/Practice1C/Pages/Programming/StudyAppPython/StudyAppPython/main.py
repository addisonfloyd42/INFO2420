import os, pickle, sys
import data.main_prog as main_prog
from data.game_classes import *
from copy import deepcopy
import pygame
from pygame import image
from pygame import mixer
from pygame import display as disp
from random import randint
import asyncio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(DATA_DIR, "Assets")

WIDTH, HEIGHT = 1000, 1000

disp.set_caption("CHENEY QUEST")
disp.set_icon(image.load(os.path.join(ASSETS_DIR,"DickCheney.png")))
WIN = disp.set_mode((WIDTH, HEIGHT))

pygame.font.init()

#mixer.init()
print("Mixer init:", pygame.mixer.get_init())

FROM_BEGINNING = False
SAVELESS = False 

UPLOAD_BEFORE = True

CHAR_W,CHAR_H = 150,150

CHAR_FILE= os.path.join(DATA_DIR,"Pickle","main_char.pkl")
LEVEL_FILE = os.path.join(DATA_DIR,"Pickle","level.pkl")


margin_l = 40
margin_t = margin_l - 20

_ , font_h = pygame.font.SysFont("arialblack", 50).size("placeholder")

line_height = 25
PAUSE_W, PAUSE_H = 350,300

OPT_W, OPT_H = 500,500

pause_gui = {"pause_menu":GUI(
    ("pause_back",GUIElement(0,0,WIDTH,HEIGHT,None,100,(0,0,0))),
    ("pause_mid",GUIElement(WIDTH/2-PAUSE_W/2,HEIGHT/2-PAUSE_H/2,PAUSE_W,PAUSE_H,None,color = (255,255,255))),
    ("0resume", Text(pygame.font.SysFont("arialblack", 50),WIDTH/2-PAUSE_W/2 + margin_l,HEIGHT/2-PAUSE_H/2 + margin_t,"resume",WIDTH, HEIGHT,255,True,(0,0,0))),
    ("1options", Text(pygame.font.SysFont("arialblack", 50),WIDTH/2-PAUSE_W/2 + margin_l,HEIGHT/2-PAUSE_H/2 + font_h + line_height ,"options",WIDTH, HEIGHT,255,True,(0,0,0))),
    ("2quit", Text(pygame.font.SysFont("arialblack", 50),WIDTH/2-PAUSE_W/2 + margin_l,HEIGHT/2-PAUSE_H/2 + 2*font_h+ 2*line_height,"quit",WIDTH, HEIGHT,255,True,(0,0,0)))),
    
    "options_menu":GUI(
    ("options_back",GUIElement(0,0,WIDTH,HEIGHT,None,100,(0,0,0))),
    ("options_mid",GUIElement(WIDTH/2-OPT_W/2,HEIGHT/2-OPT_H/2,OPT_W,OPT_H,None,color = (255,255,255))),
    ("0back", Text(pygame.font.SysFont("arialblack", 35),WIDTH/2-OPT_W/2 + margin_l,HEIGHT/2+180,"back",WIDTH, HEIGHT,255,True,(0,0,0))))}

LEVELS = {
    "0":[
    [GroundBlock(0,900,700,100),
    GroundBlock(0,800,300,100),
    GroundBlock(700,450,300,100),
    GroundBlock(0,50,200,100),
    GroundBlock(400,-300,600,100),
    GroundBlock(650,-450,250,150),
    GroundBlock(900,-650,100,350),
    GroundBlock(400,-1000,200,100),
    GroundBlock(0,-1350,100,100),
    GroundBlock(400,-1700,200,100),
    GroundBlock(900,-2050,100,100),
    GroundBlock(0,-2400,600,100),
    GroundBlock(0,-2600,200,200),
    GroundBlock(400,-2900,200,100),
    GroundBlock(900,-3300,100,100)],
    
    [Obama(850,-150,150,150,270,950,40,WIDTH,HEIGHT),
    Obama(0,-500,150,150,90,500,60,WIDTH,HEIGHT),
    Jeb(150,-850,200,200,0,1550,40,WIDTH,HEIGHT),
    Jeb(650,-3150,200,200,180,2550,40,WIDTH,HEIGHT)],
    
    [Checkpoint(400,-2800,100,400,True)]
    ],

    "1":[
    [GroundBlock(900,-2050,100,100),
    GroundBlock(0,-2400,600,100),
    GroundBlock(0,-2600,200,200),
    GroundBlock(400,-2900,200,100),
    GroundBlock(900,-3300,100,100),
    GroundBlock(350,-3650,300,100),
    GroundBlock(0,-4000,100,100),
    GroundBlock(450,-4350,100,100),
    GroundBlock(0,-4700,100,100),
    GroundBlock(350,-5050,300,100),
    GroundBlock(900,-5400,100,100),
    GroundBlock(450,-5750,100,100),
    GroundBlock(900,-6100,100,100),
    GroundBlock(350,-6450,300,100),
    GroundBlock(350,-6550,150,100),
    GroundBlock(0,-6850,100,500),
    GroundBlock(0,-7200,100,100),
    GroundBlock(0,-7550,100,100),
    GroundBlock(0,-7900,100,100),
    GroundBlock(500,-8125,500,100),
    GroundBlock(750,-8225,250,100),
    GroundBlock(0,-9275,150,200),
    GroundBlock(0,-9775,300,500),
    GroundBlock(0,-8575,600,100),
    GroundBlock(0,-8875,350,300),
    GroundBlock(700,-9175,300,300)],

    [Jeb(150,-850,200,200,0,1550,40,WIDTH,HEIGHT),
    Jeb(650,-3150,200,200,180,2550,40,WIDTH,HEIGHT),
    OJ(350,-3950,300,300,0,(-3950,-4950),20),
    OJ(350,-6350,300,300,180,(-5350,-6350),20),
    Obama(850,-6875,150,150,270,825,60,WIDTH,HEIGHT),
    Obama(850,-7225,150,150,270,825,50,WIDTH,HEIGHT),
    Obama(850,-7575,150,150,270,825,40,WIDTH,HEIGHT),
    Obama(850,-7925,150,150,270,825,30,WIDTH,HEIGHT),
    Jeb(300,-9775,300,300,180,975,38,WIDTH,HEIGHT)],

    [Checkpoint(400,-2800,100,400,False),
     Checkpoint(600,-8575,400,100,True)]
    ],

    "2":[
    [GroundBlock(0,-7900,100,100),
    GroundBlock(500,-8125,500,100),
    GroundBlock(750,-8225,250,100),
    GroundBlock(0,-9275,150,200),
    GroundBlock(0,-9775,300,500),
    GroundBlock(0,-8575,600,100),
    GroundBlock(0,-8875,350,300),
    GroundBlock(700,-9175,300,300),
    GroundBlock(900, -9575, 100, 400),
    GroundBlock(0, -9875, 700, 100),
    GroundBlock(0, -10125, 300, 75),
    GroundBlock(500, -10450, 500, 400),
    GroundBlock(0,-11450,200,1350),
    GroundBlock(850,-10850,150,400),
    GroundBlock(200,-11150,100,100),
    GroundBlock(800,-11750,100,100),
    GroundBlock(0,-12100,200,200),
    GroundBlock(200,-12100,100,100),
    GroundBlock(500,-12400,500,100),
    GroundBlock(700,-12650,300,250),
    GroundBlock(800,-13050,200,200),
    GroundBlock(900,-12850,100,200),
    GroundBlock(0,-12900,300,400)],

    [Obama(850,-7925,150,150,270,825,30,WIDTH,HEIGHT),
     Jeb(300,-9775,300,300,180,975,38,WIDTH,HEIGHT),
     Obama(0,-10050,175,175,90,925,80,WIDTH,HEIGHT),
     Clinton(200,-9575,125,125,2,200,900),
     OJ(150,-11050,200,200,90,(200,800),17),
     Bernie(600,-10500,250,250),
     OJ(200,-11350,200,200,0,(-11350,-12000),6.5),
     Bernie(750,-12300,250,250)],

    [Checkpoint(600,-8575,400,100,False),
     Checkpoint(200,-12500,100,400,True)]
    ],

    "3":[
    [GroundBlock(800,-11750,100,100),
     GroundBlock(0,-12100,200,200),
     GroundBlock(200,-12100,100,100),
     GroundBlock(500,-12400,500,100),
     GroundBlock(700,-12650,300,250),
     GroundBlock(800,-13050,200,200),
     GroundBlock(900,-12850,100,200),
     GroundBlock(0,-12900,300,400),
     GroundBlock(0,-13325,100,200),
     GroundBlock(800,-13275,150,275),
     GroundBlock(300,-13675,100,100)],

    [OJ(200,-12000,200,200,180,(-11350,-12000),6.5),
     Bernie(750,-12300,250,250),
     Bernie(0,-13125,225,225),
     Clinton(500,-13500,125,125,2,200,1000),
     Obama(0,-13450,150,150 ,90,950,40,WIDTH,HEIGHT)],

    [Checkpoint(200,-12500,100,400,False)]]}


def write_to_file(path, *args):
    out = []
    for arg in args:
        out.append(arg)
    with open(path, "wb") as file:
        pickle.dump(out,file,pickle.HIGHEST_PROTOCOL)

async def main():
    ##global bullet_list
    bullet_list = []
    

    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    FIRST_CONT = main_prog.Controller(0)
    if joysticks:
        FIRST_CONT.used = True
    main_cont = FIRST_CONT

    ##global cheney, lvl_num, h_scroll, deaths
    lvl_num = 0
    cheney = Char(WIDTH/2,900,CHAR_W,CHAR_H,1.6,5,1,0.855,18,90)
    h_scroll = 0
    deaths = 0
    #Open character location if possible
    if os.path.exists(CHAR_FILE):
        if FROM_BEGINNING:
            os.remove(CHAR_FILE)
        elif os.stat(CHAR_FILE).st_size != 0:
            with open(CHAR_FILE,"rb") as file:
                pickle_list = pickle.load(file)
                cheney = pickle_list[0]
                h_scroll = pickle_list[1]
                lvl_num = pickle_list[2]
                deaths = pickle_list[3]
    #mixer.init()
    main_song = None
    #main_song = Sound(os.path.join(DATA_DIR,"Music","background.ogg"),0.35,mixer.Channel(0))
    #main_song.channel.set_endevent(pygame.USEREVENT)
    #main_song.play()
    start_color = randint(0,359)
    while True:
        await asyncio.sleep(0)
        last_cheney, last_h_scroll = deepcopy(cheney), deepcopy(h_scroll)
        #cProfile.run('main_prog.level_run(WIN, cheney, *LEVELS[str(lvl_num)], bullet_list, h_scroll)')
        out, bullet_list, cheney, h_scroll, main_cont = await main_prog.level_run(WIN, cheney, *LEVELS[str(lvl_num)], bullet_list, h_scroll, main_cont, lvl_num, pause_gui, main_song, SAVELESS, start_color, deaths)
        if  out == "quit":
            break
            #sys.exit()
        if out == "next":
            if not SAVELESS:
                write_to_file(CHAR_FILE,cheney, h_scroll, lvl_num,deaths)
                change = randint(-15,15)
                start_color = start_color-180+change
                if start_color < 0:
                    start_color += 360
            lvl_num += 1
        else:
            deaths += 1
            start_color = randint(0,359)
            if main_cont.used:
                main_cont = main_prog.Controller(0)
                main_cont.used = True
            if SAVELESS:
                cheney = Char(WIDTH/2,900,CHAR_W,CHAR_H,1.6,5,1,0.855,18,90)
                h_scroll = 0
                lvl_num = 0
            else:
                cheney = last_cheney
                h_scroll = last_h_scroll
                write_to_file(CHAR_FILE,cheney, h_scroll, lvl_num,deaths)

if __name__ == "__main__":
    asyncio.run(main())