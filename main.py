import pygame
from messages import *
from math import atan2, sin, cos
from typing import Optional
from random import randint, choice
# noinspection PyUnresolvedReferences,PyProtectedMember
from pygame._sdl2 import Window

pygame.init()

WIDTH, HEIGHT = 1280, 720
FRAMERATE = 75

screen = pygame.display.set_mode([WIDTH, HEIGHT])
clock = pygame.time.Clock()
pygame.display.set_caption("Overused mechanic 1hgj")
font = pygame.font.SysFont("Arial", 30)

message_index = -1
message_surf: Optional[pygame.Surface] = None
text_direction = [1, 1]
text_speed = 4
wobble = 0
do_shake = False


def next_message():
    global message_surf
    global message_index
    global running
    global do_letter_spam
    global do_shake
    message_index += 1
    try:
        modifier = list(MESSAGES.values())[message_index]
        if modifier == 1:
            do_letter_spam = True
        if modifier == 2:
            do_shake = True
        if modifier == 3:
            do_shake = False
        message_surf = font.render(list(MESSAGES.keys())[message_index], True, (255, 255, 255))
    except IndexError:
        running = False


def text_wobble(direction=1):
    # direction 1 = squish flat, direction 0 = squish wall
    global wobble
    wobble = 20*(direction*2-1)


text_center = [WIDTH / 2, HEIGHT / 2]
letter_surfs = {}

qwertyuiop = "qwertyuiopasdfghjklzxcvbnm"
for letter in qwertyuiop:
    letter_surfs[letter] = font.render(letter, True, choice([
        (104, 216, 214), (156, 234, 239), (61, 204, 199), (7, 190, 184), (196, 255, 249)
    ]))

letter_spam = []
do_letter_spam = False
letter_index = 0
screen_offset = [None, None]

next_message()
running = True
while running:
    mx, my = pygame.mouse.get_pos()
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            next_message()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                angle = atan2(text_center[1] - my, text_center[0] - mx)
                text_direction = [-cos(angle), -sin(angle)]
                text_speed = randint(3, 8)
                text_wobble()

    if do_shake:
        pgwindow = Window.from_display_module()
        ticky = pygame.time.get_ticks()/100
        if screen_offset[0] is None:
            screen_offset = [pgwindow.position[0], pgwindow.position[1]]
        screen_offset[0] += cos(ticky)*7
        screen_offset[1] += sin(ticky)*7
        pgwindow.position = screen_offset[0], screen_offset[1]

    # letter spam
    if pygame.time.get_ticks() % int(FRAMERATE/7) == 0 and do_letter_spam:
        randangle = randint(0, 300)
        letter_spam.append([qwertyuiop[letter_index], [WIDTH/2, HEIGHT/2], [sin(randangle), cos(randangle)]])
        letter_index += 1
        if letter_index >= len(qwertyuiop):
            letter_index = 0

    for letter_info in letter_spam:
        screen.blit(letter_surfs[letter_info[0]], letter_info[1])
        letter_info[1][0] += 3*letter_info[2][0]
        letter_info[1][1] += 3*letter_info[2][1]
        lpos = letter_info[1]
        if lpos[0] > WIDTH:
            letter_info[2][0] = -1*abs(letter_info[2][0])
        if lpos[1] > HEIGHT:
            letter_info[2][1] = -1*abs(letter_info[2][1])
        if lpos[0] < 0:
            letter_info[2][0] = 1*abs(letter_info[2][0])
        if lpos[1] < 0:
            letter_info[2][1] = 1*abs(letter_info[2][1])

    if len(letter_spam) > 150:
        letter_spam.pop(0)

    # message text
    surf_rect = message_surf.get_rect(center=text_center)
    if surf_rect.bottom > HEIGHT:
        text_direction[1] = -1 * abs(text_direction[1])
        text_wobble()
    if surf_rect.right > WIDTH:
        text_direction[0] = -1 * abs(text_direction[0])
        text_wobble(0)
    if surf_rect.left < 0:
        text_direction[0] = 1 * abs(text_direction[0])
        text_wobble(0)
    if surf_rect.top < 0:
        text_direction[1] = 1 * abs(text_direction[1])
        text_wobble()
    text_center[0] += text_speed * text_direction[0]
    text_center[1] += text_speed * text_direction[1]

    new_surf = message_surf
    if wobble != 0:
        wobble -= wobble/abs(wobble)/2
        new_surf = pygame.transform.scale(
            new_surf,
            [
                int(new_surf.get_width()+wobble),
                int(new_surf.get_height()-wobble)
            ]
        )
        new_surf = pygame.transform.rotate(new_surf, sin(pygame.time.get_ticks()/60)*wobble/7)
    screen.blit(new_surf, new_surf.get_rect(center=text_center))

    pygame.display.flip()
    clock.tick(FRAMERATE)
pygame.quit()
