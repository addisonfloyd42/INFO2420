import pygame, os, colorsys
from pygame import transform as tf
from data.game_classes import *

CHARACTER_IMAGE = tf.scale(pygame.image.load(os.path.join("data","Assets","DickCheney.png")), (150,150))
CHARACTER_IMAGE_JUMP = tf.scale(pygame.image.load(os.path.join("data","Assets","DickCheneyJump.png")), (150,150))
CHARACTER_IMAGE_DIE = tf.flip(tf.scale(pygame.image.load(os.path.join("data","Assets","DickCheneyDie.png")), (150,150)),True,False)

BULLET_COLOR = (148, 12, 12)

def in_window(x, y, rect: pygame.Rect):
    return rect.x + rect.width > 0 and rect.y + rect.height > 0 and rect.x < x and rect.y < y

def draw_window(WIN:pygame.display,cheney,ground_list,enemy_list,checkpoints, bullet_list,level_gui, h_scroll, st_c = 0, background = None, pause_gui = None, saveless = False):
    #background
    hue = 0
    background_color = None
    if background == None:
        hue = st_c + int(h_scroll/15)
        while hue >= 360:
            hue -= 360
        while hue < 0:
            hue += 360
        a = colorsys.hls_to_rgb(hue/360,0.80,0.46)
        background_color = hue
        WIN.fill((a[0]*255,a[1]*255,a[2]*255))
    else:
        WIN.fill(background)
        background_color = colorsys.rgb_to_hls(*background)[0]*360
    #checkpoints
    x, y = WIN.get_size()
    if not saveless:
        for i in checkpoints:
            if in_window(x, y, i.rect):
                if i.active:
                    pygame.draw.rect(WIN,(0, 19, 145),i.rect)
                else:
                    pygame.draw.rect(WIN,(227, 104, 225),i.rect)
    #ground
    x, y = WIN.get_size()
    for i in ground_list:
        if in_window(x, y, i.rect):
            pygame.draw.rect(WIN,(0,0,0),i.rect)
    #bullets
    for i in bullet_list:
        i.rect.x
        pygame.draw.rect(WIN,BULLET_COLOR,i.rect)
    #enemies
    for i in enemy_list:
        if in_window(x, y, i.rect):
            WIN.blit(tf.flip(i.image,i.flip,False),(i.rect.x,i.rect.y))
    #cheney
    chr = CHARACTER_IMAGE
    if not cheney.touching:
        chr = CHARACTER_IMAGE_JUMP
    if cheney.dead == True:
        chr = CHARACTER_IMAGE_DIE
    if cheney.squat:
        chr = tf.scale(chr,(cheney.w,int(cheney.h/2)))
    if cheney.dir == 90:
        WIN.blit(tf.flip(chr,True,False),(cheney.rect.x,cheney.rect.y))
    else:
        WIN.blit(chr,(cheney.rect.x,cheney.rect.y))

    #All GUI

    temp = level_gui.surf_dict
    for i in range(2):
        for key in temp:
            if isinstance(temp[key], Text):
                if temp[key].enabled:
                    color = (0,0,0)
                    if temp[key].color == None:
                        a = colorsys.hls_to_rgb((background_color+250-360*(background_color+180>360))/360,0.40,0.54)
                        color = (a[0]*255,a[1]*255,a[2]*255)
                    else:
                        color = temp[key].color
                    rendered = temp[key].font.render(temp[key].text, True, color)
                    if temp[key].create_fade:
                        rendered.set_alpha(temp[key].fade_obj.trans)
                    else:
                        rendered.set_alpha(temp[key].transparency)
                    WIN.blit(rendered,(temp[key].x,temp[key].y))
            elif isinstance(temp[key],GUIElement):
                if temp[key].color != None:
                    WIN.blit(temp[key].image,(temp[key].x,temp[key].y))
                else:
                    WIN.blit(temp[key].image,(temp[key].x,temp[key].y))
        if pause_gui:
            temp = pause_gui.surf_dict
        else:
            break
    pygame.display.update()
