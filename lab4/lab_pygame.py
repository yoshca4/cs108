import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CS 108 Pygame")

clock = pygame.time.Clock()
FPS   = 60

# at the top of the file, outside the while loop:
x, y   = 400, 300
vx, vy = 3, 3

while True:
    # 1. Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 2. Update state
    # inside the loop, in Update state:
    x += vx
    y += vy

    # bounce off walls
    if x <= 0 or x >= WIDTH:
        vx = -vx
    if y <= 0 or y >= HEIGHT:
        vy = -vy

    # 3. Draw
    screen.fill((30, 30, 46))
    pygame.draw.circle(screen, (137, 180, 250), (int(x), int(y)), 30)
    
    pygame.display.flip()           # push frame to screen
    clock.tick(FPS)                 # cap at 60 FPS