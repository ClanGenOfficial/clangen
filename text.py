import pygame
import sys
from pygame.locals import *

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Define the font
FONT = pygame.font.Font(None, 32)

# The text to display
text = "This is the text to be typed out"

# This list will hold each 'frame' of the text, i.e., it will start with the first character of the text, 
# then the first two, first three, and so on until it includes the entire text
text_frames = [text[:i+1] for i in range(len(text))]

clock = pygame.time.Clock()

frame_index = 0
# The delay in milliseconds between when each new character is added
typing_delay = 200
# Time when the next character should be added
next_frame_time = pygame.time.get_ticks() + typing_delay

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))

    now = pygame.time.get_ticks()
    if now >= next_frame_time and frame_index < len(text_frames):
        frame_index += 1
        next_frame_time += typing_delay

    if frame_index < len(text_frames):
        frame = FONT.render(text_frames[frame_index], True, (255, 255, 255))
        screen.blit(frame, (50, 50))

    pygame.display.update()
    clock.tick(60)