import pygame, os, time, colorsys
from XInput import set_vibration, get_battery_information
from pygame import transform as tf
from pygame import mixer
import data.graphics as graphics
from data.game_classes import *
from time import perf_counter
from copy import deepcopy
from random import randint

FPS_CAP = 60
DEFAULT_DEADZONE = 0.2

TOP_LIM = 400
BOTTOM_LIM = 600


def die(args: list, cheney: Char, main_cont:Controller, clock:pygame.time.Clock, deaths, main_screen_ind):
    """Runs when the character dies."""
    args = list(args)
    args[9] = (220,30,50)
    cheney.dead = True
    args[6].surf_dict["death_text"].change_text(f"DEATHS: {deaths + 1}")
    if main_cont.used:
        vib = int(65535*0.9)
        incr = 10
        for i in range(0,50):
            clock.tick(FPS_CAP)
            set_vibration(main_cont.index,vib,vib)
            vib -= incr
            if vib < 0:
                vib = 0
            incr = incr * 2 #+= 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                    set_vibration(main_cont.index,0,0)
                    return "quit"
            graphics.draw_window(*args)
        set_vibration(main_cont.index,0,0)
    else:
        for i in range(0,50):
            clock.tick(FPS_CAP)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                    return "quit"
            graphics.draw_window(*args)
    return "die"

def pause(WIN:pygame.display, cheney:Char, ground_list:list, enemy_list:list, checkpoints:list, bullet_list:list, main_screen:GUI, h_scroll, start_color:tuple, pause_gui:GUI, clock:pygame.time.Clock, saveless):
    print(get_battery_information(0))
    mouse_down = False
    menu = "pause_menu"
    curr_button = 0
    cont_used = True
    moved = True
    mouse_coords = pygame.mouse.get_pos()
    press = False
    pygame.joystick.init()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                cont_used = True
                if event.axis == 1:
                    if abs(event.value)>DEFAULT_DEADZONE and not moved:
                        moved = True
                        if event.value > 0:
                            curr_button += 1
                            if curr_button > pause_gui[menu].max_button:
                                curr_button = 0
                        else:
                            curr_button -= 1
                            if curr_button < 0:
                                curr_button = pause_gui[menu].max_button
                    elif abs(event.value)<DEFAULT_DEADZONE and moved:
                        moved = False
            if event.type == pygame.MOUSEMOTION:
                cont_used = False
                mouse_coords = pygame.mouse.get_pos()
            if event.type == pygame.JOYBUTTONDOWN:
                cont_used = True
                if event.button == 0:
                    press = True
                if event.button == 7:
                    return 1
            if event.type == pygame.QUIT:
                return 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
                cont_used = False
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False
                cont_used = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 1
        for key in pause_gui[menu].surf_dict :
            if isinstance(pause_gui[menu].surf_dict[key],Text):
                temp = pause_gui[menu].surf_dict[key]
                if not cont_used:
                    if temp.x <= mouse_coords[0] <= temp.x + temp.w and temp.y <= mouse_coords[1] <= temp.y + temp.h:
                        temp.color = (177, 2, 212)
                        if menu == "pause_menu":
                            if key == "0resume" and mouse_down:
                                return 1
                            if key == "2quit" and mouse_down:
                                return 0
                            if key == "1options" and mouse_down:
                                menu = "options_menu"
                                curr_button = 0
                                break
                        elif menu == "options_menu":
                            if key == "0back" and mouse_down:
                                menu = "pause_menu"
                                curr_button = 0
                                break
                    else:
                        temp.color = (0,0,0)
                else:
                    if int(key[0]) == curr_button:
                        temp.color = (177, 2, 212)
                        if press:
                            press = False
                            if menu == "pause_menu":
                                if key == "0resume":
                                    return 1
                                if key == "1options":
                                    menu = "options_menu"
                                    curr_button = 0
                                    break
                                if key == "2quit":
                                    return 0
                            elif menu == "options_menu":
                                if key == "0back":
                                    menu = "pause_menu"
                                    curr_button = 0;
                                    break
                    else:
                        temp.color = (0,0,0)
        #                    WIN, cheney, ground_list, enemy_list, checkpoints, bullet_list, level_gui,   h_scroll, st_c = 0, background = None, pause_gui = None, saveless = False
        graphics.draw_window(WIN, cheney, ground_list, enemy_list, checkpoints, bullet_list, main_screen, h_scroll, start_color, None, pause_gui = pause_gui[menu], saveless = saveless)

def update_h(h_scroll, *args):
    """Updates scroll height for given lists, assuming they're global."""
    for arg in args:
        for i in arg:
            i.rect.y = i.init_y + h_scroll
            if hasattr(i, "first_y_transl"):
                i.first_y_transl = i.first_y + h_scroll

def level_run(WIN: pygame.display, cheney:Char, ground_list, enemy_list, checkpoints, bullet_list, h_scroll, main_cont, level, pause_gui, main_song:Sound, saveless:bool, start_color, deaths):
    def font(size):
        return pygame.font.SysFont("arialblack", size) 
    
    WIDTH, HEIGHT = WIN.get_size()
    pygame.init()
    pygame.font.init()
    #font = pygame.font.SysFont("arialblack", 120)
    #['arial', 'arialblack', 'bahnschrift', 'calibri', 'cambria', 'cambriamath', 'candara', 'comicsansms', 'consolas', 'constantia', 'corbel', 'couriernew', 'ebrima', 'franklingothicmedium', 'gabriola', 'gadugi', 'georgia', 'holomdl2assets', 'impact', 'inkfree', 'javanesetext', 'leelawadeeui', 'leelawadeeuisemilight', 'lucidaconsole', 'lucidasans', 'malgungothic', 'malgungothicsemilight', 'microsofthimalaya', 'microsoftjhenghei', 'microsoftjhengheiui', 'microsoftnewtailue', 'microsoftphagspa', 'microsoftsansserif', 'microsofttaile', 'microsoftyahei', 'microsoftyaheiui', 'microsoftyibaiti', 'mingliuextb', 'pmingliuextb', 'mingliuhkscsextb', 'mongolianbaiti', 'msgothic', 'msuigothic', 'mspgothic', 'mvboli', 'myanmartext', 'nirmalaui', 'nirmalauisemilight', 'palatinolinotype', 'segoemdl2assets', 'segoeprint', 'segoescript', 'segoeui', 'segoeuiblack', 'segoeuiemoji', 'segoeuihistoric', 'segoeuisemibold', 'segoeuisemilight', 'segoeuisymbol', 'simsun', 'nsimsun', 'simsunextb', 'sitkasmall', 'sitkatext', 'sitkasubheading', 'sitkaheading', 'sitkadisplay', 'sitkabanner', 'sylfaen', 'symbol', 'tahoma', 'timesnewroman', 'trebuchetms', 'verdana', 'webdings', 'wingdings', 'yugothic', 'yugothicuisemibold', 'yugothicui', 'yugothicmedium', 'yugothicuiregular', 'yugothicregular', 'yugothicuisemilight']    

    sfx = SoundGroup(
        hit_sound = Sound(mixer.Sound(os.path.join("data",'Music','exp_fin.wav')),1),
        jump_sound = Sound(mixer.Sound(os.path.join("data",'Music','jump_fin.wav')),1),
        check_sound = Sound(mixer.Sound(os.path.join("data",'Music','check_fin.wav')),0.15)
    )

    music_vol = 0.5
    sfx_vol = 0.5

    sfx.set_vol(sfx_vol)
    main_song.set_volume(music_vol)
    

    main_screen = GUI()
    main_screen.add_to_dict("death_text",Text(font(40), "r", "t", f"DEATHS: {deaths}", WIDTH, HEIGHT, 100, True, (50,50,50)))
    if not saveless:
        main_screen.add_to_dict("level_text",Text(font(120), "r", "b", f"LEVEL {str(level + 1)}", WIDTH, HEIGHT, 120, True, None, True, 0))
    elif level == 0:
        main_screen.add_to_dict("level_text",Text(font(120), "r", "b", "ONE SHOT", WIDTH, HEIGHT, 120, True, None, True, 0))
    if main_cont.used:
        main_screen.add_to_dict("cont_icon",GUIElement(0,0,75,75,tf.scale(pygame.image.load(os.path.join("data","Assets","Controller.png")),(75,75)),127))
    else:
        main_screen.add_to_dict("cont_icon",GUIElement(0,0,75,75,tf.scale(pygame.image.load(os.path.join("data","Assets","WASD.png")),(75,75)),127))

    clock = pygame.time.Clock()
    main_screen.surf_dict
    run = True

    top_cap = 20000
    bottom_cap = h_scroll

    BULLET_VEL = 20
    
    frame_list = []
    
    jumped = False
    #update enemies
    for i in enemy_list:
        if hasattr(i,"first_x"):
            i.init_x = i.first_x
            i.init_y = i.first_y

    def event_handler():
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                main_song.play()
            if event.type == pygame.JOYAXISMOTION:
                main_cont.used = True
                if event.axis == 0:
                    main_cont.l_joy_x = event.value *(1+DEFAULT_DEADZONE)
                elif event.axis == 1:
                    main_cont.l_joy_y = event.value* (1+DEFAULT_DEADZONE)
            if event.type == pygame.JOYBUTTONDOWN:
                main_cont.used = True
                if event.button == 0:
                    main_cont.a = True
                if event.button == 7:
                    mixer.pause()
                    outcome = pause(WIN,cheney,ground_list,enemy_list,checkpoints, bullet_list,main_screen,h_scroll, start_color, pause_gui, clock, saveless)
                    if not outcome:
                        return False
                    mixer.unpause()
            if event.type == pygame.JOYBUTTONUP:
                main_cont.used = True
                if event.button == 0:
                    main_cont.a = False
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                main_cont.used = False
                if event.key == pygame.K_ESCAPE:
                    mixer.pause()
                    outcome = pause(WIN,cheney,ground_list,enemy_list,checkpoints, bullet_list,main_screen,h_scroll, start_color, pause_gui, clock, saveless)
                    if not outcome:
                        return False
                    mixer.unpause()
        return True

    while run:
        #print(-h_scroll+1000)
        #print(cheney.x_vel)
        #start = perf_counter()
        clock.tick(FPS_CAP)
        run = event_handler()
        #controller icon update
        if main_cont.used:
            main_screen.surf_dict["cont_icon"] = GUIElement(0,0,75,75,tf.scale(pygame.image.load(os.path.join("data","Assets","Controller.png")),(75,75)),127)
        else:
            main_screen.surf_dict["cont_icon"] = GUIElement(0,0,75,75,tf.scale(pygame.image.load(os.path.join("data","Assets","WASD.png")),(75,75)),127)
        #text update
        for key in main_screen.surf_dict:
            if isinstance(main_screen.surf_dict[key], Text):
                if main_screen.surf_dict[key].create_fade and main_screen.surf_dict[key].enabled:
                    if main_screen.surf_dict[key].tick == 0:
                        main_screen.surf_dict[key].fade_obj.fade_in(2)
                    elif main_screen.surf_dict[key].tick == 250:
                        main_screen.surf_dict[key].fade_obj.fade_out(2)
                        if main_screen.surf_dict[key].fade_obj.speed == None:
                            main_screen.surf_dict[key].enabled = False
                    main_screen.surf_dict[key].fade_obj.update_fade()
                    main_screen.surf_dict[key].tick += 1
        #enemy update
        for i in enemy_list:
            if isinstance(i,Obama) or isinstance(i,Jeb):
                if i.should_fire():
                    i.tick -= 1
                    if i.tick < 1:
                        i.tick = i.tick_cap
                        i.fire_bullet(bullet_list)
            elif isinstance(i,OJ):
                if cheney.rect.x + cheney.rect.w/2 >= i.init_x + i.rect.w/2:
                    i.flip = False
                else:
                    i.flip = True
                if i.dir == 0:
                    i.image = i.image_up
                    i.init_y -= i.speed
                    if i.init_y <= i.lims[1]:
                        i.dir = 180
                        i.init_y = i.lims[1]
                elif i.dir == 180:
                    i.image = i.image_down
                    i.init_y += i.speed
                    if i.init_y >= i.lims[0]:
                        i.dir = 0
                        i.init_y = i.lims[0]
                elif i.dir == 90:
                    i.init_x += i.speed
                    if i.init_x >= i.lims[1]:
                        i.dir = 270
                        i.init_x = i.lims[1]
                elif i.dir == 270:
                    i.init_x -= i.speed
                    if i.init_x <= i.lims[0]:
                        i.dir = 90
                        i.init_x = i.lims[0]
                i.rect.x = i.init_x
            elif isinstance(i, Clinton):
                i.update_pos(cheney, i.speed)
            elif isinstance(i, Bernie):
                i.flip = bool(i.rect.x < cheney.rect.x)
        #bullet update
        for i in bullet_list:
            if i.dir == 90 or i.dir == 270:
                i.init_x += BULLET_VEL*(i.dir == 90)- BULLET_VEL*(i.dir == 270)
                i.dist += abs(BULLET_VEL*(i.dir == 90)- BULLET_VEL*(i.dir == 270))
                i.rect.x = int(i.init_x)
                if i.dist >= i.end:
                    bullet_list.remove(i)
            elif i.dir == 0 or i.dir == 180:
                i.init_y += BULLET_VEL*(i.dir == 180)- BULLET_VEL*(i.dir == 0)
                i.dist += abs(BULLET_VEL*(i.dir == 180)- BULLET_VEL*(i.dir == 0))
                i.rect.y = int(i.init_y)
                if i.dist >= i.end:
                    bullet_list.remove(i)
        update_h(h_scroll, ground_list,enemy_list,bullet_list, checkpoints) #Updates scrollR
        #Y Controls
        up_k, down_k, left_k, right_k = False, False, False, False
        if main_cont.used:
            up_k = main_cont.a
            down_k = main_cont.l_joy_y >= 0.5
        else:
            keys_pressed = pygame.key.get_pressed()
            up_k = keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]
            down_k = keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]
            left_k = keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]
            right_k = keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]

        if down_k:
            cheney.g = 4.6
            cheney.squat = True
            if cheney.rect.height == cheney.h:
                cheney.rect.y += int(cheney.h/2)
                cheney.rect.height = int(cheney.h/2)
        else:
            cheney.squat = False
            cheney.g = 1.6
            if cheney.rect.height != cheney.h:
                cheney.rect.y -= int(cheney.h/2)
                cheney.rect.height = cheney.h
                if cheney.rect.collidelist(ground_list) != -1:
                    cheney.squat = True
                    cheney.rect.y += int(cheney.h/2)
                    cheney.rect.height = int(cheney.h/2)

        if up_k:
            if not jumped and cheney.touching:
                jumped = True
                sfx.play("jump_sound")
                cheney.jump(-35)
        else:
            jumped = False

        #Updates y
        _ = cheney.rect.y
        cheney.update_y(ground_list)
        if cheney.rect.y < TOP_LIM and h_scroll != top_cap:
            h_scroll += TOP_LIM - cheney.rect.y
            overshoot = 0
            if h_scroll > top_cap:
                overshoot = h_scroll - top_cap
                h_scroll = top_cap
                cheney.rect.y -= overshoot
            else:
                cheney.rect.y = TOP_LIM

        if cheney.rect.y + cheney.rect.height > BOTTOM_LIM and h_scroll != bottom_cap:
            h_scroll -= cheney.rect.y + cheney.rect.height - BOTTOM_LIM 
            overshoot = 0
            if h_scroll < bottom_cap:
                overshoot = bottom_cap-h_scroll
                h_scroll = bottom_cap
                cheney.rect.y -= overshoot
            else:
                cheney.rect.y = BOTTOM_LIM - cheney.rect.height

        #x Controls
        if main_cont.used:
            cheney.move_x(joy_in = main_cont.l_joy_x, deadzone_in = DEFAULT_DEADZONE)              

        else:
            if right_k and not left_k:
                cheney.move_x(dir = 1)
                cheney.dir = 90
                cheney.moving = True

            elif left_k and not right_k:
                cheney.move_x(dir = -1)
                cheney.dir = 270
                cheney.moving = True

            else:
                cheney.move_x(joy_in = 0)
                cheney.moving = False
        cheney.update_x(ground_list)
        
        #Updates x
        if cheney.rect.x < 0:
            cheney.rect.x = 0
            cheney.x_vel = 0
        elif cheney.rect.x + cheney.rect.width > WIDTH:
            cheney.rect.x = WIDTH - cheney.rect.width
            cheney.x_vel = 0
        
        #Checks for checkpoint collision
        #WIN:pygame.display,cheney,ground_list,enemy_list,checkpoints, bullet_list,level_gui,h_scroll,background = None, st_c = 0, pause_gui = None, saveless = False
        draw = (WIN, cheney, ground_list, enemy_list, checkpoints, bullet_list, main_screen, h_scroll, start_color, None, None, saveless)
        _ = cheney.rect.collidelistall(checkpoints)
        if _:
            for i in _:
                if checkpoints[i].active:
                    graphics.draw_window(*draw)
                    if not saveless:
                        sfx.play("check_sound")
                    return "next", bullet_list, cheney, h_scroll, main_cont

        #Checks for death, draws to screen
        try:
            if cheney.rect.y > HEIGHT:
                run = False
                sfx.play("hit_sound")
                return die(draw, cheney, main_cont, clock, deaths, 6), bullet_list, cheney, h_scroll, main_cont
            elif cheney.rect.collidelist(bullet_list) != -1 or cheney.rect.collidelist(enemy_list) != -1:
                    run = False
                    sfx.play("hit_sound")
                    return die(draw, cheney, main_cont, clock, deaths, 6), bullet_list, cheney, h_scroll, main_cont
            else:
                graphics.draw_window(*draw)
        except ValueError:
            pass

        #stop = perf_counter()
        #frame_list.append(int(1/(stop-start)))
        #if len(frame_list)>= 120:
            #print(f"^{max(frame_list)} v{min(frame_list)}")
            #frame_list = []

    pygame.quit()
    return "quit", None, None, None, None
