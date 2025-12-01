import cv2
import mediapipe as mp
import pygame
import numpy as np
import sys
import time

# ------------------- CONFIG -------------------
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 15
BALL_RADIUS = 10
BALL_SPEED = 5
BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_WIDTH = WIDTH // BRICK_COLS
BRICK_HEIGHT = 30
SMOOTHING = 0.7  

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
BRICK_COLOR = (255, 165, 0)

# ------------------- PYGAME INIT -------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DX-Ball Hand Gesture Control")
clock = pygame.time.Clock()

# ------------------- MEDIAPIPE INIT -------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

# ------------------- GAME VARIABLES -------------------
paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
paddle_y = HEIGHT - 50
prev_paddle_x = paddle_x

ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_vel_x = BALL_SPEED
ball_vel_y = -BALL_SPEED

# Generate bricks
bricks = []
for row in range(BRICK_ROWS):
    for col in range(BRICK_COLS):
        bricks.append(pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT, BRICK_WIDTH-2, BRICK_HEIGHT-2))

lives = 10
score = 0

# ------------------- HELPER FUNCTIONS -------------------
def draw():
    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, (paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.circle(screen, RED, (int(ball_x), int(ball_y)), BALL_RADIUS)
    for brick in bricks:
        pygame.draw.rect(screen, BRICK_COLOR, brick)
    font = pygame.font.SysFont(None, 30)
    score_text = font.render(f"Score: {score}  Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, HEIGHT - 30))
    pygame.display.update()

def detect_hand():
    global prev_paddle_x, paddle_x
    ret, frame = cap.read()
    if not ret:
        return
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        x_norm = hand_landmarks.landmark[8].x
        target_x = int(x_norm * WIDTH) - PADDLE_WIDTH // 2
        paddle_x = int(SMOOTHING * prev_paddle_x + (1 - SMOOTHING) * target_x)
        paddle_x = max(0, min(WIDTH - PADDLE_WIDTH, paddle_x))
        prev_paddle_x = paddle_x

# ------------------- MAIN GAME LOOP -------------------
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    detect_hand()

    ball_x += ball_vel_x
    ball_y += ball_vel_y

    if ball_x - BALL_RADIUS <= 0 or ball_x + BALL_RADIUS >= WIDTH:
        ball_vel_x *= -1
    if ball_y - BALL_RADIUS <= 0:
        ball_vel_y *= -1

    paddle_rect = pygame.Rect(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
    if paddle_rect.collidepoint(ball_x, ball_y + BALL_RADIUS):
        ball_vel_y *= -1

    hit_index = None
    for i, brick in enumerate(bricks):
        if brick.collidepoint(ball_x, ball_y - BALL_RADIUS) or brick.collidepoint(ball_x, ball_y + BALL_RADIUS):
            ball_vel_y *= -1
            hit_index = i
            break
        elif brick.collidepoint(ball_x - BALL_RADIUS, ball_y) or brick.collidepoint(ball_x + BALL_RADIUS, ball_y):
            ball_vel_x *= -1
            hit_index = i
            break
    if hit_index is not None:
        bricks.pop(hit_index)
        score += 10

    if ball_y - BALL_RADIUS > HEIGHT:
        lives -= 1
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2
        ball_vel_y = -BALL_SPEED
        ball_vel_x = BALL_SPEED * np.random.choice([-1, 1])
        if lives <= 0:
            print("Game Over!")
            running = False

    draw()

# ------------------- CLEANUP -------------------
cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()
