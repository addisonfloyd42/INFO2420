from math import atan2, cos, sin, hypot, floor
import pygame, os, colorsys
from pygame import transform as tf
import data.graphics as graphics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR)
ASSETS_DIR = os.path.join(DATA_DIR, "Assets")

class GUI:
    def __init__(self, *args):
        self.surf_dict = {}
        self.max_button = -1
        for i in args:
           self.add_to_dict(i[0],i[1])
    def add_to_dict(self, name, value):
        self.surf_dict[name] = value
        if isinstance(value, Text):
            self.max_button += 1

class GUIElement:
    def __init__(self, x, y, w, h, image = None, transparency = 255, color = None):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.color = color
        self.transparency = transparency
        if image:
            self.image = image
            self.image.set_alpha(self.transparency)
        elif color:
            self.image = pygame.Surface((w, h))
            self.image.fill(color)
            self.image.set_alpha(self.transparency)

class Sound:
    def __init__(self, path, start_vol, channel = None):
        self.channel = channel
        self.sound = pygame.mixer.Sound(path)
        self.sound.set_volume(start_vol)
        self.start_vol = start_vol
        self.channel = channel

    def set_volume(self, vol):
        self.sound.set_volume(vol * self.start_vol)

    def play(self):
        if self.channel:
            self.channel.play(self.sound)
        else:
            self.sound.play()

class SoundGroup:
    def __init__(self, **kwargs):
        self.sound_dict = {}
        for key, value in kwargs.items():
            self.sound_dict[key] = value
    def add(**kwargs):
        for key, value in kwargs.items():
            self.sound_dict[key] = value
    def set_vol(self, vol):
        for i in self.sound_dict:
            self.sound_dict[i].set_volume(vol)
    def play(self, key):
        self.sound_dict[key].play()

class Text:
    def __init__(self, font: pygame.font, x, y, text, width, height, transparency, enabled, color = None, create_fade:bool = False, fade_start: int = 0):
        self.font = font
        self.text = text
        self.color = color
        self.tick = 0
        self.type = "text"
        self.transparency = transparency
        self.create_fade = create_fade
        self._left_or = False
        self._width = width
        if create_fade:
            self.fade_obj = FadeTransition(transparency, fade_start)
        else:
            self.fade_obj = None
        self.enabled = enabled
        self.w, self.h = self.font.size(text)
        if isinstance(x,str):
            if x.lower() == "l":
                self.x = 0
            elif x.lower() == "r":
                self.x = width - self.w
                self._left_or = True
            else:
                raise Exception("x-value must be either integer or string with 'l' or 'r'")
        else:
            self.x = x

        if isinstance(y,str):
            if y.lower() == "t":
                self.y = 0
            elif y.lower() == "b":
                self.y = height - self.h
            else:
                raise Exception("y-value must be either integer or string with 't' or 'b'")
        else:
            self.y = y

    def change_text(self,text):
        self.text = text
        self.w, self.h = self.font.size(text)
        self.x = self._width - self.w

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
    def __init__(self, index):
        self.index = index
        self.used = False
        self.a = False
        self.b = False
        self.x = False
        self.y = False
        self.l_joy_x = 0
        self.l_joy_y = 0
        self.r_joy_x = 0
        self.r_joy_y = 0

    def __str__(self):
        return f"a: {self.a}, b: {self.b}, x: {self.x}, y: {self.y}"
        
class Char:
    """Class for the Main Character."""
    def __init__(self, x, y, w, h, g, reg_accel, squat_accel,deccel, speed, dir):
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)
        self.g = g
        self.reg_accel = reg_accel
        self.squat_accel = squat_accel
        self.deccel = deccel
        self.speed = speed
        self.dir = dir
        self.x_vel = 1
        self.y_vel = 1
        self.half_height, self.half_width = h/2, w/2
        self.touching = False
        self.moving = False
        self.squat = False
        self.dead = False
        self.accel = self.reg_accel
    
    def update_x(self,ground_list):
        self.x_vel = self.x_vel * self.deccel
        self.x_vel += self.accel
        self.rect.x += self.x_vel
        if abs(self.x_vel) > self.speed:
            if self.x_vel > 0:
                self.x_vel = self.speed
            else:
                self.x_vel = -self.speed
        if self.rect.collidelist(ground_list) != -1:
            while not self.rect.collidelist(ground_list) == -1:
                try:
                    self.rect.x += int(self.x_vel/abs(self.x_vel))*-1
                except ZeroDivisionError:
                    break
            self.x_vel = 0
        self.x_vel = int(self.x_vel*10)/10

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
        self.y_vel = init_vel
        self.touching = False

    def move_x(self, dir = 1, joy_in = 1, deadzone_in = 0):
        accel_mod = 0
        if self.squat:
            accel_mod = self.squat_accel
            deadzone_in = deadzone_in * 1.1
        else:
            accel_mod = self.reg_accel
        if abs(joy_in)<deadzone_in:
            self.accel = 0
            self.moving = False
        else:
            if abs(joy_in) > deadzone_in*1.3:
                self.dir = 90 + 180 * ((dir < 0) or (joy_in < 0))
            self.accel = joy_in * accel_mod * dir
            self.moving = True

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
            self.image = tf.scale(pygame.image.load(os.path.join(ASSETS_DIR,"Obama.png")), (w,h))
        else:
            self.image = tf.flip(tf.scale(pygame.image.load(os.path.join(ASSETS_DIR,"Obama.png")), (w,h)),flip_x = True, flip_y = False)
           
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
            self.image = tf.scale(pygame.image.load(os.path.join(ASSETS_DIR,"Jeb.png")), (w,h))
        else:
            self.image = tf.flip(tf.scale(pygame.image.load(os.path.join(ASSETS_DIR,"Jeb.png")), (w,h)),False, True)
           
    def fire_bullet(self, bullet_list):
        bullet_list.append(Bullet((self.init_x+(self.rect.w/2)),(self.init_y+(self.rect.h/2)),20,75,(self.dir == 180)*180,self.bullet_end))

    def should_fire(self):
        return self.load_interval[0] <= self.rect.x <= self.load_interval[1]

class OJ:
    def __init__(self, x, y, w, h, dir, lims:tuple, speed):
        self.rect = pygame.Rect(x,y,w,h)
        self.init_x, self.first_x = x,x
        self.init_y, self.first_y = y,y

        self.dir = dir
        self.speed = speed
        if len(lims) != 2:
            raise Exception("lims must contain two values")
        self.lims = lims
        self.flip = False
        self.image_up = tf.scale(pygame.image.load(os.path.join(ASSETS_DIR,"OJUp.png")), (w,h))
        self.image_down = tf.scale(pygame.image.load(os.path.join(ASSETS_DIR,"OJDown.png")), (w,h))
        self.image = self.image_down

class Clinton:
    def __init__(self,x, y, w, h, speed, trans, max_dist):
        self.init_x, self.init_y = x, y
        self.first_x, self.first_y = x, y
        self.first_y_transl = y
        self.rect = pygame.Rect(x, y, w, h)
        self.speed = speed
        self.trans = trans
        self.max_dist = max_dist
        self.image = tf.scale(pygame.image.load(os.path.join(ASSETS_DIR,"BillClinton.png")),(w,h))
        self.image.set_alpha(trans)
        self.dir = None
        self.flip = False

    def update_pos(self, cheney:Char, speed:int):
        #dist(zip(cheney.rect.x, cheney.rect.y),zip())
        if not (cheney.rect.y > self.first_y_transl + self.max_dist  or cheney.rect.y + cheney.rect.w < self.first_y_transl - self.max_dist):
            if hypot(cheney.rect.x - self.first_x, cheney.rect.y - self.first_y_transl) > self.max_dist:
                self.image.set_alpha(self.trans*0.5)
                return
            self.image.set_alpha(self.trans)
            if cheney.rect.x-self.rect.x == 0:
                self.dir = 180*(self.rect.y < cheney.rect.y)
            else:
                self.dir = int((atan2(cheney.rect.y-self.rect.y,cheney.rect.x-self.rect.x)+1.5708) * 57.324 )
            if self.dir<0:
                self.dir += 360
            if 0 <= self.dir <= 180:
                self.flip = True
            else:
                self.flip = False
            self.init_x += speed * sin(self.dir*0.01745)
            self.init_y -= speed * cos(self.dir*0.01745)
            self.rect.x = self.init_x
        else:
            self.image.set_alpha(self.trans*0.5)

class Bernie:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x,y,w,h)
        self.init_x, self.init_y = x, y
        self.image = self.image = tf.scale(pygame.image.load(os.path.join(ASSETS_DIR,"Bern.png")),(w,h))
        self.flip = False

class Bullet:
    """Class for any bullets."""
    def __init__(self, x, y, w, h, dir, end):
        self.rect = pygame.Rect(x,y,w,h)
        self.init_x = x
        self.init_y = y
        self.dir = dir
        self.end = end
        self.dist = 0
