import pygame
from sys import exit

pygame.init()

screen = pygame.display.set_mode((800, 600))
screen.fill('white')
clock = pygame.time.Clock()

test_surface = pygame.image.load('photo.jpg').convert_alpha()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    screen.blit(test_surface, (0,0))
    pygame.display.update()
    clock.tick(60)