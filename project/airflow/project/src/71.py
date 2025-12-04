import pygame
import os

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Move & Toggle Color + Image")
clock = pygame.time.Clock()

# Переменные
done = False
is_blue = True
x = 30
y = 30

# Кэш изображений
_image_library = {}

def get_image(path):
    global _image_library
    image = _image_library.get(path)
    if image is None:
        canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep).lower()
        try:
            image = pygame.image.load(canonicalized_path).convert_alpha()
            print("Image loaded:", canonicalized_path, image.get_size())
        except pygame.error as e:
            print(f"Failed to load image {canonicalized_path}: {e}")
            image = pygame.Surface((50, 50))
            image.fill((200, 0, 0))  # Заглушка, если файл не найден
        _image_library[path] = image
    return image

# Главный игровой цикл
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                is_blue = not is_blue

    # Движение прямоугольника
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP]: y -= 3
    if pressed[pygame.K_DOWN]: y += 3
    if pressed[pygame.K_LEFT]: x -= 3
    if pressed[pygame.K_RIGHT]: x += 3

    # Очистка экрана
    screen.fill((255, 255, 255))

    # Рисуем изображение
    screen.blit(get_image('ball.png'), (20, 20))

    # Цветной прямоугольник
    color = (0, 128, 255) if is_blue else (255, 100, 0)
    pygame.draw.rect(screen, color, pygame.Rect(x, y, 60, 60))

    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

pygame.quit()