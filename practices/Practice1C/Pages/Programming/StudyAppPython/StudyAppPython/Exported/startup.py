import os, pickle, cProfile, sys
import data.main_prog as main_prog
from data.main_prog import Obama, Jeb, OJ, GroundBlock, Checkpoint, Char
from copy import deepcopy
import pygame
from pygame import image
from pygame import display as disp

WIDTH, HEIGHT = 1000, 1000

disp.set_caption("CHENEY QUEST")
disp.set_icon(image.load(os.path.join("data","Assets","DickCheney.png")))
WIN = disp.set_mode((WIDTH, HEIGHT))

FROM_BEGINNING = False  

UPLOAD_BEFORE = True

CHAR_W,CHAR_H = 150,150

CHAR_FILE= os.path.join("data","Pickle","main_char.pkl")
LEVEL_FILE = os.path.join("data","Pickle","level.pkl")

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
    GroundBlock(0,-8575,600,100),
    GroundBlock(0,-8875,300,300),
    GroundBlock(700,-9175,300,300)],

    [Jeb(150,-850,200,200,0,1550,40,WIDTH,HEIGHT),
    Jeb(650,-3150,200,200,180,2550,40,WIDTH,HEIGHT),
    OJ(350,-3950,300,300,0,(-3950,-4950),20),
    OJ(350,-6350,300,300,180,(-5350,-6350),20),
    Obama(850,-6875,150,150,270,825,60,WIDTH,HEIGHT),
    Obama(850,-7225,150,150,270,825,50,WIDTH,HEIGHT),
    Obama(850,-7575,150,150,270,825,40,WIDTH,HEIGHT),
    Obama(850,-7925,150,150,270,825,30,WIDTH,HEIGHT),
    Jeb(300,-9775,300,300,180,975,40,WIDTH,HEIGHT)],

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
    GroundBlock(0,-8875,300,300),
    GroundBlock(700,-9175,300,300),
    GroundBlock(900, -9575, 100, 400),
    GroundBlock(0, -9875, 700, 100),
    GroundBlock(0, -10150, 300, 100),
    GroundBlock(500, -10450, 500, 400),
    GroundBlock(0,-10450,150,300)],

    [Obama(850,-7925,150,150,270,825,30,WIDTH,HEIGHT),
     Jeb(300,-9775,300,300,180,975,40,WIDTH,HEIGHT),
     Obama(0,-10050,175,175,90,925,90,WIDTH,HEIGHT)],

    [Checkpoint(600,-8575,400,100,False)]
    ]}


def write_to_file(path, *args):
    out = []
    for arg in args:
        out.append(arg)
    with open(path, "wb") as file:
        pickle.dump(out,file,pickle.HIGHEST_PROTOCOL)

def main():
    ##global bullet_list
    bullet_list = []

    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    FIRST_CONT = main_prog.Controller()
    if joysticks:
        FIRST_CONT.used = True
    main_cont = FIRST_CONT

    ##global cheney, lvl_num, h_scroll
    lvl_num = 0
    cheney = Char(WIDTH/2,900,CHAR_W,CHAR_H,1.6,0.75,6,18,90)
    h_scroll = 0

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


    while True:
        last_cheney, last_h_scroll = deepcopy(cheney), deepcopy(h_scroll)
        #cProfile.run('main_prog.level_run(WIN, cheney, *LEVELS[str(lvl_num)], bullet_list, h_scroll)')
        out, bullet_list, cheney, h_scroll, main_cont = main_prog.level_run(WIN, cheney, *LEVELS[str(lvl_num)], bullet_list, h_scroll, main_cont, lvl_num)
        if  out == "quit":
            break
            #sys.exit()
        if out == "next":
            lvl_num += 1
            write_to_file(CHAR_FILE,cheney, h_scroll, lvl_num)
        else:
            main_cont = FIRST_CONT
            cheney = last_cheney
            h_scroll = last_h_scroll

if __name__ == "__main__":
    main()