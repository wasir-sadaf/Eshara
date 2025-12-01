import cv2
import mediapipe as mp
import pygame
import numpy as np
import random

# ---------- CONFIG ----------
CELL_SIZE = 20
WIDTH, HEIGHT = 800, 600
ACCEL = 0.2
DAMPING = 0.7
FOOD_COLOR = (0, 255, 0)
SNAKE_COLOR = (237, 26, 18)
BG_COLOR = (26, 26, 26)
FRAME_SKIP = 2
# ----------------------------

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.4,
    min_tracking_confidence=0.4
)

# Webcam setup
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

# Pygame setup
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand-Controlled Snake")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Snake state
snake = [(WIDTH // 2, HEIGHT // 2)]
px, py = WIDTH // 2, HEIGHT // 2
vx, vy = 0.0, 0.0
snake_length = 1
score = 0

# Food
food_x = random.randint(0, WIDTH // CELL_SIZE - 1) * CELL_SIZE
food_y = random.randint(0, HEIGHT // CELL_SIZE - 1) * CELL_SIZE

counter = 0
running = True

while running:
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)

        counter += 1
        process_frame = (counter % FRAME_SKIP == 0)
        target_x, target_y = px, py

        if process_frame:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)
            if result.multi_hand_landmarks:
                lm = result.multi_hand_landmarks[0].landmark
                ix, iy = lm[8].x, lm[8].y
                target_x = int(ix * WIDTH)
                target_y = int(iy * HEIGHT)

        # Velocity smoothing
        vx += (target_x - px) * ACCEL
        vy += (target_y - py) * ACCEL
        vx *= DAMPING
        vy *= DAMPING
        px += vx
        py += vy

        # Move snake
        head_pos = (int(px) // CELL_SIZE * CELL_SIZE, int(py) // CELL_SIZE * CELL_SIZE)
        snake.insert(0, head_pos)
        if len(snake) > snake_length:
            snake.pop()

        head_x, head_y = snake[0]

        # Food collision: grow snake and update score, do NOT reset position
        if head_x == food_x and head_y == food_y:
            snake_length += 1
            score += 1
            food_x = random.randint(0, WIDTH // CELL_SIZE - 1) * CELL_SIZE
            food_y = random.randint(0, HEIGHT // CELL_SIZE - 1) * CELL_SIZE

        # Self-collision: reset snake but keep score
        if len(snake) > 1 and (head_x, head_y) in snake[1:]:
            print("Self-collision! Snake reset.")
            snake = [(px, py)]
            snake_length = 1

        # Boundary collision: reset snake but keep score
        if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
            print("Hit boundary! Snake reset.")
            snake = [(px, py)]
            snake_length = 1

        # Draw everything
        win.fill(BG_COLOR)
        for seg in snake:
            pygame.draw.rect(win, SNAKE_COLOR, (seg[0], seg[1], CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(win, FOOD_COLOR, (food_x, food_y, CELL_SIZE, CELL_SIZE))

        # Draw score
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        win.blit(score_text, (10, 10))

        pygame.display.update()
        clock.tick(60)

    except Exception as e:
        print("Error:", e)
        continue

cap.release()
pygame.quit()
