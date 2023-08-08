import pygame
import sys

pygame.init()

# Configuración de la ventana del juego
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mi Juego PANG")

# Carga la imagen del personaje
character_image = pygame.image.load("luiso.png")
character_rect = character_image.get_rect()
character_speed = 5

# Configuración de las pelotas
ball_image = pygame.image.load("pelota.png")
ball_rect = ball_image.get_rect()
ball_speed_x, ball_speed_y = 5, 5

# Configuración de las barreras
barrier_image = pygame.image.load("barrera.png")
barrier_rect = barrier_image.get_rect()

def game_loop():
    global character_rect, ball_rect, ball_speed_x, ball_speed_y, barrier_rect

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            character_rect.x -= character_speed
        if keys[pygame.K_RIGHT]:
            character_rect.x += character_speed

        # Movimiento de la pelota
        ball_rect.x += ball_speed_x
        ball_rect.y += ball_speed_y

        # Rebotar la pelota en los bordes de la ventana
        if ball_rect.left <= 0 or ball_rect.right >= screen_width:
            ball_speed_x = -ball_speed_x
        if ball_rect.top <= 0 or ball_rect.bottom >= screen_height:
            ball_speed_y = -ball_speed_y

        # Dibuja los elementos en la pantalla
        screen.fill((255, 255, 255))
        screen.blit(character_image, character_rect)
        screen.blit(ball_image, ball_rect)
        screen.blit(barrier_image, barrier_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    game_loop()
