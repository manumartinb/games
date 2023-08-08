import pygame
import sys
import os
import random

pygame.init()

# Ruta del directorio donde se encuentran las imágenes
img_dir = os.path.join(os.path.dirname(__file__), "C:\\Users\\ManuNewPC\\Desktop\\Script")

# Configuración de la ventana del juego
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Luiso SALVATION")

# Cargar el fondo de pantalla
background_image = pygame.image.load(os.path.join(img_dir, "campo.png"))

# Carga la imagen del personaje
character_image = pygame.image.load(os.path.join(img_dir, "luiso.png"))
character_rect = character_image.get_rect()
character_speed = 5

# Cargar las imágenes "vamosX.png"
vamos_images = [pygame.image.load(os.path.join(img_dir, f"vamos{i}.png")) for i in range(1, 7)]
vamos_rect = vamos_images[0].get_rect()

# Cargar las imágenes de "bomba.png" y "pelota.png"
bomba_image = pygame.image.load(os.path.join(img_dir, "bomba.png"))
pelota_image = pygame.image.load(os.path.join(img_dir, "pelota.png"))
object_images = [bomba_image, pelota_image]

# Configuración de la pelota actual
object_image = random.choice(object_images)
object_rect = object_image.get_rect()
object_speed_x, object_speed_y = 5, 5  # Cambiar la velocidad inicial de la pelota para que comience moviéndose hacia abajo

# Variable para controlar si la pelota está cayendo o subiendo
is_object_falling = True

# Lista de textos aleatorios
random_texts = ["Eso es", "Ahora sí", "Vamos niño"]

# Variables para controlar la aparición de la imagen "vamosX.png"
show_vamos = False
vamos_timer = 0
VAMOS_DURATION = 0.5 * 1000  # 0.5 segundos en milisegundos

def show_random_text(text):
    # Crear una fuente para el texto
    font = pygame.font.SysFont(None, 30)

    # Renderizar el texto en una superficie
    text_surface = font.render(text, True, (255, 255, 255))

    # Obtener el rectángulo del texto
    text_rect = text_surface.get_rect()

    # Posicionar el rectángulo del texto cerca de "luiso"
    text_rect.center = (character_rect.centerx, character_rect.top - 20)

    # Dibujar el texto en la pantalla
    screen.blit(text_surface, text_rect)

def game_loop():
    global character_rect, object_rect, object_speed_x, object_speed_y, is_object_falling, vamos_rect, object_image, show_vamos, vamos_timer

    clock = pygame.time.Clock()

    # Asegurar que "luiso" esté pegado al fondo de la pantalla
    character_rect.y = screen_height - character_rect.height

    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            character_rect.x -= character_speed
        if keys[pygame.K_RIGHT]:
            character_rect.x += character_speed

        # Limitar el rango de movimiento de "luiso" en la parte inferior de la pantalla
        character_rect.x = max(0, min(character_rect.x, screen_width - character_rect.width))

        # Movimiento del objeto (bomba o pelota)
        object_rect.x += object_speed_x
        if is_object_falling:
            object_rect.y += object_speed_y
        else:
            object_rect.y -= object_speed_y

        # Rebotar el objeto en los bordes de la ventana
        if object_rect.left <= 0 or object_rect.right >= screen_width:
            object_speed_x = -object_speed_x

        # Rebotar el objeto en la parte superior de la ventana solo cuando está cayendo
        if object_rect.top <= 0 and is_object_falling:
            is_object_falling = False

        # Verificar si el objeto toca el fondo de la pantalla
        if object_rect.bottom >= screen_height:
            # Si el objeto llega abajo, reiniciar su posición y dirección
            object_image = random.choice(object_images)
            object_rect.x = random.randint(0, screen_width - object_rect.width)
            object_rect.y = 0
            object_speed_y = abs(object_speed_y)
            is_object_falling = True

            # Mostrar una imagen "vamosX.png" aleatoriamente durante 0.5 segundos
            show_vamos = True
            vamos_timer = pygame.time.get_ticks()
            vamos_image = random.choice(vamos_images)

            # Establecer la posición de "vamosX.png" cerca de "luiso"
            vamos_rect.centerx = character_rect.centerx + random.randint(-character_rect.width // 2, character_rect.width // 2)
            vamos_rect.centery = character_rect.centery + random.randint(-character_rect.height // 2, -character_rect.height // 2)

        # Verificar si el tiempo para mostrar "vamosX.png" ha pasado
        if show_vamos and pygame.time.get_ticks() - vamos_timer > VAMOS_DURATION:
            show_vamos = False

        # Limitar el rango de movimiento del objeto
        object_rect.x = max(0, min(object_rect.x, screen_width - object_rect.width))
        object_rect.y = max(0, min(object_rect.y, screen_height - object_rect.height))

        # Verificar colisión con el personaje
        if object_rect.colliderect(character_rect):
            # Mostrar un texto aleatorio cerca de "luiso" cuando ocurre la colisión
            show_random_text(random.choice(random_texts))
            game_over = True  # Terminar el juego si hay colisión

        # Dibujar el fondo de pantalla
        screen.blit(background_image, (0, 0))

        # Dibujar los elementos en la pantalla
        screen.blit(character_image, character_rect)
        screen.blit(object_image, object_rect)

        # Mostrar una imagen "vamosX.png" cerca de "luiso" si es necesario
        if show_vamos:
            screen.blit(vamos_image, vamos_rect)

        pygame.display.flip()
        clock.tick(60)

    # Mostrar mensaje de "GAME OVER" cuando el juego termina
    font = pygame.font.SysFont(None, 50)
    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(game_over_text, game_over_rect)
    pygame.display.flip()

    # Esperar un tiempo antes de salir
    pygame.time.wait(2000)

if __name__ == "__main__":
    game_loop()