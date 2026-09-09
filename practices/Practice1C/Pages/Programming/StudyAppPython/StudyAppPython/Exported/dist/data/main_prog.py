import pygame, os, time, colorsys
from math import atan, cos, sin, sqrt
from pygame import transform as tf
import data.graphics as graphics
from time import perf_counter
from random import randint

class GUI:
    surf_dict = {}
    def add_to_dict(self, name, value):
        self.surf_dict[name] = value

class ControlGUI:
    def __init__(self,cont_or_wasd):
        w, h = 75, 75
        self.wasd = tf.scale(pygame.image.load(os.path.join("data","Assets","WASD.png")), (w,h))
        self.control = tf.scale(pygame.image.load(os.path.join("data","Assets","Controller.png")), (w,h))
        self.x, self.y = 0, 0
        self.transparency = 255/2
        self.type = "image"
        if cont_or_wasd == "cont":
            self.image = self.control
        else:
            self.image = self.wasd
        self.image.set_alpha(self.transparency)

class Text:
    def __init__(self, font: pygame.font, x, y, text, width, height, transparency, enabled, color = None, create_fade:bool = False, fade_start: int = 0):
        self.font = font
        self.text = text
        self.color = color
        self.tick = 0
        self.type = "text"
        self.transparency = transparency
        self.create_fade = create_fade
        if create_fade:
            self.fade_obj = FadeTransition(transparency, fade_start)
        else:
            self.fade_obj = None
        self.enabled = enabled
        w, h = self.font.size(text)
        if isinstance(x,str):
            if x.lower() == "l":
                self.x = 0
            elif x.lower() == "r":
                self.x = width - w
            else:
                raise Exception("x-value must be either integer or string with 'l' or 'r'")
        else:
            self.x = x

        if isinstance(y,str):
            if y.lower() == "t":
                self.y = 0
            elif y.lower() == "b":
                self.y = height - h
            else:
                raise Exception("y-value must be either integer or string with 't' or 'b'")
        else:
            self.y = y

class FadeTransition:
    def __init__(self, max_trans:int = 255, fade_start:int = 0, surface = None):
        self.surface = surface
        self.max_trans = max_trans
        self.trans = fade_start
        self.speed = None

    def update_fade(self):
        if self.speed:
            self.trans += self.speed
            if self.speed < 0 and self.trans <= 0:
                self.speed = None
                self.trans = 0
            elif self.speed > 0 and self.trans >= self.max_trans:
                self.speed = None
                self.trans = self.max_trans

    def fade_in(self,speed):
        if self.speed != None:
            return False
        else:
            self.speed = speed
            return True

    def fade_out(self,speed):
        if self.speed != None:
            return False
        else:
            self.speed = -speed
            return True

class Controller:
    def __init__(self):
        self.used = False
        self.a = False
        self.b = False
        self.x = False
        self.y = False
        self.l_joy_x = 0
        self.l_joy_y = 0
        self.r_joy_x = 0
        self.r_joy_y = 0
        
class Char:
    """Class for the Main Character."""
    def __init__(self, x, y, w, h, g, x_decel, x_accel, speed, dir):
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)
        self.g = g
        self.x_decel = x_decel
        self.x_accel = x_accel
        self.speed = speed
        self.dir = dir
        self.x_vel = 1
        self.y_vel = 1
        self.half_height, self.half_width = h/2, w/2
        self.touching = False
        self.moving = False
        self.squat = False
        self.dead = False
    
    def update_x(self,ground_list):
        self.rect.x += self.x_vel
        if not self.moving:
            self.x_vel = self.x_vel * self.x_decel
        if self.rect.collidelist(ground_list) != -1:
            while not self.rect.collidelist(ground_list) == -1:
                try:
                    self.rect.x += int(self.x_vel/abs(self.x_vel))*-1
                except ZeroDivisionError:
                    break
            self.x_vel = 0
        if abs(self.x_vel)< 0.25:
            self.x_vel = 0

    def update_y(self,ground_list):
        if not self.y_vel:
            self.y_vel = 1
            self.touching = False
        self.rect.y += self.y_vel
        if self.rect.collidelist(ground_list) != -1:
            if self.y_vel > 0:
                self.touching = True
            while not self.rect.collidelist(ground_list) == -1:
                try:
                    self.rect.y += int(self.y_vel/abs(self.y_vel))*-1
                except ZeroDivisionError:
                    break
            self.y_vel = 0
        if self.touching:
            self.y_vel = 0
        else:
            self.y_vel += self.g

    def jump(self,init_vel):
        if self.touching:
            self.y_vel = init_vel
            self.touching = False

    def move_x(self,dir, joy_in = 1):
        if self.squat and self.touching:
            _speed = self.speed*0.6*abs(joy_in)
        else:
            _speed = self.speed*abs(joy_in)
        if (self.x_vel < _speed and dir == 1) or (self.x_vel > -1*_speed and dir == -1):
            self.x_vel += self.x_accel*dir
        else:
            self.x_vel = _speed*dir

class GroundBlock:
    """Class for all ground blocks."""
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.init_x = x
        self.init_y = y

class Checkpoint:
    """Class for checkpoints."""
    def __init__(self, x, y, w, h, active):
        self.rect = pygame.Rect(x, y, w, h)
        self.init_x = x
        self.init_y = y
        self.active = active

class Obama:
    """Class for all Obama enemies."""
    def __init__(self, x, y, w, h, dir:int, bullet_end, tick_cap, win_width, win_height):
        self.rect = pygame.Rect(x,y,w,h)
        self.init_x = x
        self.init_y = y
        self.dir = dir
        self.bullet_end = bullet_end
        self.tick_cap = tick_cap
        self.win_width,self.win_height = win_width, win_height
        self.tick = 0
        self.flip = False
        if dir == 90:
            self.image = tf.scale(pygame.image.load(os.path.join("data","Assets","OBAMA.png")), (w,h))
        else:
            self.image = tf.flip(tf.scale(pygame.image.load(os.path.join("data","Assets","OBAMA.png")), (w,h)),flip_x = True, flip_y = False)
           
    def fire_bullet(self, bullet_list):
        bullet_list.append(Bullet((self.init_x+(self.rect.w/2)),(self.init_y+(self.rect.h/2)),75,20,(90 + (self.dir == 270)*180),self.bullet_end))

    def should_fire(self):
        return graphics.in_window(self.win_width,self.win_height,self.rect)
        
class Jeb:
    """Class for all Jeb enemies."""
    def __init__(self, x, y, w, h, dir:int, bullet_end, tick_cap, win_width, win_height, load_interval: tuple = None):
        self.rect = pygame.Rect(x,y,w,h)
        self.init_x = x
        self.init_y = y
        self.dir = dir
        self.bullet_end = bullet_end
        self.tick_cap = tick_cap
        self.flip = False
        self.win_width,self.win_height = win_width, win_height
        if load_interval == None:
            if self.dir == 0:
                self.load_interval = (-h,self.win_height+bullet_end)
            else:
                self.load_interval = (-h - bullet_end,self.win_height)#(,HEIGHT+)
        else:
            self.load_interval = load_interval
            if load_interval[0] <= load_interval[1] or len(load_interval) != 2:
                raise Exception("load_interval must contain two items, the first being larger than the second.")
        self.tick = 0
        if dir == 0:
            self.image = tf.scale(pygame.image.load(os.path.join("data","Assets","Jeb.png")), (w,h))
        else:
            self.image = tf.flip(tf.scale(pygame.image.load(os.path.join("data","Assets","Jeb.png")), (w,h)),False, True)
           
    def fire_bullet(self, bullet_list):
        bullet_list.append(Bullet((self.init_x+(self.rect.w/2)),(self.init_y+(self.rect.h/2)),20,75,(self.dir == 180)*180,self.bullet_end))

    def should_fire(self):
        return self.load_interval[0] <= self.rect.x <= self.load_interval[1]

class OJ:
    def __init__(self, x, y, w, h, dir, lims:tuple, speed):
        self.rect = pygame.Rect(x,y,w,h)
        self.init_x = x
        self.init_y = y
        self.dir = dir
        self.speed = speed
        if len(lims) != 2:
            raise Exception("lims must contain two values")
        self.lims = lims
        self.flip = False
        self.image = None
        self.image_up = tf.scale(pygame.image.load(os.path.join("data","Assets","OJUp.png")), (w,h))
        self.image_down = tf.scale(pygame.image.load(os.path.join("data","Assets","OJDown.png")), (w,h))

class Clinton:
    def __init__(self,x, y, w, h):
        self.init_x, self.init_y = x, y
        self.first_x, self.first_y = x, y
        self.half_width, self.half_height = self.w/2, self.hs/2
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.image.load(os.path.join("data","Assets","BillClinton.png"))
        self.dir = None
        self.flip = None

    def update_pos(self, cheney:Char, speed:int):
        if sqrt(pow(cheney.rect.x-self.init_x,2)+pow(cheney.rect.y-self.init_y,2)) > 500:
            return
        self.dir = atan((cheney.rect.y-self.init_y)/(cheney.rect.x-self.init_x))
        if 0 <= self.dir <= 180:
            self.flip = True
        else:
            self.flip = False
        self.init_x += speed * cos(dir)
        self.init_y += speed * sin(dir)



class Bullet:
    """Class for any bullets."""
    def __init__(self, x, y, w, h, dir, end):
        self.rect = pygame.Rect(x,y,w,h)
        self.init_x = x
        self.init_y = y
        self.dir = dir
        self.end = end
        self.dist = 0

def die(args: list, cheney: Char):
    """Runs when the character dies."""
    cheney.dead = True
    graphics.draw_window(*args[:-2], background = (220,30,50))
    time.sleep(0.5)
    return "die"

def update_h(h_scroll, *args):
    """Updates scroll height for given lists, assuming they're global."""
    for arg in args:
        for i in arg:
            i.rect.y = i.init_y + h_scroll

FPS_CAP = 60

def level_run(WIN: pygame.display, cheney:Char, ground_list, enemy_list, checkpoints, bullet_list, h_scroll, main_cont, level):
    WIDTH, HEIGHT = WIN.get_size()
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("arialblack", 120)
    #['arial', 'arialblack', 'bahnschrift', 'calibri', 'cambria', 'cambriamath', 'candara', 'comicsansms', 'consolas', 'constantia', 'corbel', 'couriernew', 'ebrima', 'franklingothicmedium', 'gabriola', 'gadugi', 'georgia', 'holomdl2assets', 'impact', 'inkfree', 'javanesetext', 'leelawadeeui', 'leelawadeeuisemilight', 'lucidaconsole', 'lucidasans', 'malgungothic', 'malgungothicsemilight', 'microsofthimalaya', 'microsoftjhenghei', 'microsoftjhengheiui', 'microsoftnewtailue', 'microsoftphagspa', 'microsoftsansserif', 'microsofttaile', 'microsoftyahei', 'microsoftyaheiui', 'microsoftyibaiti', 'mingliuextb', 'pmingliuextb', 'mingliuhkscsextb', 'mongolianbaiti', 'msgothic', 'msuigothic', 'mspgothic', 'mvboli', 'myanmartext', 'nirmalaui', 'nirmalauisemilight', 'palatinolinotype', 'segoemdl2assets', 'segoeprint', 'segoescript', 'segoeui', 'segoeuiblack', 'segoeuiemoji', 'segoeuihistoric', 'segoeuisemibold', 'segoeuisemilight', 'segoeuisymbol', 'simsun', 'nsimsun', 'simsunextb', 'sitkasmall', 'sitkatext', 'sitkasubheading', 'sitkaheading', 'sitkadisplay', 'sitkabanner', 'sylfaen', 'symbol', 'tahoma', 'timesnewroman', 'trebuchetms', 'verdana', 'webdings', 'wingdings', 'yugothic', 'yugothicuisemibold', 'yugothicui', 'yugothicmedium', 'yugothicuiregular', 'yugothicregular', 'yugothicuisemilight']    
    start_color = randint(0,359)

    level_gui = GUI()

    level_gui.add_to_dict("level_text",Text(font, "r", "b", f"LEVEL {str(level + 1)}", WIDTH, HEIGHT, 120, True, None, True, 0))
    if main_cont.used:
        level_gui.add_to_dict("cont_icon",ControlGUI("cont"))
    else:
        level_gui.add_to_dict("cont_icon",ControlGUI("wasd"))

    clock = pygame.time.Clock()

    run = True

    TOP_LIM = 400
    BOTTOM_LIM = 600

    top_cap = 20000
    bottom_cap = h_scroll

    BULLET_VEL = 20
    
    frame_list = []
    
    cont_image = ControlGUI("wasd")
    while run:
        #start = perf_counter()
        clock.tick(FPS_CAP)
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                if event.axis == 0:
                    main_cont.l_joy_x = event.value
                elif event.axis == 1:
                    main_cont.l_joy_y = event.value
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    main_cont.a = True
            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    main_cont.a = False
            if event.type == pygame.JOYHATMOTION:
                print(event)
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
        
        #text update
        for key in level_gui.surf_dict:
            if isinstance(level_gui.surf_dict[key], Text):
                if level_gui.surf_dict[key].create_fade and level_gui.surf_dict[key].enabled:
                    if level_gui.surf_dict[key].tick == 0:
                        level_gui.surf_dict[key].fade_obj.fade_in(2)
                    elif level_gui.surf_dict[key].tick == 250:
                        level_gui.surf_dict[key].fade_obj.fade_out(2)
                        if level_gui.surf_dict[key].fade_obj.speed == None:
                            level_gui.surf_dict[key].enabled = False
                    level_gui.surf_dict[key].fade_obj.update_fade()
                    level_gui.surf_dict[key].tick += 1
        #enemy update
        for i in enemy_list:
            if isinstance(i,Obama) or isinstance(i,Jeb):
                if i.should_fire():
                    i.tick -= 1
                    if i.tick < 1:
                        i.tick = i.tick_cap
                        i.fire_bullet(bullet_list)
            if isinstance(i,OJ):
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





        update_h(h_scroll, ground_list,enemy_list,bullet_list, checkpoints) #Updates scroll

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
            cheney.jump(-35)

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
            if cheney.squat:
                deadzone = 0.3
            else:
                deadzone = 0.2
            if main_cont.l_joy_x > deadzone:
                cheney.move_x(1, main_cont.l_joy_x)
                cheney.dir = 90
                cheney.moving = True
            elif main_cont.l_joy_x < -deadzone:
                cheney.move_x(-1, main_cont.l_joy_x)
                cheney.dir = 270
                cheney.moving = True

            else:
                cheney.moving = False


        else:
            if right_k and not left_k:
                cheney.move_x(1)
                cheney.dir = 90
                cheney.moving = True

            elif left_k and not right_k:
                cheney.move_x(-1)
                cheney.dir = 270
                cheney.moving = True

            else:
                cheney.moving = False
        cheney.update_x(ground_list)
        
        #Updates x
        if cheney.rect.x < 0:
            cheney.rect.x = 0
        elif cheney.rect.x + cheney.rect.width > WIDTH:
            cheney.rect.x = WIDTH - cheney.rect.width
        
        #Checks for checkpoint collision

        draw = (WIN,cheney,ground_list,enemy_list,checkpoints, bullet_list,level_gui,h_scroll, None, start_color)

        _ = cheney.rect.collidelistall(checkpoints)
        if _:
            for i in _:
                if checkpoints[i].active:
                    graphics.draw_window(*draw)
                    return "next", bullet_list, cheney, h_scroll, main_cont

        #Checks for death, draws to screen
        try:
            if cheney.rect.y > HEIGHT:
                run = False
                return die(draw, cheney), bullet_list, cheney, h_scroll, main_cont
            elif cheney.rect.collidelist(bullet_list) != -1 or cheney.rect.collidelist(enemy_list) != -1:
                    run = False
                    return die(draw, cheney), bullet_list, cheney, h_scroll, main_cont
            else:
                graphics.draw_window(*draw)
        except ValueError:
            pass

        #stop = perf_counter()
        #frame_list.append(int(1/(stop-start)))
        #if len(frame_list)>= 120:
         #   print(f"^{max(frame_list)} v{min(frame_list)}")
          #  frame_list = []

    pygame.quit()
    return "quit", None, None, None, None
