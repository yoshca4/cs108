import pygame
import sys

pygame.init()

import random, math

class Particle:
    def __init__(self, x, y):
        angle  = random.uniform(0, 2 * math.pi)
        speed  = random.uniform(1, 4)
        self.x  = x
        self.y  = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life     = 1.0               # 1.0 = fully alive
        self.decay    = random.uniform(0.01, 0.03)
        self.radius   = random.randint(3, 8)
        self.color    = (
            random.randint(150, 255),
            random.randint(50,  150),
            random.randint(200, 255),
        )

    def update(self):
        self.x    += self.vx
        self.y    += self.vy
        self.vy   += 0.05          # gravity
        self.life -= self.decay

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha  = int(self.life * 255)
        radius = int(self.radius * self.life)
        color  = (
            int(self.color[0] * self.life),
            int(self.color[1] * self.life),
            int(self.color[2] * self.life),
        )
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), max(1, radius))

    def is_dead(self):
        return self.life <= 0

particles = []

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CS 108 Pygame")

clock = pygame.time.Clock()
FPS   = 60

# at the top of the file, outside the while loop:
x, y   = 400, 300
vx, vy = 3, 2

while True:
    # 1. Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    # "# 1. Handle events", replace the event-based spawn, with:
    if pygame.mouse.get_pressed()[0]:
        for _ in range(5):
            particles.append(Particle(mx, my))

    # 2. Update state
    # inside the loop, in Update state:
    keys = pygame.key.get_pressed()
    SPEED = 4

    if keys[pygame.K_LEFT]:  x -= SPEED
    if keys[pygame.K_RIGHT]: x += SPEED
    if keys[pygame.K_UP]:    y -= SPEED
    if keys[pygame.K_DOWN]:  y += SPEED

    mx, my = pygame.mouse.get_pos()
    pressed = pygame.mouse.get_pressed()
    
    for p in particles:
        p.update()
    particles = [p for p in particles if not p.is_dead()]

    # 3. Draw
    screen.fill((30, 30, 46))
    pygame.draw.circle(screen, (137, 180, 250), (int(x), int(y)), 30)
    pygame.draw.circle(screen, (166, 227, 161), (mx, my), 15)
    for p in particles:
        p.draw(screen)
    
    pygame.display.flip()           # push frame to screen
    clock.tick(FPS)                 # cap at 60 FPS
