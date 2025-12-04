import pygame, psycopg2
import random
from config import config

# ----- БАЗА ДАННЫХ -----

def connect():
    params = config()
    return psycopg2.connect(**params)

def get_user_id(name):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE name = %s", (name,))
    result = cur.fetchone()
    if result:
        user_id = result[0]
    else:
        cur.execute("INSERT INTO users(name) VALUES (%s) RETURNING id", (name,))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.execute("INSERT INTO user_score(user_id, score, level) VALUES (%s, 0, 1)", (user_id,))
        conn.commit()
    cur.close()
    conn.close()
    return user_id

def get_user_state(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT score, level FROM user_score WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result if result else (0, 1)

def save_user_state(user_id, score, level):
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE user_score SET score = %s, level = %s WHERE user_id = %s", (score, level, user_id))
    conn.commit()
    cur.close()
    conn.close()

# ----- НАЧАЛО -----
print("Enter your username:")
name = input()
user_id = get_user_id(name)
score, level = get_user_state(user_id)

# ----- ИГРА -----

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 500, 500
BLOCK_SIZE = 20
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake with PostgreSQL")
clock = pygame.time.Clock()
FPS = 6 + (level - 1) * 4

WHITE = (255, 255, 255)
WHITE_2 = (180, 180, 180)
RED = (200, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 200)
BLACK = (0, 0, 0)

paused = False
time = 0

def draw_grid():
    for i in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        for j in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
            pygame.draw.rect(screen, WHITE_2, (i, j, BLOCK_SIZE, BLOCK_SIZE), 1)

class Wall:
    def __init__(self, level):
        self.body = []
        self.load_wall(level)
    
    def load_wall(self, level):
        try:
            with open(f'level{level}.txt', 'r') as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                for j, ch in enumerate(line):
                    if ch == '#':
                        self.body.append([j, i])
        except:
            self.body = []  # если файл не найден, стена пуста

    def draw(self):
        for x, y in self.body:
            pygame.draw.rect(screen, RED, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

class Food:
    def __init__(self):
        self.generate_random_pos()
    
    def my_round(self, value, base=BLOCK_SIZE):
        return base * round(value / base)
    
    def generate_random_pos(self):
        self.x = self.my_round(random.randint(0, WINDOW_WIDTH - BLOCK_SIZE))
        self.y = self.my_round(random.randint(0, WINDOW_HEIGHT - BLOCK_SIZE))
    
    def respawn(self):
        self.generate_random_pos()
    
    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, BLOCK_SIZE, BLOCK_SIZE))

class Snake:
    def __init__(self):
        self.body = [[10, 10], [11, 10]]
        self.dx = 1
        self.dy = 0

    def draw(self):
        for i, (x, y) in enumerate(self.body):
            color = RED if i == 0 else GREEN
            pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def collide_self(self):
        if self.body[0] in self.body[1:]:
            return True
        return False

    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i] = self.body[i - 1][:]
        self.body[0][0] += self.dx
        self.body[0][1] += self.dy

        # телепортация через стены
        self.body[0][0] %= WINDOW_WIDTH // BLOCK_SIZE
        self.body[0][1] %= WINDOW_HEIGHT // BLOCK_SIZE

snake = Snake()
food = Food()
wall = Wall(level)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_user_state(user_id, score, level)
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_s:
                save_user_state(user_id, score, level)
                print("Game saved.")
            elif not paused:
                if event.key == pygame.K_UP: snake.dx, snake.dy = 0, -1
                elif event.key == pygame.K_DOWN: snake.dx, snake.dy = 0, 1
                elif event.key == pygame.K_LEFT: snake.dx, snake.dy = -1, 0
                elif event.key == pygame.K_RIGHT: snake.dx, snake.dy = 1, 0

    if paused:
        continue

    snake.move()

    if snake.collide_self():
        save_user_state(user_id, score, level)
        break

    # Столкновение со стеной
    for wx, wy in wall.body:
        if snake.body[0][0] == wx and snake.body[0][1] == wy:
            save_user_state(user_id, score, level)
            running = False

    # Еда
    if snake.body[0][0] * BLOCK_SIZE == food.x and snake.body[0][1] * BLOCK_SIZE == food.y:
        snake.body.append([0, 0])
        food.respawn()
        score += random.randint(1, 3)
        if score % 5 == 0 and score != 0:
            level += 1
            FPS += 4
            wall = Wall(level)

    time += 1
    if time % 100 == 0:
        food.respawn()

    screen.fill(WHITE)
    draw_grid()
    wall.draw()
    snake.draw()
    food.draw()

    font = pygame.font.Font(None, 30)
    screen.blit(font.render(f"Score: {score}", True, BLACK), (20, 20))
    screen.blit(font.render(f"Level: {level}", True, BLACK), (380, 20))
    screen.blit(font.render(f"[P] Pause | [S] Save", True, (100, 100, 100)), (120, 470))

    pygame.display.flip()
    clock.tick(FPS)
